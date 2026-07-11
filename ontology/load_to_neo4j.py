"""
Loads the Synapse knowledge graph into Neo4j from ontology/nodes/*.json and
ontology/relationships/*.json, using ontology/schema/node_labels.json for
primary-key lookups.

Expected input formats
-----------------------
ontology/nodes/<Label>.json
    A JSON list of records for one node label, e.g. ontology/nodes/Coil.json:
    [
      {"coil_id": "COIL-000001", "grade": "Fe500", "thickness_mm": 3.2, ...},
      ...
    ]
    The filename stem (case-insensitive) must match a label name in
    schema/node_labels.json.

ontology/relationships/*.json
    A JSON list of edge records, e.g. ontology/relationships/produced_at.json:
    [
      {
        "type": "PRODUCED_AT",
        "from": {"label": "Coil", "key": "COIL-000001"},
        "to": {"label": "Equipment", "key": "EQ-0001"},
        "properties": {"date": "2024-01-01"}
      },
      ...
    ]
    "from"/"to" identify the target node by label + primary-key value (the
    primary-key *property name* for that label is looked up from
    schema/node_labels.json, not stored in the edge record itself).

Environment variables
----------------------
NEO4J_URI       default: bolt://localhost:7687
NEO4J_USER      default: neo4j
NEO4J_PASSWORD  default: neo4j
"""

import json
import logging
import os
from pathlib import Path

from neo4j import GraphDatabase

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("load_to_neo4j")

ONTOLOGY_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = ONTOLOGY_DIR / "schema"
NODES_DIR = ONTOLOGY_DIR / "nodes"
RELATIONSHIPS_DIR = ONTOLOGY_DIR / "relationships"

NODE_LOAD_ORDER = [
    "Standard",
    "RawMaterial",
    "Equipment",
    "Technician",
    "Procedure",
    "Coil",
    "QualityTest",
    "Deviation",
    "Failure",
    "RCA",
    "Document",
]


def create_constraints(driver, pk_by_label):
    """Create a uniqueness constraint on each label's primary key BEFORE the node MERGE step.
    Uses IF NOT EXISTS so it is idempotent. Creating the constraint also fails fast if the
    graph already contains duplicate primary keys, so this doubles as a data-integrity gate."""
    created = []
    with driver.session() as session:
        for label in NODE_LOAD_ORDER:
            pk = pk_by_label[label]
            name = f"uniq_{label}_{pk}"
            session.run(
                f"CREATE CONSTRAINT {name} IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.{pk} IS UNIQUE"
            )
            created.append((label, pk, name))
            log.info("Constraint ensured: %s  (%s.%s IS UNIQUE)", name, label, pk)
    log.info("Created/ensured %d uniqueness constraints", len(created))
    return created


def load_node_schema():
    """Returns {label: primary_key_property_name} from schema/node_labels.json."""
    with open(SCHEMA_DIR / "node_labels.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    return {entry["label"]: entry["primary_key"] for entry in schema["labels"]}


def _norm(name):
    """Normalize a label or filename stem for matching: lowercase, drop non-alphanumerics.
    So label 'RawMaterial' matches file 'raw_material.json', 'QualityTest' matches
    'quality_test.json', etc."""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def find_node_file(label):
    """Finds ontology/nodes/<label>.json, tolerating snake_case vs CamelCase. None if absent."""
    if not NODES_DIR.exists():
        return None
    target = _norm(label)
    for path in NODES_DIR.glob("*.json"):
        if _norm(path.stem) == target:
            return path
    return None


def neo4j_props(record):
    """Neo4j node/relationship properties must be primitives or arrays of primitives.
    Nested objects (dicts) and non-primitive lists (e.g. composition, feature_values,
    sensor_values, key_specifications) are serialized to JSON-string properties -- the
    'JSON blob' representation the schema documents. Lists of primitives (e.g. material_ids,
    typical_failure_modes) are left as native Neo4j arrays."""
    def scalar(v):
        return v is None or isinstance(v, (str, int, float, bool))

    out = {}
    for k, v in record.items():
        if isinstance(v, dict):
            out[k] = json.dumps(v)
        elif isinstance(v, list) and not all(scalar(x) for x in v):
            out[k] = json.dumps(v)
        else:
            out[k] = v
    return out


def upsert_node(session, label, pk_prop, record, counts):
    pk_value = record.get(pk_prop)
    if pk_value is None:
        log.warning("Skipping %s record with missing primary key '%s': %s", label, pk_prop, record)
        counts[label]["skipped"] += 1
        return

    query = f"""
        MERGE (n:{label} {{{pk_prop}: $pk_value}})
        SET n += $properties
    """
    try:
        session.run(query, pk_value=pk_value, properties=neo4j_props(record))
        counts[label]["upserted"] += 1
    except Exception as exc:
        log.error("Failed to upsert %s[%s=%s]: %s", label, pk_prop, pk_value, exc)
        counts[label]["skipped"] += 1


def load_all_nodes(driver, pk_by_label):
    counts = {label: {"upserted": 0, "skipped": 0} for label in NODE_LOAD_ORDER}

    with driver.session() as session:
        for label in NODE_LOAD_ORDER:
            path = find_node_file(label)
            if path is None:
                log.info("No node file found for label '%s' (expected nodes/%s.json), skipping.", label, label)
                continue

            with open(path, "r", encoding="utf-8") as f:
                records = json.load(f)

            pk_prop = pk_by_label[label]
            for record in records:
                upsert_node(session, label, pk_prop, record, counts)

            log.info(
                "%-12s: %d upserted, %d skipped (from %s)",
                label, counts[label]["upserted"], counts[label]["skipped"], path.name,
            )

    return counts


def upsert_relationship(session, rel_type, from_label, from_pk_prop, from_key,
                         to_label, to_pk_prop, to_key, properties, counts):
    query = f"""
        MATCH (a:{from_label} {{{from_pk_prop}: $from_key}})
        MATCH (b:{to_label} {{{to_pk_prop}: $to_key}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $properties
        RETURN count(r) AS created
    """
    try:
        result = session.run(query, from_key=from_key, to_key=to_key, properties=neo4j_props(properties or {}))
        record = result.single()
        created = record["created"] if record else 0
    except Exception as exc:
        log.error(
            "Failed to upsert relationship %s (%s:%s=%s -> %s:%s=%s): %s",
            rel_type, from_label, from_pk_prop, from_key, to_label, to_pk_prop, to_key, exc,
        )
        counts[rel_type]["skipped"] += 1
        return

    if created:
        counts[rel_type]["upserted"] += created
    else:
        log.warning(
            "Skipping %s: could not find %s{%s=%s} and/or %s{%s=%s} "
            "(FK target not loaded yet)",
            rel_type, from_label, from_pk_prop, from_key, to_label, to_pk_prop, to_key,
        )
        counts[rel_type]["skipped"] += 1


def load_all_relationships(driver, pk_by_label):
    counts = {}

    if not RELATIONSHIPS_DIR.exists():
        log.info("No relationships directory found, skipping relationship load.")
        return counts

    rel_files = sorted(RELATIONSHIPS_DIR.glob("*.json"))
    if not rel_files:
        log.info("No relationship files found in %s, nothing to load.", RELATIONSHIPS_DIR)
        return counts

    with driver.session() as session:
        for path in rel_files:
            with open(path, "r", encoding="utf-8") as f:
                edges = json.load(f)

            for edge in edges:
                rel_type = edge.get("type")
                from_ref = edge.get("from", {})
                to_ref = edge.get("to", {})
                properties = edge.get("properties", {})

                from_label = from_ref.get("label")
                to_label = to_ref.get("label")
                from_key = from_ref.get("key")
                to_key = to_ref.get("key")

                if not all([rel_type, from_label, to_label, from_key is not None, to_key is not None]):
                    log.warning("Skipping malformed edge record in %s: %s", path.name, edge)
                    continue

                if from_label not in pk_by_label or to_label not in pk_by_label:
                    log.warning(
                        "Skipping edge with unknown label(s) %s -> %s in %s",
                        from_label, to_label, path.name,
                    )
                    continue

                counts.setdefault(rel_type, {"upserted": 0, "skipped": 0})

                upsert_relationship(
                    session,
                    rel_type,
                    from_label, pk_by_label[from_label], from_key,
                    to_label, pk_by_label[to_label], to_key,
                    properties,
                    counts,
                )

            log.info("Processed relationship file %s", path.name)

    return counts


def print_summary(node_counts, rel_counts):
    print("\n" + "=" * 60)
    print("LOAD SUMMARY")
    print("=" * 60)
    print("\nNodes:")
    for label in NODE_LOAD_ORDER:
        c = node_counts.get(label, {"upserted": 0, "skipped": 0})
        print(f"  {label:<12} upserted={c['upserted']:<6} skipped={c['skipped']}")

    print("\nRelationships:")
    if not rel_counts:
        print("  (none loaded)")
    else:
        for rel_type, c in sorted(rel_counts.items()):
            print(f"  {rel_type:<20} upserted={c['upserted']:<6} skipped={c['skipped']}")
    print()


def main():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "neo4j")

    pk_by_label = load_node_schema()

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        log.info("Connected to Neo4j at %s", uri)

        create_constraints(driver, pk_by_label)
        node_counts = load_all_nodes(driver, pk_by_label)
        rel_counts = load_all_relationships(driver, pk_by_label)

        print_summary(node_counts, rel_counts)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
