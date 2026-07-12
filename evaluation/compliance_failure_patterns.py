"""Measure compliance-deviation timing against linked equipment failures.

This produces descriptive detection metrics with denominators and Wilson confidence intervals.
It does not claim detection *accuracy* until an independent expert-labelled event sample exists.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = ROOT / "ontology" / "nodes"
RELS = ROOT / "ontology" / "relationships"
RESULTS = Path(__file__).with_name("compliance_failure_results.json")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def wilson(successes: int, total: int, z: float = 1.96) -> list[float]:
    if not total:
        return [0.0, 0.0]
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [round(max(0, centre - spread), 4), round(min(1, centre + spread), 4)]


def run(window_days: int = 30) -> dict:
    deviations = {row["deviation_id"]: row for row in load(NODES / "deviation.json")}
    failures = {row["failure_id"]: row for row in load(NODES / "failure.json")}

    coil_tests = defaultdict(set)
    for edge in load(RELS / "tested_by.json"):
        coil_tests[edge["from"]["key"]].add(edge["to"]["key"])
    failed_standard = {
        edge["from"]["key"]: edge["to"]["key"]
        for edge in load(RELS / "failed_standard.json")
    }

    by_standard = defaultdict(dict)
    for edge in load(RELS / "has_deviation.json"):
        if edge["from"]["label"] != "Coil":
            continue
        deviation_id, coil_id = edge["to"]["key"], edge["from"]["key"]
        standards = {
            failed_standard[test_id] for test_id in coil_tests[coil_id]
            if test_id in failed_standard
        }
        for standard_id in standards:
            by_standard[standard_id][deviation_id] = edge["properties"]["date_flagged"]

    grouped = defaultdict(set)
    for standard_id in by_standard:
        if "IS1786" in standard_id:
            grouped["IS:1786"].add(standard_id)
        elif "IS2062" in standard_id:
            grouped["IS:2062"].add(standard_id)
        elif "ASTMA370" in standard_id:
            grouped["ASTM A370"].add(standard_id)

    patterns = {}
    evidence = {}
    for family, standard_ids in grouped.items():
        cohort = {}
        for standard_id in sorted(standard_ids):
            cohort.update(by_standard[standard_id])
        linked, preceded, followed = [], [], []
        for deviation_id, flagged in sorted(cohort.items()):
            failure_id = deviations[deviation_id].get("failure_id_fk")
            if not failure_id or failure_id not in failures:
                continue
            delta_days = (
                datetime.fromisoformat(failures[failure_id]["timestamp"]).date()
                - date.fromisoformat(flagged)
            ).days
            row = {"deviation_id": deviation_id, "failure_id": failure_id, "delta_days": delta_days}
            linked.append(row)
            if 0 <= delta_days <= window_days:
                preceded.append(row)
            if -window_days <= delta_days < 0:
                followed.append(row)

        n = len(linked)
        patterns[family] = {
            "deviation_cohort_n": len(cohort),
            "failure_linked_n": n,
            "preceded_failure_within_30d_n": len(preceded),
            "preceded_failure_rate_among_linked": round(len(preceded) / n, 4) if n else 0,
            "preceded_failure_rate_95pct_wilson": wilson(len(preceded), n),
            "followed_failure_within_30d_n": len(followed),
            "failure_preceded_deviation_rate_among_linked": round(len(followed) / n, 4) if n else 0,
            "failure_preceded_deviation_rate_95pct_wilson": wilson(len(followed), n),
            "confidence": "high" if n >= 100 else "medium" if n >= 30 else "low",
        }
        evidence[family] = {"preceded_examples": preceded[:10], "followed_examples": followed[:10]}

    result = {
        "benchmark": "compliance deviation to equipment failure timing",
        "window_days": window_days,
        "patterns": patterns,
        "evidence_examples": evidence,
        "accuracy_validation": {
            "status": "pending independent expert-labelled event sample",
            "claim_allowed": False,
        },
        "scope_note": (
            "Cohorts are deviations on coils with tests linked to the named failed-standard family. "
            "Timing uses date_flagged and the explicitly enriched failure_id_fk. Rates are descriptive, not causal."
        ),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
