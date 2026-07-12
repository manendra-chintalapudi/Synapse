"""
Graph retrieval layer: Cypher queries against the Neo4j knowledge graph.

query_graph(cypher, params) -> list of dicts is the generic entry point the pipeline's
graph_retrieval_node calls. entity_neighborhood() provides the pre-built, entity-type-aware
query templates the router's plans map onto (same template pattern as the structured layer).
"""
import json
import os
from functools import lru_cache
from pathlib import Path

from neo4j import GraphDatabase

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
# accept NEO4J_USER or NEO4J_USERNAME (the latter is what AuraDB's downloaded creds file uses)
NEO4J_USER = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "synapse123")

_driver = None
ROOT = Path(__file__).resolve().parents[1]
NODE_DIR = ROOT / "ontology" / "nodes"
REL_DIR = ROOT / "ontology" / "relationships"


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver


def query_graph(cypher: str, params: dict = None) -> list:
    """Run arbitrary Cypher, return a list of plain dicts (one per record)."""
    with get_driver().session() as session:
        result = session.run(cypher, **(params or {}))
        return [record.data() for record in result]


# ---------------------------------------------------------------------------
# entity-type-aware neighborhood templates (what a routed graph plan executes)
# ---------------------------------------------------------------------------
TEMPLATES = {
    "coil": """
        MATCH (c:Coil {coil_id: $id})
        OPTIONAL MATCH (c)-[:PRODUCED_AT]->(e:Equipment)
        OPTIONAL MATCH (c)-[:MADE_FROM]->(rm:RawMaterial)
        OPTIONAL MATCH (c)-[:HAS_DEVIATION]->(d:Deviation)
        RETURN c{.coil_id, .grade, .status, .production_date, .heat_number} AS coil,
               e{.equipment_id, .name, .type, relationship:'PRODUCED_AT'} AS produced_at_equipment,
               [x IN collect(DISTINCT rm{.material_id, .type}) | x][..5] AS made_from_materials,
               [x IN collect(DISTINCT d{.deviation_id, .severity, .description}) | x][..5] AS deviations
    """,
    "equipment": """
        MATCH (e:Equipment {equipment_id: $id})
        OPTIONAL MATCH (e)-[:EXPERIENCED]->(f:Failure)
        OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
        OPTIONAL MATCH (r)-[:PERFORMED_BY]->(t:Technician)
        RETURN e{.equipment_id, .name, .type, .location, .maintenance_interval} AS equipment,
               [x IN collect(DISTINCT f{.failure_id, .failure_mode, .timestamp}) | x][..8] AS failures,
               [x IN collect(DISTINCT r{.rca_id, .rca_date, .root_cause_text, .corrective_action, .industry_reference}) | x][..8] AS rca_records,
               [x IN collect(DISTINCT t.name) | x][..8] AS rca_analysts
    """,
    "failure": """
        MATCH (e:Equipment)-[:EXPERIENCED]->(f:Failure {failure_id: $id})
        OPTIONAL MATCH (f)-[:DIAGNOSED_BY]->(r:RCA)
        OPTIONAL MATCH (r)-[:PERFORMED_BY]->(t:Technician)
        OPTIONAL MATCH (f)-[:DOCUMENTED_IN]->(d:Document)
        OPTIONAL MATCH (p:Procedure {procedure_id: r.procedure_ref})
        RETURN f{.failure_id, .failure_mode, .timestamp, .sensor_values,
                 .impacted_coil_ids, .impacted_failed_tests} AS failure,
               e{.equipment_id, .name, .type, relationship:'EXPERIENCED'} AS equipment,
               [x IN collect(DISTINCT r{.rca_id, .rca_date, .root_cause_text,
                    .corrective_action, .violated_step, .procedure_ref,
                    .industry_reference}) | x][..4] AS rca_records,
               [x IN collect(DISTINCT t{.technician_id, .name, .role, .shift}) | x][..4] AS rca_analysts,
               [x IN collect(DISTINCT p{.procedure_id, .title,
                    linkage:'RCA.procedure_ref'}) | x][..4] AS procedures,
               [x IN collect(DISTINCT d{.document_id, .title, .doc_type,
                    relationship:'DOCUMENTED_IN'}) | x][..4] AS documents
    """,
    "standard": """
        MATCH (s:Standard {standard_id: $id})
        OPTIONAL MATCH (qt:QualityTest)-[:FAILED_STANDARD]->(s)
        OPTIONAL MATCH (p:Procedure)-[:REFERENCES_STANDARD]->(s)
        RETURN s{.standard_id, .name, .clause_text} AS standard,
               count(DISTINCT qt) AS tests_that_failed_this_standard,
               [x IN collect(DISTINCT p.title) | x][..5] AS referencing_procedures
    """,
    "technician": """
        MATCH (t:Technician {technician_id: $id})
        OPTIONAL MATCH (e:Equipment)-[:MAINTAINED_BY]->(t)
        OPTIONAL MATCH (r:RCA)-[:PERFORMED_BY]->(t)
        RETURN t{.technician_id, .name, .role, .shift, .certification} AS technician,
               [x IN collect(DISTINCT e{.equipment_id, .name}) | x][..6] AS maintains_equipment,
               [x IN collect(DISTINCT r{.rca_id, .rca_date}) | x][..6] AS performed_rcas
    """,
}


def _rehydrate_industry_reference(records):
    """RCA.industry_reference is a nested object stored in Neo4j as a JSON string
    (node properties can't be maps). Parse it back to a dict so the synthesizer sees
    {source_name, source_url, summary_text} and can cite [Industry Reference: ...]."""
    for rec in records:
        for r in (rec.get("rca_records") or []):
            ref = r.get("industry_reference")
            if isinstance(ref, str):
                try:
                    r["industry_reference"] = json.loads(ref)
                except Exception:
                    pass
    return records


@lru_cache(maxsize=None)
def _node_index(name, key):
    rows = json.loads((NODE_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return {row[key]: row for row in rows}


@lru_cache(maxsize=None)
def _relationships(name):
    return json.loads((REL_DIR / f"{name}.json").read_text(encoding="utf-8"))


def _project(row, fields, relationship=None):
    if not row:
        return None
    result = {field: row.get(field) for field in fields if field in row}
    if relationship:
        result["relationship"] = relationship
    return result


def _local_neighborhood(entity_type, entity_id):
    """Read an equivalent neighborhood from the committed, audited ontology snapshot."""
    if entity_type == "failure":
        failure = _node_index("failure", "failure_id").get(entity_id)
        if not failure:
            return []
        equipment = _node_index("equipment", "equipment_id").get(failure.get("equipment_id"))
        rcas = [row for row in _node_index("rca", "rca_id").values() if row.get("failure_id") == entity_id]
        technicians = _node_index("technician", "technician_id")
        procedures = _node_index("procedure", "procedure_id")
        documents = _node_index("document", "document_id")
        documented_ids = [edge["to"]["key"] for edge in _relationships("documented_in") if edge["from"]["key"] == entity_id]
        return [{
            "failure": _project(failure, ["failure_id", "failure_mode", "timestamp", "sensor_values", "impacted_coil_ids", "impacted_failed_tests"]),
            "equipment": _project(equipment, ["equipment_id", "name", "type"], "EXPERIENCED"),
            "rca_records": [_project(row, ["rca_id", "rca_date", "root_cause_text", "corrective_action", "violated_step", "procedure_ref", "industry_reference"]) for row in rcas[:4]],
            "rca_analysts": [_project(technicians.get(row.get("analyst")), ["technician_id", "name", "role", "shift"]) for row in rcas[:4] if technicians.get(row.get("analyst"))],
            "procedures": [{**_project(procedures.get(row.get("procedure_ref")), ["procedure_id", "title"]),
                            "linkage": "RCA.procedure_ref"}
                           for row in rcas[:4] if procedures.get(row.get("procedure_ref"))],
            "documents": [_project(documents.get(doc_id), ["document_id", "title", "doc_type"], "DOCUMENTED_IN") for doc_id in documented_ids[:4] if documents.get(doc_id)],
            "_evidence_backend": "locked_ontology_snapshot",
        }]

    if entity_type == "coil":
        coil = _node_index("coil", "coil_id").get(entity_id)
        if not coil:
            return []
        equipment = _node_index("equipment", "equipment_id").get(coil.get("equipment_id"))
        materials = _node_index("raw_material", "material_id")
        deviations = [row for row in _node_index("deviation", "deviation_id").values() if row.get("coil_id_fk") == entity_id]
        return [{
            "coil": _project(coil, ["coil_id", "grade", "status", "production_date", "heat_number"]),
            "produced_at_equipment": _project(equipment, ["equipment_id", "name", "type"], "PRODUCED_AT"),
            "made_from_materials": [_project(materials.get(mid), ["material_id", "type"]) for mid in coil.get("material_ids", [])[:5] if materials.get(mid)],
            "deviations": [_project(row, ["deviation_id", "severity", "description"]) for row in deviations[:5]],
            "_evidence_backend": "locked_ontology_snapshot",
        }]

    if entity_type == "equipment":
        equipment = _node_index("equipment", "equipment_id").get(entity_id)
        if not equipment:
            return []
        failures = [row for row in _node_index("failure", "failure_id").values() if row.get("equipment_id") == entity_id]
        failure_ids = {row["failure_id"] for row in failures}
        rcas = [row for row in _node_index("rca", "rca_id").values() if row.get("failure_id") in failure_ids]
        technicians = _node_index("technician", "technician_id")
        return [{
            "equipment": _project(equipment, ["equipment_id", "name", "type", "location", "maintenance_interval"]),
            "failures": [_project(row, ["failure_id", "failure_mode", "timestamp"]) for row in failures[:8]],
            "rca_records": [_project(row, ["rca_id", "rca_date", "root_cause_text", "corrective_action", "industry_reference"]) for row in rcas[:8]],
            "rca_analysts": [technicians[row["analyst"]]["name"] for row in rcas[:8] if row.get("analyst") in technicians],
            "_evidence_backend": "locked_ontology_snapshot",
        }]

    if entity_type == "standard":
        standard = _node_index("standard", "standard_id").get(entity_id)
        if not standard:
            return []
        failed_test_ids = {edge["from"]["key"] for edge in _relationships("failed_standard") if edge["to"]["key"] == entity_id}
        procedure_ids = [edge["from"]["key"] for edge in _relationships("references_standard") if edge["to"]["key"] == entity_id]
        procedures = _node_index("procedure", "procedure_id")
        return [{
            "standard": _project(standard, ["standard_id", "name", "clause_text"]),
            "tests_that_failed_this_standard": len(failed_test_ids),
            "referencing_procedures": [procedures[pid]["title"] for pid in procedure_ids[:5] if pid in procedures],
            "_evidence_backend": "locked_ontology_snapshot",
        }]
    return []


def entity_neighborhood(entity_type: str, entity_id: str) -> list:
    """Run Neo4j first, then discloseably fall back to the locked ontology snapshot."""
    template = TEMPLATES.get(entity_type)
    if template is None:                       # e.g. doc_type entities have no graph shape
        return []
    try:
        records = _rehydrate_industry_reference(query_graph(template, {"id": entity_id}))
        if records:
            return records
    except Exception:
        pass
    return _rehydrate_industry_reference(_local_neighborhood(entity_type, entity_id))


if __name__ == "__main__":
    print(entity_neighborhood("coil", "C10234"))
