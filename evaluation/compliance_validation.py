"""Validate the highest-deviation compliance family against independent Cypher."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "retrieval", ROOT / "synthesizer"):
    sys.path.insert(0, str(path))

from api.compliance_store import get_standard_detail  # noqa: E402
from graph_store import query_graph  # noqa: E402

RESULTS = Path(__file__).with_name("compliance_validation_results.json")
FAMILY_ID = "is-1786"
REPRESENTATIVE_IDS = ["DEV1174", "DEV1020", "DEV1050"]

MANUAL_QUERY = """
MATCH (s:Standard)<-[:FAILED_STANDARD]-(:QualityTest)<-[:TESTED_BY]-(c:Coil)-[hd:HAS_DEVIATION]->(d:Deviation)
WHERE s.standard_id STARTS WITH 'STD-IS1786-'
WITH DISTINCT d, hd.date_flagged AS dateFlagged
OPTIONAL MATCH (f:Failure {failure_id: d.failure_id_fk})
OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
WITH d, f, r,
     CASE WHEN f IS NULL THEN null
          ELSE duration.inDays(
                 date(substring(toString(dateFlagged), 0, 10)),
                 date(substring(toString(f.timestamp), 0, 10))
               ).days END AS delta
RETURN count(*) AS deviationCohort,
       sum(CASE WHEN f IS NOT NULL THEN 1 ELSE 0 END) AS failureLinked,
       sum(CASE WHEN r IS NOT NULL THEN 1 ELSE 0 END) AS rcaLinked,
       sum(CASE WHEN delta >= 0 AND delta <= 30 THEN 1 ELSE 0 END) AS downstream30d
"""

CAUSE_QUERY = """
MATCH (s:Standard)<-[:FAILED_STANDARD]-(:QualityTest)<-[:TESTED_BY]-(c:Coil)-[hd:HAS_DEVIATION]->(d:Deviation)
WHERE s.standard_id STARTS WITH 'STD-IS1786-'
WITH DISTINCT d, hd.date_flagged AS dateFlagged
MATCH (f:Failure {failure_id: d.failure_id_fk})-[:DIAGNOSED_BY]->(r:RCA)
WITH r, duration.inDays(
       date(substring(toString(dateFlagged), 0, 10)),
       date(substring(toString(f.timestamp), 0, 10))
     ).days AS delta
WHERE delta >= 0 AND delta <= 30
RETURN r.root_cause_text AS rootCause, count(*) AS count
ORDER BY count DESC, rootCause
LIMIT 1
"""

CHAIN_QUERY = """
UNWIND $ids AS id
MATCH (c:Coil)-[hd:HAS_DEVIATION]->(d:Deviation {deviation_id: id})
MATCH (c)-[:PRODUCED_AT]->(e:Equipment)
MATCH (e)-[:EXPERIENCED]->(f:Failure {failure_id: d.failure_id_fk})
MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)-[:PERFORMED_BY]->(t:Technician)
MATCH (c)-[:TESTED_BY]->(qt:QualityTest)-[:FAILED_STANDARD]->(s:Standard)
WHERE s.standard_id STARTS WITH 'STD-IS1786-'
RETURN id, hd.date_flagged AS dateFlagged, c.coil_id AS coilId,
       e.equipment_id AS equipmentId, f.failure_id AS failureId,
       r.rca_id AS rcaId, t.technician_id AS technicianId,
       collect(DISTINCT [qt.test_id, s.standard_id]) AS failedTests
ORDER BY id
"""


def plain(value):
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [plain(item) for item in value]
    if isinstance(value, (date, datetime)) or hasattr(value, "iso_format"):
        try:
            return value.isoformat()
        except AttributeError:
            return value.iso_format()
    return value


def run() -> dict:
    detail = get_standard_detail(FAMILY_ID)
    manual = plain(query_graph(MANUAL_QUERY)[0])
    top_cause = plain(query_graph(CAUSE_QUERY)[0])
    chains = [plain(row) for row in query_graph(CHAIN_QUERY, {"ids": REPRESENTATIVE_IDS})]
    pattern = detail["pattern"]
    projected_chains = {
        (row.get("deviation") or {}).get("deviation_id"): {
            "coilId": (row.get("coil") or {}).get("coil_id"),
            "equipmentId": (row.get("equipment") or {}).get("equipment_id"),
            "failureId": (row.get("failure") or {}).get("failure_id"),
            "rcaId": (row.get("rca") or {}).get("rca_id"),
            "technicianId": (row.get("technician") or {}).get("technician_id"),
        }
        for row in detail["deviations"]
        if (row.get("deviation") or {}).get("deviation_id") in REPRESENTATIVE_IDS
    }
    chain_matches = all(
        projected_chains.get(row["id"]) == {
            "coilId": row["coilId"], "equipmentId": row["equipmentId"],
            "failureId": row["failureId"], "rcaId": row["rcaId"],
            "technicianId": row["technicianId"],
        }
        for row in chains
    )
    frontend = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "frontend" / "chat.html",
            ROOT / "frontend" / "ui" / "src" / "ComplianceApp.tsx",
            ROOT / "frontend" / "ui" / "src" / "main.tsx",
        )
    )
    navigation_contract = all(token in frontend for token in (
        'window.SynapsePillars?.openFailure(failureId)',
        'function openFailure(failureId: string)',
        '#/rca/${encodeURIComponent(failureId)}',
        'id="rca-react-root"',
    ))
    passed = (
        manual["deviationCohort"] == pattern["deviation_cohort_n"] == 338
        and manual["failureLinked"] == pattern["failure_linked_n"] == 171
        and manual["rcaLinked"] == 171
        and manual["downstream30d"] == pattern["downstream_failure_n"] == 15
        and top_cause["count"] == pattern["most_common_root_cause_n"] == 8
        and len(chains) == len(REPRESENTATIVE_IDS)
        and chain_matches and navigation_contract
    )
    result = {
        "benchmark": "Compliance UI projection vs independent Cypher",
        "family_id": FAMILY_ID,
        "passed": passed,
        "manual_pattern": manual,
        "detail_pattern": pattern,
        "manual_top_cause": top_cause,
        "representative_chains": chains,
        "chain_projection_matches": chain_matches,
        "cross_pillar_navigation_contract": navigation_contract,
        "scope_note": "Navigation validation checks the rendered click contract; live authenticated browser validation remains a separate deployment check.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
