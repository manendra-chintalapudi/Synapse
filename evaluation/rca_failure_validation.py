"""Validate RCA detail projections against an independent direct-Cypher query."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RESULTS = Path(__file__).with_name("rca_failure_validation_results.json")

DIRECT_QUERY = """
MATCH (e:Equipment)-[:EXPERIENCED]->(f:Failure {failure_id: $failure_id})
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
OPTIONAL MATCH (r)-[:PERFORMED_BY]->(t:Technician)
OPTIONAL MATCH (e)-[:FOLLOWS_PROCEDURE]->(p:Procedure)
WHERE r IS NULL OR p.procedure_id = r.procedure_ref
OPTIONAL MATCH (f)-[:DOCUMENTED_IN]->(doc:Document)
OPTIONAL MATCH (d:Deviation) WHERE d.failure_id_fk = f.failure_id
OPTIONAL MATCH (c:Coil)-[:HAS_DEVIATION]->(d)
OPTIONAL MATCH (c)-[:TESTED_BY]->(qt:QualityTest)
OPTIONAL MATCH (qt)-[:TESTED_AGAINST]->(tested:Standard)
OPTIONAL MATCH (qt)-[:FAILED_STANDARD]->(failed:Standard)
RETURN f.failure_id AS failure_id, e.equipment_id AS equipment_id,
       r.rca_id AS rca_id, t.technician_id AS technician_id,
       p.procedure_id AS procedure_id,
       count(DISTINCT d) AS deviation_count,
       count(DISTINCT qt) AS test_count,
       count(DISTINCT doc) AS document_count,
       collect(DISTINCT tested.standard_id) + collect(DISTINCT failed.standard_id) AS standard_ids
"""


def run(failure_ids: list[str]) -> dict:
    for path in (ROOT, ROOT / "retrieval", ROOT / "synthesizer"):
        sys.path.insert(0, str(path))
    from api.rca_store import get_failure_detail
    from graph_store import query_graph

    cases = []
    for failure_id in failure_ids:
        detail = get_failure_detail(failure_id)
        direct = query_graph(DIRECT_QUERY, {"failure_id": failure_id})[0]
        direct_standard_count = len({sid for sid in direct["standard_ids"] if sid})
        observed = {
            "failure_id": detail["failure"].get("failure_id"),
            "equipment_id": detail["equipment"].get("equipment_id"),
            "rca_id": detail["rca"].get("rca_id"),
            "technician_id": detail["technician"].get("technician_id"),
            "procedure_id": detail["procedure"].get("procedure_id"),
            "deviation_count": len(detail["deviations"]),
            "test_count": len(detail["downstream_tests"]),
            "document_count": len(detail["documents"]),
            "standard_count": len(detail["standards"]),
        }
        expected = {
            "failure_id": direct["failure_id"],
            "equipment_id": direct["equipment_id"],
            "rca_id": direct["rca_id"],
            "technician_id": direct["technician_id"],
            "procedure_id": direct["procedure_id"],
            "deviation_count": direct["deviation_count"],
            "test_count": direct["test_count"],
            "document_count": direct["document_count"],
            "standard_count": direct_standard_count,
        }
        checks = {key: observed[key] == expected[key] for key in expected}
        cases.append({
            "failure_id": failure_id,
            "expected_direct_cypher": expected,
            "observed_detail_projection": observed,
            "checks": checks,
            "passed": all(checks.values()),
        })
    result = {
        "benchmark": "RCA detail versus independent direct Cypher",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_size": len(cases),
        "failure_ids": failure_ids,
        "cases": cases,
        "passed": all(case["passed"] for case in cases),
        "scope_note": "Validates IDs and chain cardinalities only; browser click-through is verified separately.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", help="Optional dotenv credential file; omitted in configured environments")
    parser.add_argument("--failure-id", action="append", dest="failure_ids")
    args = parser.parse_args()
    load_dotenv(args.credentials, override=True)
    result = run(args.failure_ids or ["F1114", "F1019", "F1186"])
    print(json.dumps({
        "sample_size": result["sample_size"],
        "failure_ids": result["failure_ids"],
        "passed": result["passed"],
    }, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
