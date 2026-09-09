"""Read-only Neo4j queries for the RCA & Failures browsing page."""
from __future__ import annotations

import json
import re
import threading
import time
from collections import Counter
from datetime import date, datetime

from confidence import calibrate_confidence
from graph_store import _local_neighborhood, _node_index, query_graph
from structured_store import query_federated

SEVERITY_RANK = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unrated": 0}
_CACHE_SECONDS = 30
_cache_lock = threading.Lock()
_cache_at = 0.0
_cache_rows: list[dict] | None = None

LIST_QUERY = """
MATCH (e:Equipment)-[:EXPERIENCED]->(f:Failure)
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
OPTIONAL MATCH (d:Deviation) WHERE d.failure_id_fk = f.failure_id
RETURN e{.equipment_id, .name, .type} AS equipment,
       f{.failure_id, .failure_mode, .timestamp} AS failure,
       r{.rca_id, .rca_date, .root_cause_text, .corrective_action, .procedure_ref} AS rca,
       [x IN collect(DISTINCT d{.deviation_id, .severity}) WHERE x.deviation_id IS NOT NULL] AS deviations
"""

DETAIL_QUERY = """
MATCH (e:Equipment)-[:EXPERIENCED]->(f:Failure {failure_id: $failure_id})
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
OPTIONAL MATCH (r)-[:PERFORMED_BY]->(t:Technician)
OPTIONAL MATCH (e)-[:FOLLOWS_PROCEDURE]->(p:Procedure)
WHERE r IS NULL OR p.procedure_id = r.procedure_ref
OPTIONAL MATCH (f)-[:DOCUMENTED_IN]->(doc:Document)
WITH e, f, r, t, p,
     [x IN collect(DISTINCT doc{.document_id, .title, .doc_type, .vector_ref})
      WHERE x.document_id IS NOT NULL] AS documents
OPTIONAL MATCH (d:Deviation) WHERE d.failure_id_fk = f.failure_id
OPTIONAL MATCH (c:Coil)-[:HAS_DEVIATION]->(d)
OPTIONAL MATCH (c)-[:TESTED_BY]->(qt:QualityTest)
OPTIONAL MATCH (qt)-[:FAILED_STANDARD]->(failed:Standard)
OPTIONAL MATCH (qt)-[:TESTED_AGAINST]->(tested:Standard)
RETURN e{.equipment_id, .name, .type, .location} AS equipment,
       f{.failure_id, .failure_mode, .timestamp, .sensor_values} AS failure,
       r{.rca_id, .rca_date, .root_cause_text, .corrective_action,
         .violated_step, .procedure_ref} AS rca,
       t{.technician_id, .name, .role, .shift, .certification} AS technician,
       p{.procedure_id, .title, .steps_text} AS procedure,
       documents,
       [x IN collect(DISTINCT d{.deviation_id, .severity, .description, .coil_id_fk})
        WHERE x.deviation_id IS NOT NULL] AS deviations,
       [x IN collect(DISTINCT c{.coil_id, .grade, .status}) WHERE x.coil_id IS NOT NULL] AS coils,
       collect(DISTINCT {
         test_id: qt.test_id,
         test_date: qt.test_date,
         fault_type: qt.fault_type,
         result: CASE WHEN qt.test_id IS NULL THEN null
                      WHEN qt.fault_type IS NULL OR toLower(qt.fault_type) IN ['none','no fault','pass'] THEN 'Pass'
                      ELSE 'Failed: ' + qt.fault_type END,
         standard_id: coalesce(failed.standard_id, tested.standard_id, qt.standard_ref),
         standard_name: coalesce(failed.name, tested.name)
       }) AS downstream_tests
"""

RECURRENCE_QUERY = """
MATCH (f:Failure {failure_id: $failure_id})-[:DIAGNOSED_BY]->(r:RCA)
MATCH (other:Failure)-[:DIAGNOSED_BY]->(otherRca:RCA)
WHERE other.failure_id <> f.failure_id
  AND ((r.root_cause_text IS NOT NULL AND
        toLower(trim(otherRca.root_cause_text)) = toLower(trim(r.root_cause_text)))
       OR
       (r.corrective_action IS NOT NULL AND
        toLower(trim(otherRca.corrective_action)) = toLower(trim(r.corrective_action))))
OPTIONAL MATCH (oe:Equipment)-[:EXPERIENCED]->(other)
RETURN other{.failure_id, .failure_mode, .timestamp} AS failure,
       oe{.equipment_id, .name} AS equipment,
       otherRca{.rca_id} AS rca
ORDER BY other.timestamp DESC
"""


def _local_failure_rows() -> list[dict]:
    """Build the RCA list from the committed ontology when Neo4j is unavailable."""
    failures = _node_index("failure", "failure_id")
    equipment = _node_index("equipment", "equipment_id")
    rcas = _node_index("rca", "rca_id").values()
    deviations = _node_index("deviation", "deviation_id").values()
    rcas_by_failure = {}
    for rca in rcas:
        rcas_by_failure.setdefault(rca.get("failure_id"), []).append(rca)
    deviations_by_failure = {}
    for deviation in deviations:
        failure_id = deviation.get("failure_id_fk")
        if failure_id:
            deviations_by_failure.setdefault(failure_id, []).append(deviation)
    rows = []
    for failure in failures.values():
        fid = failure.get("failure_id")
        eq = equipment.get(failure.get("equipment_id"), {})
        linked_rcas = rcas_by_failure.get(fid, [])
        rows.append({
            "equipment": {"equipment_id": eq.get("equipment_id"), "name": eq.get("name"), "type": eq.get("type")},
            "failure": {key: failure.get(key) for key in ("failure_id", "failure_mode", "timestamp")},
            "rca": linked_rcas[0] if linked_rcas else {},
            "deviations": [{"deviation_id": d.get("deviation_id"), "severity": d.get("severity")}
                           for d in deviations_by_failure.get(fid, [])],
        })
    return rows


def _local_failure_detail(failure_id: str) -> dict | None:
    records = _local_neighborhood("failure", failure_id)
    if not records:
        return None
    row = records[0]
    rca_records = row.get("rca_records") or []
    analysts = row.get("rca_analysts") or []
    procedures = row.get("procedures") or []
    return {
        "equipment": row.get("equipment") or {},
        "failure": row.get("failure") or {},
        "rca": rca_records[0] if rca_records else {},
        "technician": analysts[0] if analysts else {},
        "procedure": procedures[0] if procedures else {},
        "documents": row.get("documents") or [],
        "deviations": [], "coils": [], "downstream_tests": [],
        "_evidence_backend": "locked_ontology_snapshot",
    }


def _duckdb_failure_rows() -> list[dict]:
    """Read the RCA register from DuckDB, without requiring Neo4j."""
    rows = query_federated(
        """
        SELECT e.equipment_id, e.name AS equipment_name, e.type AS equipment_type,
               f.failure_id, f.failure_mode, f.timestamp,
               r.rca_id, r.rca_date, r.root_cause_text, r.corrective_action,
               r.procedure_ref, r.violated_step,
               d.deviation_id, d.severity
        FROM cmms.main.failures f
        LEFT JOIN scada.main.equipment e ON e.equipment_id = f.equipment_id
        LEFT JOIN cmms.main.rca r ON r.failure_id = f.failure_id
        LEFT JOIN qms.main.deviations d ON d.failure_id_fk = f.failure_id
        ORDER BY f.timestamp DESC
        """
    )
    grouped: dict[str, dict] = {}
    for row in rows:
        failure_id = row.get("failure_id")
        if not failure_id:
            continue
        item = grouped.setdefault(failure_id, {
            "equipment": {
                "equipment_id": row.get("equipment_id"),
                "name": row.get("equipment_name"),
                "type": row.get("equipment_type"),
            },
            "failure": {key: row.get(key) for key in ("failure_id", "failure_mode", "timestamp")},
            "rca": {key: row.get(key) for key in (
                "rca_id", "rca_date", "root_cause_text", "corrective_action", "procedure_ref", "violated_step"
            ) if row.get(key) is not None},
            "deviations": [],
        })
        if row.get("deviation_id"):
            item["deviations"].append({"deviation_id": row["deviation_id"], "severity": row.get("severity")})
    return list(grouped.values())


def _duckdb_failure_detail(failure_id: str) -> dict | None:
    """Read one RCA chain from DuckDB and return the API's existing shape."""
    rows = query_federated(
        """
        SELECT e.equipment_id, e.name AS equipment_name, e.type AS equipment_type,
               e.location, f.failure_id, f.failure_mode, f.timestamp, f.sensor_values,
               r.rca_id, r.rca_date, r.root_cause_text, r.corrective_action,
               r.violated_step, r.procedure_ref, r.analyst,
               t.technician_id, t.name AS technician_name, t.role AS technician_role,
               t.shift, t.certification,
               p.title AS procedure_title, p.steps_text AS procedure_steps,
               d.deviation_id, d.severity, d.description, d.coil_id_fk
        FROM cmms.main.failures f
        LEFT JOIN scada.main.equipment e ON e.equipment_id = f.equipment_id
        LEFT JOIN cmms.main.rca r ON r.failure_id = f.failure_id
        LEFT JOIN cmms.main.technicians t ON t.technician_id = r.analyst
        LEFT JOIN cmms.main.procedures p ON p.procedure_id = r.procedure_ref
        LEFT JOIN qms.main.deviations d ON d.failure_id_fk = f.failure_id
        WHERE f.failure_id = ?
        """.replace("?", f"'{failure_id.replace(chr(39), chr(39) * 2)}'", 1)
    )
    if not rows:
        return None
    first = rows[0]
    rca = {key: first.get(key) for key in (
        "rca_id", "rca_date", "root_cause_text", "corrective_action", "violated_step", "procedure_ref"
    ) if first.get(key) is not None}
    deviations = []
    seen = set()
    for row in rows:
        if row.get("deviation_id") and row["deviation_id"] not in seen:
            seen.add(row["deviation_id"])
            deviations.append({key: row.get(key) for key in ("deviation_id", "severity", "description", "coil_id_fk")})
    technician = {key: first.get(source) for key, source in {
        "technician_id": "technician_id", "name": "technician_name", "role": "technician_role", "shift": "shift", "certification": "certification"
    }.items() if first.get(source) is not None}
    procedure = {key: first.get(source) for key, source in {
        "procedure_id": "procedure_ref", "title": "procedure_title", "steps_text": "procedure_steps"
    }.items() if first.get(source) is not None}
    return {
        "equipment": {key: first.get(source) for key, source in {
            "equipment_id": "equipment_id", "name": "equipment_name", "type": "equipment_type", "location": "location"
        }.items() if first.get(source) is not None},
        "failure": {key: first.get(key) for key in ("failure_id", "failure_mode", "timestamp", "sensor_values")},
        "rca": rca,
        "technician": technician,
        "procedure": procedure,
        "documents": [], "deviations": deviations, "coils": [], "downstream_tests": [],
        "_evidence_backend": "duckdb",
    }


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


def _date_only(value) -> str:
    text = str(_plain(value) or "")
    return text[:10]


def _normalise(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _severity(deviations: list[dict]) -> str:
    levels = [str(row.get("severity") or "").lower() for row in deviations]
    levels = [level for level in levels if level in SEVERITY_RANK]
    return max(levels, key=SEVERITY_RANK.get) if levels else "unrated"


def _load_failures(force: bool = False) -> list[dict]:
    global _cache_at, _cache_rows
    now = time.monotonic()
    with _cache_lock:
        if not force and _cache_rows is not None and now - _cache_at < _CACHE_SECONDS:
            return [dict(row) for row in _cache_rows]
    try:
        raw = [_plain(row) for row in _duckdb_failure_rows()]
        snapshot_fallback = False
    except Exception:
        try:
            raw = [_plain(row) for row in query_graph(LIST_QUERY)]
            snapshot_fallback = False
        except Exception:
            raw = _local_failure_rows()
            snapshot_fallback = True
    cause_counts = Counter(
        _normalise((row.get("rca") or {}).get("root_cause_text"))
        for row in raw if (row.get("rca") or {}).get("root_cause_text")
    )
    rows = []
    for record in raw:
        equipment, failure, rca = record.get("equipment") or {}, record.get("failure") or {}, record.get("rca") or {}
        deviations = record.get("deviations") or []
        cause = _normalise(rca.get("root_cause_text"))
        recurrence_count = cause_counts.get(cause, 0) if cause else 0
        has_rca = bool(rca.get("rca_id"))
        rows.append({
            "failure_id": failure.get("failure_id"),
            "equipment_id": equipment.get("equipment_id"),
            "equipment_name": equipment.get("name") or equipment.get("equipment_id"),
            "equipment_type": equipment.get("type") or "Unknown",
            "failure_date": _date_only(failure.get("timestamp")),
            "failure_timestamp": str(_plain(failure.get("timestamp")) or ""),
            "failure_mode": failure.get("failure_mode") or "unknown",
            "severity": _severity(deviations),
            "severity_source": "linked_deviation" if deviations else "unrated_no_linked_deviation",
            "status": "open" if not has_rca else "recurring" if recurrence_count > 1 else "resolved",
            "has_rca": has_rca,
            "rca_id": rca.get("rca_id"),
            "recurrence_count": recurrence_count,
            "evidence_backend": "locked_ontology_snapshot" if snapshot_fallback else "DuckDB",
        })
    with _cache_lock:
        _cache_rows, _cache_at = rows, time.monotonic()
    return [dict(row) for row in rows]


def get_summary() -> dict:
    rows = _load_failures()
    with_rca = sum(1 for row in rows if row["has_rca"])
    modes = Counter(row["failure_mode"] for row in rows)
    equipment = Counter((row["equipment_id"], row["equipment_name"]) for row in rows)
    common_mode, common_mode_count = modes.most_common(1)[0] if modes else ("—", 0)
    common_equipment, common_equipment_count = equipment.most_common(1)[0] if equipment else (("—", "—"), 0)
    dates = sorted(row["failure_date"] for row in rows if row["failure_date"])
    return {
        "total_failures": len(rows),
        "failures_with_rca": with_rca,
        "rca_completion_pct": round(with_rca * 100 / len(rows), 1) if rows else 0,
        "most_common_failure_mode": {"name": common_mode, "count": common_mode_count},
        "most_affected_equipment": {
            "equipment_id": common_equipment[0], "name": common_equipment[1], "count": common_equipment_count,
        },
        "filters": {
            "equipment_types": sorted({row["equipment_type"] for row in rows}),
            "severities": [level for level in ("critical", "high", "medium", "low", "unrated") if any(row["severity"] == level for row in rows)],
            "date_min": dates[0] if dates else None,
            "date_max": dates[-1] if dates else None,
        },
        "procedure_link_note": "RCA procedure_ref is resolved through Equipment-[:FOLLOWS_PROCEDURE]->Procedure.",
    }


def get_failures(
    *, equipment_type: str | None = None, date_from: str | None = None,
    date_to: str | None = None, severity: str | None = None,
    has_rca: bool | None = None, sort: str = "recent",
) -> dict:
    rows = _load_failures()
    if equipment_type:
        rows = [row for row in rows if row["equipment_type"] == equipment_type]
    if date_from:
        rows = [row for row in rows if row["failure_date"] >= date_from]
    if date_to:
        rows = [row for row in rows if row["failure_date"] <= date_to]
    if severity:
        rows = [row for row in rows if row["severity"] == severity.lower()]
    if has_rca is not None:
        rows = [row for row in rows if row["has_rca"] is has_rca]
    if sort == "severe":
        rows.sort(key=lambda row: (SEVERITY_RANK.get(row["severity"], 0), row["failure_timestamp"]), reverse=True)
    elif sort == "recurring":
        rows.sort(key=lambda row: (row["recurrence_count"], row["failure_timestamp"]), reverse=True)
    else:
        rows.sort(key=lambda row: row["failure_timestamp"], reverse=True)
    return {"count": len(rows), "failures": rows}


def _actions(rca: dict, recurrence_count: int, downstream_count: int) -> list[dict]:
    actions = []
    if rca.get("corrective_action"):
        actions.append({"role": "Maintenance", "text": f"Verify corrective work and closure evidence: {rca['corrective_action']}"})
    if rca.get("violated_step"):
        actions.append({"role": "Maintenance", "text": f"Close and document the procedure gap: {rca['violated_step']}"})
    if recurrence_count:
        actions.append({"role": "Reliability", "text": f"Compare this event with {recurrence_count} matching prior failure(s) before closure."})
    if downstream_count:
        actions.append({"role": "QA", "text": f"Review {downstream_count} linked downstream quality result(s) before releasing affected material."})
    return actions


def get_failure_detail(failure_id: str) -> dict | None:
    try:
        duckdb_detail = _duckdb_failure_detail(failure_id)
    except Exception:
        duckdb_detail = None
    if duckdb_detail is not None:
        row = duckdb_detail
        rca = row.get("rca") or {}
        recurrences = []
        row["provenance"] = {
            "query_mode": "duckdb",
            "procedure_path": "Failure -> DuckDB cmms.rca -> cmms.procedures",
            "llm_used": False,
        }
        row["evidence_chain"] = [
            {"kind": "Failure", "id": (row.get("failure") or {}).get("failure_id"), "label": (row.get("failure") or {}).get("failure_mode"), "record": row.get("failure"), "citation": "DuckDB"},
            {"kind": "RCA", "id": rca.get("rca_id"), "label": "Root cause analysis", "record": rca, "citation": "DuckDB"},
        ]
        row["recurrences"] = recurrences
        row["recurrence_count"] = 0
        row["confidence"] = calibrate_confidence(direct_chain=bool(rca.get("rca_id")), corroborating_sources=sum(bool(row.get(key)) for key in ("technician", "procedure", "deviations")), sample_size=1)
        row["severity"] = _severity(row.get("deviations") or [])
        row["status"] = "resolved" if rca.get("rca_id") else "open"
        row["recommended_actions"] = _actions(rca, 0, 0)
        return row
    try:
        rows = [_plain(row) for row in query_graph(DETAIL_QUERY, {"failure_id": failure_id})]
    except Exception:
        rows = []
    if not rows:
        local = _local_failure_detail(failure_id)
        if local is None:
            return None
        local["provenance"] = {
            "query_mode": "locked_ontology_snapshot_fallback",
            "procedure_path": "Failure <-[:EXPERIENCED]- Equipment -[:FOLLOWS_PROCEDURE]-> Procedure",
            "llm_used": False,
        }
        local["evidence_chain"] = [
            {"kind": "Failure", "id": (local.get("failure") or {}).get("failure_id"),
             "label": (local.get("failure") or {}).get("failure_mode"), "record": local.get("failure"), "citation": "Graph"},
            {"kind": "RCA", "id": (local.get("rca") or {}).get("rca_id"),
             "label": "Root cause analysis", "record": local.get("rca"), "citation": "Graph"},
        ]
        local["recurrences"] = []
        local["recurrence_count"] = 0
        local["confidence"] = calibrate_confidence(
            direct_chain=bool((local.get("rca") or {}).get("rca_id")), corroborating_sources=0, sample_size=1
        )
        local["severity"] = "unrated"
        local["status"] = "resolved" if (local.get("rca") or {}).get("rca_id") else "open"
        local["recommended_actions"] = _actions(local.get("rca") or {}, 0, 0)
        return local
    row = rows[0]
    failure, equipment = row.get("failure") or {}, row.get("equipment") or {}
    rca, technician, procedure = row.get("rca") or {}, row.get("technician") or {}, row.get("procedure") or {}
    deviations = [item for item in row.get("deviations") or [] if item.get("deviation_id")]
    documents = [item for item in row.get("documents") or [] if item.get("document_id")]
    tests_by_id = {}
    for item in row.get("downstream_tests") or []:
        if item.get("test_id"):
            tests_by_id.setdefault(item["test_id"], item)
    downstream_tests = list(tests_by_id.values())
    recurrences = [_plain(item) for item in query_graph(RECURRENCE_QUERY, {"failure_id": failure_id})]
    recurrences = [{**(item.get("failure") or {}), "equipment": item.get("equipment") or {}, "rca": item.get("rca") or {}} for item in recurrences]
    corroborating = sum(bool(value) for value in (technician, procedure, documents, deviations, downstream_tests))
    confidence = calibrate_confidence(
        direct_chain=bool(rca.get("rca_id")),
        corroborating_sources=corroborating,
        sample_size=max(1, len(recurrences) + 1),
    )
    severity = _severity(deviations)
    status = "open" if not rca.get("rca_id") else "recurring" if recurrences else "resolved"
    standards = []
    seen_standards = set()
    for item in downstream_tests:
        sid = item.get("standard_id")
        if sid and sid not in seen_standards:
            standards.append({"standard_id": sid, "name": item.get("standard_name")})
            seen_standards.add(sid)
    steps = [
        {"kind": "Failure", "id": failure.get("failure_id"), "label": failure.get("failure_mode"), "record": failure, "citation": "Graph"},
        {"kind": "RCA", "id": rca.get("rca_id"), "label": "Root cause analysis", "record": rca, "citation": "Graph"},
        {"kind": "Technician", "id": technician.get("technician_id"), "label": technician.get("name"), "record": technician, "citation": "Graph"},
        {"kind": "Procedure", "id": procedure.get("procedure_id"), "label": procedure.get("title"), "record": procedure, "citation": "Graph"},
        {"kind": "Deviation", "id": deviations[0].get("deviation_id") if deviations else None, "label": f"{len(deviations)} linked", "record": deviations, "citation": "Graph"},
        {"kind": "Standard", "id": standards[0].get("standard_id") if standards else None, "label": f"{len(standards)} linked", "record": standards, "citation": "Graph"},
        {"kind": "Document", "id": documents[0].get("document_id") if documents else None, "label": f"{len(documents)} linked", "record": documents, "citation": "RAG"},
    ]
    return {
        "failure": failure,
        "equipment": equipment,
        "rca": rca,
        "technician": technician,
        "procedure": procedure,
        "deviations": deviations,
        "coils": row.get("coils") or [],
        "documents": documents,
        "downstream_tests": downstream_tests,
        "standards": standards,
        "recurrences": recurrences,
        "recurrence_count": len(recurrences),
        "confidence": confidence,
        "severity": severity,
        "status": status,
        "evidence_chain": steps,
        "recommended_actions": _actions(rca, len(recurrences), len(downstream_tests)),
        "provenance": {
            "query_mode": "direct_read_only_cypher",
            "procedure_path": "Failure <-[:EXPERIENCED]- Equipment -[:FOLLOWS_PROCEDURE]-> Procedure, selected by RCA.procedure_ref",
            "llm_used": False,
        },
    }
