"""
Graph retrieval layer: Cypher queries against the Neo4j knowledge graph.

query_graph(cypher, params) -> list of dicts is the generic entry point the pipeline's
graph_retrieval_node calls. entity_neighborhood() provides the pre-built, entity-type-aware
query templates the router's plans map onto (same template pattern as the structured layer).
"""
import json
import os

from neo4j import GraphDatabase

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
# accept NEO4J_USER or NEO4J_USERNAME (the latter is what AuraDB's downloaded creds file uses)
NEO4J_USER = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "synapse123")

_driver = None


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


def entity_neighborhood(entity_type: str, entity_id: str) -> list:
    """Run the type-appropriate neighborhood template for one matched entity."""
    template = TEMPLATES.get(entity_type)
    if template is None:                       # e.g. doc_type entities have no graph shape
        return []
    return _rehydrate_industry_reference(query_graph(template, {"id": entity_id}))


if __name__ == "__main__":
    print(entity_neighborhood("coil", "C10234"))
