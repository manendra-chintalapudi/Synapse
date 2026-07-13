"""Compare the deployed Neo4j graph with the locked local ontology audit."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
LOCKED_RESULTS = Path(__file__).with_name("graph_completeness_results.json")
RESULTS = Path(__file__).with_name("live_graph_parity_results.json")

ID_KEYS = {
    "Coil": "coil_id",
    "Deviation": "deviation_id",
    "Document": "document_id",
    "Equipment": "equipment_id",
    "Failure": "failure_id",
    "Procedure": "procedure_id",
    "QualityTest": "test_id",
    "RCA": "rca_id",
    "RawMaterial": "material_id",
    "Standard": "standard_id",
    "Technician": "technician_id",
}


def run() -> dict:
    locked = json.loads(LOCKED_RESULTS.read_text(encoding="utf-8"))
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
    password = os.environ.get("NEO4J_PASSWORD")
    if not uri or not password:
        raise RuntimeError("NEO4J_URI and NEO4J_PASSWORD are required")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=os.environ.get("NEO4J_DATABASE", "neo4j")) as session:
        totals = dict(session.run(
            "MATCH (n) WITH count(n) AS nodes MATCH ()-[r]->() RETURN nodes, count(r) AS relationships"
        ).single())
        live_node_counts = {
            row["label"]: row["count"]
            for row in session.run(
                "MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS count ORDER BY label"
            )
        }
        live_relationship_counts = {
            row["type"]: row["count"]
            for row in session.run(
                "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY type"
            )
        }
        id_integrity = {}
        for label, key in ID_KEYS.items():
            query = (
                f"MATCH (n:`{label}`) WITH n[$key] AS entityId, count(*) AS copies "
                "RETURN sum(CASE WHEN entityId IS NULL THEN copies ELSE 0 END) AS nullIds, "
                "sum(CASE WHEN entityId IS NOT NULL AND copies > 1 THEN copies - 1 ELSE 0 END) AS duplicateIds"
            )
            row = dict(session.run(query, key=key).single())
            id_integrity[label] = {
                "id_key": key,
                "null_ids": row.get("nullIds") or 0,
                "duplicate_ids": row.get("duplicateIds") or 0,
            }
    driver.close()

    checks = {
        "node_total": totals["nodes"] == locked["node_total"],
        "relationship_total": totals["relationships"] == locked["edge_total"],
        "node_counts": live_node_counts == locked["node_counts"],
        "relationship_counts": live_relationship_counts == locked["relationship_counts"],
        "id_integrity": all(
            row["null_ids"] == 0 and row["duplicate_ids"] == 0
            for row in id_integrity.values()
        ),
    }
    result = {
        "benchmark": "live Neo4j parity with locked ontology",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": all(checks.values()),
        "checks": checks,
        "live": {
            "node_total": totals["nodes"],
            "relationship_total": totals["relationships"],
            "node_counts": live_node_counts,
            "relationship_counts": live_relationship_counts,
            "id_integrity": id_integrity,
        },
        "locked": {
            "node_total": locked["node_total"],
            "relationship_total": locked["edge_total"],
            "node_counts": locked["node_counts"],
            "relationship_counts": locked["relationship_counts"],
        },
        "scope_note": "Compares deployed totals, per-label/per-relationship counts and primary-ID uniqueness with the committed locked ontology; semantic property equality is outside this audit.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", help="Optional dotenv credential file; omitted in configured environments")
    args = parser.parse_args()
    load_dotenv(args.credentials, override=True)
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
