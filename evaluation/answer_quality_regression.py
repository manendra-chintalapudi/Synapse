"""Offline deterministic answer-quality regression over locked evidence records.

This verifies content and the four-layer answer contract without claiming public-service
availability, latency, or domain-expert validation.
"""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "evaluation", ROOT / "retrieval", ROOT / "synthesizer"):
    sys.path.insert(0, str(path))

try:
    import requests  # noqa: F401
except ModuleNotFoundError:
    sys.modules["requests"] = types.ModuleType("requests")
try:
    import neo4j  # noqa: F401
except ModuleNotFoundError:
    module = types.ModuleType("neo4j")
    module.GraphDatabase = object
    sys.modules["neo4j"] = module

from answer_quality_benchmark import CASES, score
from graph_store import _local_neighborhood
from synthesize import _deterministic_evidence_answer, extract_sources

RESULTS = Path(__file__).with_name("answer_quality_regression_results.json")


def run() -> dict:
    evidence = {
        "rhf_cooling_circuit_rca": (
            _local_neighborhood("failure", "F1186"),
            [{"document_id": "DOC1242", "text": (ROOT / "data/unstructured/documents/DOC1242.md").read_text(encoding="utf-8")}],
            {},
        ),
        "coil_equipment_lineage": (_local_neighborhood("coil", "C10234"), [], {}),
        "is2062_scope_and_action": (
            [],
            [{"document_id": "DOC1058", "text": (ROOT / "data/unstructured/standards/is_2062.md").read_text(encoding="utf-8")}],
            {},
        ),
        "failed_coil_count": ([], [], {"qms+erp (federated)": [
            {"metric": "coils_with_at_least_one_failed_test", "value": 324},
            {"metric": "total_coils", "value": 400},
            {"metric": "total_quality_tests", "value": 1941},
        ]}),
        "equipment_failure_rank": ([], [], {"cmms+scada (equipment failures this quarter)": [
            {"equipment_id": "EQ-CR-01", "equipment_name": "Overhead Crane (Rolling Mill Bay) #1", "failure_count": 1},
        ]}),
        "coating_fault_standard": ([], [], {"qms (coating-fault standards)": [
            {"standard_ref": "STD-IS1786-01", "associated_test_count": 15, "associated_coil_count": 15},
            {"standard_ref": "STD-IS1786-04", "associated_test_count": 15, "associated_coil_count": 14},
        ]}),
        "quality_deviation_rate": ([], [], {"qms (test deviation rate)": [
            {"total_tests": 1941, "failed_tests": 644, "deviation_rate_pct": 33.18},
        ]}),
        "document_inventory": ([], [], {"document inventory": [
            {"metric": "total_documents", "value": 255},
            {"metric": "doc_type:work_order", "value": 188},
            {"metric": "doc_type:deviation_report", "value": 15},
            {"metric": "doc_type:equipment_manual", "value": 13},
        ]}),
    }
    rows = []
    for case in CASES:
        graph, documents, structured = evidence[case["id"]]
        answer = _deterministic_evidence_answer(case["question"], graph, documents, structured)
        response = {"answer": answer, "sources": extract_sources(answer), "model_used": "deterministic/evidence-template", "retrieval_errors": {}}
        rows.append({
            **case,
            "response": response,
            "automated_score": score(case, response),
            "expert_review": {"status": "pending", "factual_correctness_1_to_5": None, "operational_usefulness_1_to_5": None, "notes": None},
        })
    result = {
        "benchmark": "offline deterministic answer-quality regression",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(rows),
        "automated_mean_pass_rate": round(sum(row["automated_score"]["automated_pass_rate"] for row in rows) / len(rows), 3),
        "expert_validation_complete": False,
        "execution_scope": "Locked ontology/document evidence; not a public endpoint or latency test.",
        "scope_note": "Automated rubric results are not a substitute for domain-expert scoring.",
        "cases": rows,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({"benchmark": result["benchmark"], "case_count": result["case_count"], "automated_mean_pass_rate": result["automated_mean_pass_rate"], "expert_validation_complete": result["expert_validation_complete"]}, indent=2))
