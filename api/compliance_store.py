"""Read-only Neo4j compliance queries and deterministic pattern projections."""
from __future__ import annotations

import math
import threading
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

from graph_store import query_graph


WINDOW_DAYS = 30
CACHE_SECONDS = 30
ACTIVE_PREFIXES = ("STD-IS1786", "STD-ASTMA370", "STD-IS2062")
FAMILIES = {
    "is-1786": {
        "prefix": "STD-IS1786",
        "name": "BIS IS:1786",
        "scope": "High-strength deformed steel bars and wires for concrete reinforcement.",
    },
    "astm-a370": {
        "prefix": "STD-ASTMA370",
        "name": "ASTM A370",
        "scope": "Mechanical testing methods for steel products, including tension, bend, hardness and impact.",
    },
    "is-2062": {
        "prefix": "STD-IS2062",
        "name": "BIS IS:2062",
        "scope": "Hot-rolled medium and high-tensile structural steel for general structural use.",
    },
}

TEST_QUERY = """
MATCH (qt:QualityTest)-[outcome:TESTED_AGAINST|FAILED_STANDARD]->(s:Standard)
WHERE any(prefix IN $prefixes WHERE s.standard_id STARTS WITH prefix)
RETURN qt{.test_id, .test_date, .fault_type, .standard_ref} AS test,
       s{.standard_id, .name, .clause_text} AS standard,
       type(outcome) AS outcome
"""

DEVIATION_QUERY = """
MATCH (c:Coil)-[hd:HAS_DEVIATION]->(d:Deviation)
MATCH (c)-[:TESTED_BY]->(:QualityTest)-[:FAILED_STANDARD]->(s:Standard)
WHERE any(prefix IN $prefixes WHERE s.standard_id STARTS WITH prefix)
WITH c, d, hd, collect(DISTINCT s.standard_id) AS standard_ids
OPTIONAL MATCH (c)-[:PRODUCED_AT]->(e:Equipment)
OPTIONAL MATCH (e)-[:EXPERIENCED]->(f:Failure)
WHERE d.failure_id_fk = f.failure_id
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
OPTIONAL MATCH (r)-[:PERFORMED_BY]->(t:Technician)
OPTIONAL MATCH (c)-[:MADE_FROM]->(rm:RawMaterial)
RETURN d{.deviation_id, .description, .severity, .coil_id_fk, .equipment_id_fk, .failure_id_fk} AS deviation,
       hd.date_flagged AS date_flagged,
       c{.coil_id, .grade, .heat_number, .production_date, .status} AS coil,
       e{.equipment_id, .name, .type, .location} AS equipment,
       f{.failure_id, .failure_mode, .timestamp} AS failure,
       r{.rca_id, .rca_date, .root_cause_text, .corrective_action, .procedure_ref} AS rca,
       t{.technician_id, .name, .role, .shift} AS technician,
       standard_ids,
       [x IN collect(DISTINCT rm{.material_id, .type, .supplier_id})
        WHERE x.material_id IS NOT NULL] AS materials
"""

OVERALL_QUERY = """
MATCH (source)-[hd:HAS_DEVIATION]->(d:Deviation)
OPTIONAL MATCH (source:Coil)-[:PRODUCED_AT]->(coilEquipment:Equipment)
WITH source, hd, d,
     CASE WHEN source:Equipment THEN source ELSE coilEquipment END AS equipment
OPTIONAL MATCH (equipment)-[:EXPERIENCED]->(f:Failure)
WHERE d.failure_id_fk = f.failure_id
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
WITH d, hd, f, r,
     CASE WHEN f IS NULL THEN null
          ELSE duration.inDays(
                 date(substring(toString(hd.date_flagged), 0, 10)),
                 date(substring(toString(f.timestamp), 0, 10))
               ).days END AS delta,
     CASE WHEN source:Coil THEN 'Coil' ELSE 'Equipment' END AS source_type
WITH count(DISTINCT d) AS total_deviations,
     count(DISTINCT CASE WHEN source_type = 'Coil' THEN d END) AS coil_sourced,
     count(DISTINCT CASE WHEN source_type = 'Equipment' THEN d END) AS equipment_sourced,
     count(DISTINCT CASE WHEN f IS NOT NULL THEN d END) AS linked_failures,
     count(DISTINCT CASE WHEN r IS NOT NULL THEN d END) AS linked_rcas,
     count(DISTINCT CASE WHEN delta >= 0 AND delta <= $window_days THEN d END) AS downstream_failures
MATCH (s:Standard)
RETURN total_deviations, coil_sourced, equipment_sourced, linked_failures,
       linked_rcas, downstream_failures, count(s) AS total_standard_nodes
"""

_lock = threading.Lock()
_cache_at = 0.0
_cache_payload: tuple[list[dict], list[dict], dict] | None = None


def _plain(value):
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, (date, datetime)) or hasattr(value, "iso_format"):
        try:
            return value.isoformat()
        except AttributeError:
            return value.iso_format()
    return value


def _date(value) -> date | None:
    text = str(_plain(value) or "")[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _family_id(standard_id: str | None) -> str | None:
    for family_id, definition in FAMILIES.items():
        if str(standard_id or "").startswith(definition["prefix"]):
            return family_id
    return None


def _load(force: bool = False) -> tuple[list[dict], list[dict], dict]:
    global _cache_at, _cache_payload
    now = time.monotonic()
    with _lock:
        if not force and _cache_payload is not None and now - _cache_at < CACHE_SECONDS:
            tests, deviations, overall = _cache_payload
            return list(tests), list(deviations), dict(overall)
    params = {"prefixes": list(ACTIVE_PREFIXES)}
    tests = [_plain(row) for row in query_graph(TEST_QUERY, params)]
    deviations = [_plain(row) for row in query_graph(DEVIATION_QUERY, params)]
    overall_rows = [_plain(row) for row in query_graph(OVERALL_QUERY, {"window_days": WINDOW_DAYS})]
    overall = overall_rows[0] if overall_rows else {}
    with _lock:
        _cache_payload = tests, deviations, overall
        _cache_at = time.monotonic()
    return list(tests), list(deviations), dict(overall)


def _family_tests(rows: list[dict], family_id: str) -> list[dict]:
    return [row for row in rows if _family_id((row.get("standard") or {}).get("standard_id")) == family_id]


def _family_deviations(rows: list[dict], family_id: str) -> list[dict]:
    prefix = FAMILIES[family_id]["prefix"]
    return [row for row in rows if any(str(value).startswith(prefix) for value in row.get("standard_ids") or [])]


def _trend(rows: list[dict]) -> dict:
    dated = [(row, _date((row.get("test") or {}).get("test_date"))) for row in rows]
    dated = [(row, when) for row, when in dated if when]
    if not dated:
        return {"monthly": [], "recent_rate_pct": 0, "prior_rate_pct": 0, "change_pp": 0}
    max_date = max(when for _, when in dated)
    recent_start, prior_start = max_date - timedelta(days=89), max_date - timedelta(days=179)

    def rate(items):
        return 100 * sum(row.get("outcome") == "FAILED_STANDARD" for row, _ in items) / len(items) if items else 0

    recent = [(row, when) for row, when in dated if recent_start <= when <= max_date]
    prior = [(row, when) for row, when in dated if prior_start <= when < recent_start]
    monthly: dict[str, list[dict]] = defaultdict(list)
    for row, when in dated:
        monthly[when.strftime("%Y-%m")].append(row)
    points = []
    for month, month_rows in sorted(monthly.items())[-12:]:
        failed = sum(row.get("outcome") == "FAILED_STANDARD" for row in month_rows)
        points.append({"month": month, "total": len(month_rows), "failed": failed, "failure_rate_pct": round(100 * failed / len(month_rows), 2)})
    recent_rate, prior_rate = rate(recent), rate(prior)
    return {
        "monthly": points,
        "recent_rate_pct": round(recent_rate, 2),
        "prior_rate_pct": round(prior_rate, 2),
        "change_pp": round(recent_rate - prior_rate, 2),
        "recent_n": len(recent),
        "prior_n": len(prior),
        "max_test_date": max_date.isoformat(),
    }


def _wilson(successes: int, total: int, z: float = 1.96) -> list[float]:
    if not total:
        return [0.0, 0.0]
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(100 * max(0, centre - spread), 2), round(100 * min(1, centre + spread), 2)]


def _deviation_projection(row: dict) -> dict:
    flagged, failed = _date(row.get("date_flagged")), _date((row.get("failure") or {}).get("timestamp"))
    delta = (failed - flagged).days if flagged and failed else None
    return {
        "deviation": row.get("deviation") or {},
        "date_flagged": flagged.isoformat() if flagged else None,
        "coil": row.get("coil") or {},
        "equipment": row.get("equipment") or {},
        "failure": row.get("failure") or {},
        "rca": row.get("rca") or {},
        "technician": row.get("technician") or {},
        "materials": row.get("materials") or [],
        "delta_days": delta,
        "downstream_within_window": delta is not None and 0 <= delta <= WINDOW_DAYS,
    }


def _clause_stats(test_rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in test_rows:
        grouped[(row.get("standard") or {}).get("standard_id")].append(row)
    clauses = []
    for standard_id, rows in grouped.items():
        failed = sum(row.get("outcome") == "FAILED_STANDARD" for row in rows)
        trend = _trend(rows)
        standard = rows[0].get("standard") or {}
        clauses.append({
            "standard_id": standard_id,
            "name": standard.get("name"),
            "clause_text": standard.get("clause_text"),
            "total_tests": len(rows),
            "pass_count": len(rows) - failed,
            "fail_count": failed,
            "failure_rate_pct": round(100 * failed / len(rows), 2) if rows else 0,
            "trend": trend,
            "rising": trend["change_pp"] > 2 and trend.get("recent_n", 0) >= 10 and trend.get("prior_n", 0) >= 10,
        })
    return sorted(clauses, key=lambda row: row["failure_rate_pct"], reverse=True)


def _standard_row(family_id: str, tests: list[dict], deviations: list[dict]) -> dict:
    family_tests = _family_tests(tests, family_id)
    family_deviations = _family_deviations(deviations, family_id)
    failed = sum(row.get("outcome") == "FAILED_STANDARD" for row in family_tests)
    clauses = _clause_stats(family_tests)
    trend = _trend(family_tests)
    rising = [row for row in clauses if row["rising"]]
    missing_action = sum(
        bool((row.get("failure") or {}).get("failure_id")) and not (row.get("rca") or {}).get("corrective_action")
        for row in family_deviations
    )
    risk = {
        "warning": bool(rising or missing_action),
        "rising_clause_count": len(rising),
        "missing_corrective_action_count": missing_action,
        "label": f"{len(rising)} clause{'s' if len(rising) != 1 else ''} rising" if rising else "Stable trend",
        "followthrough_observable": False,
    }
    definition = FAMILIES[family_id]
    return {
        "family_id": family_id,
        "name": definition["name"],
        "scope": definition["scope"],
        "clause_count": len(clauses),
        "total_tests": len(family_tests),
        "pass_count": len(family_tests) - failed,
        "fail_count": failed,
        "failure_rate_pct": round(100 * failed / len(family_tests), 2) if family_tests else 0,
        "deviation_count": len(family_deviations),
        "trend": trend,
        "risk": risk,
    }


def get_summary() -> dict:
    tests, deviations, overall = _load()
    standards = [_standard_row(family_id, tests, deviations) for family_id in FAMILIES]
    standards.sort(key=lambda row: row["failure_rate_pct"], reverse=True)
    failed = sum(row.get("outcome") == "FAILED_STANDARD" for row in tests)
    total_deviations = int(overall.get("total_deviations") or 0)
    linked = int(overall.get("linked_failures") or 0)
    downstream = int(overall.get("downstream_failures") or 0)
    return {
        "window_days": WINDOW_DAYS,
        "total_standard_nodes": int(overall.get("total_standard_nodes") or 0),
        "active_standard_families": len(FAMILIES),
        "active_clause_count": len({(row.get("standard") or {}).get("standard_id") for row in tests}),
        "total_tests": len(tests),
        "failed_tests": failed,
        "passed_tests": len(tests) - failed,
        "overall_deviation_rate_pct": round(100 * failed / len(tests), 2) if tests else 0,
        "total_deviations": total_deviations,
        "coil_sourced_deviations": int(overall.get("coil_sourced") or 0),
        "equipment_sourced_deviations": int(overall.get("equipment_sourced") or 0),
        "failure_linked_deviations": linked,
        "rca_linked_deviations": int(overall.get("linked_rcas") or 0),
        "downstream_failure_count": downstream,
        "downstream_failure_pct_linked": round(100 * downstream / linked, 2) if linked else 0,
        "downstream_failure_pct_all": round(100 * downstream / total_deviations, 2) if total_deviations else 0,
        "headline": {
            "value_pct": round(100 * downstream / linked, 2) if linked else 0,
            "numerator": downstream,
            "denominator": linked,
            "label": f"failure-linked deviations followed by equipment failure within {WINDOW_DAYS} days",
        },
        "standards": standards,
        "provenance": {
            "query_mode": "direct_read_only_cypher",
            "llm_used": False,
            "scope": "Temporal linkage is descriptive and does not assert that a deviation caused a failure.",
        },
    }


def _groups(rows: list[dict], key_fn, label_fn) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[key_fn(row)].append(row)
    return [
        {
            "key": key,
            "label": label_fn(key, items),
            "count": len(items),
            "linked_failures": sum(bool((item.get("failure") or {}).get("failure_id")) for item in items),
            "downstream_within_window": sum(bool(item.get("downstream_within_window")) for item in items),
            "deviation_ids": [(item.get("deviation") or {}).get("deviation_id") for item in items],
        }
        for key, items in sorted(grouped.items(), key=lambda pair: pair[0], reverse=True)
    ]


def _cross_flags(rows: list[dict]) -> list[dict]:
    linked = [row for row in rows if (row.get("failure") or {}).get("failure_id")]
    shifts = Counter((row.get("technician") or {}).get("shift") for row in linked if (row.get("technician") or {}).get("shift"))
    technicians = Counter(
        ((row.get("technician") or {}).get("technician_id"), (row.get("technician") or {}).get("name"))
        for row in linked if (row.get("technician") or {}).get("technician_id")
    )
    heats = Counter((row.get("coil") or {}).get("heat_number") for row in rows if (row.get("coil") or {}).get("heat_number"))
    suppliers = Counter()
    for row in rows:
        suppliers.update({material.get("supplier_id") for material in row.get("materials") or [] if material.get("supplier_id")})

    def flag(dimension, value, count, sample, note):
        share = round(100 * count / sample, 1) if sample else 0
        return {"dimension": dimension, "value": value, "count": count, "sample_size": sample, "share_pct": share, "confidence": "low" if sample < 8 else "medium", "note": note}

    flags = []
    if shifts:
        value, count = shifts.most_common(1)[0]
        flags.append(flag("Assigned RCA technician shift", f"Shift {value}", count, sum(shifts.values()), "This is the RCA technician's assigned shift, not the incident shift."))
    if technicians:
        (technician_id, name), count = technicians.most_common(1)[0]
        flags.append(flag("RCA technician", f"{name} ({technician_id})", count, sum(technicians.values()), "Descriptive authorship concentration; it does not imply technician causation."))
    if heats:
        value, count = heats.most_common(1)[0]
        share = 100 * count / sum(heats.values())
        note = "No meaningful heat concentration is present." if share < 10 else "This heat appears repeatedly and warrants a material review."
        flags.append(flag("Material heat", value, count, sum(heats.values()), note))
    if suppliers:
        value, count = suppliers.most_common(1)[0]
        flags.append(flag("Raw-material supplier", value, count, sum(suppliers.values()), "Multiple raw materials may contribute to one coil; treat this as a screening signal."))
    return flags


def get_standard_detail(family_id: str) -> dict | None:
    if family_id not in FAMILIES:
        return None
    tests, deviations, _ = _load()
    family_tests = _family_tests(tests, family_id)
    raw_deviations = _family_deviations(deviations, family_id)
    rows = [_deviation_projection(row) for row in raw_deviations]
    rows.sort(key=lambda row: row.get("date_flagged") or "", reverse=True)
    standard = _standard_row(family_id, tests, deviations)
    linked = [row for row in rows if (row.get("failure") or {}).get("failure_id")]
    downstream = [row for row in linked if row.get("downstream_within_window")]
    causes = Counter((row.get("rca") or {}).get("root_cause_text") for row in downstream if (row.get("rca") or {}).get("root_cause_text"))
    common_cause, common_count = causes.most_common(1)[0] if causes else (None, 0)
    confidence = "high" if len(linked) >= 100 else "medium" if len(linked) >= 30 else "low"
    pattern = {
        "window_days": WINDOW_DAYS,
        "deviation_cohort_n": len(rows),
        "failure_linked_n": len(linked),
        "downstream_failure_n": len(downstream),
        "downstream_rate_among_linked_pct": round(100 * len(downstream) / len(linked), 2) if linked else 0,
        "downstream_rate_full_cohort_pct": round(100 * len(downstream) / len(rows), 2) if rows else 0,
        "wilson_95pct": _wilson(len(downstream), len(linked)),
        "most_common_root_cause": common_cause,
        "most_common_root_cause_n": common_count,
        "confidence": confidence,
        "scope": "The date test is directional (deviation first, failure 0–30 days later) and descriptive, not causal.",
    }
    by_month = _groups(rows, lambda row: (row.get("date_flagged") or "Unknown")[:7], lambda key, _: key)
    by_equipment = _groups(
        rows,
        lambda row: (row.get("equipment") or {}).get("equipment_id") or "Unlinked",
        lambda key, items: f"{(items[0].get('equipment') or {}).get('name') or key} · {key}",
    )
    return {
        "standard": standard,
        "clauses": _clause_stats(family_tests),
        "deviations": rows,
        "deviation_groups": {"month": by_month, "equipment": by_equipment},
        "pattern": pattern,
        "cross_dimensional_flags": _cross_flags(rows),
        "provenance": {
            "query_mode": "direct_read_only_cypher",
            "llm_used": False,
            "failure_link": "Deviation.failure_id_fk → Failure, verified through the same Equipment's EXPERIENCED relationship",
            "standard_link": "Standard ← FAILED_STANDARD ← QualityTest ← TESTED_BY ← Coil → HAS_DEVIATION → Deviation",
            "followthrough_gap": "Corrective-action completion/status is not modeled; only recorded corrective-action text is available.",
        },
    }
