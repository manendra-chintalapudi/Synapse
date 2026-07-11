"""Audit the locked ontology for counts, endpoint integrity and schema compliance."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology"
RESULTS = Path(__file__).with_name("graph_completeness_results.json")


def run() -> dict:
    schema_nodes = json.loads((ONTOLOGY / "schema" / "node_labels.json").read_text(encoding="utf-8"))
    schema_rels = json.loads((ONTOLOGY / "schema" / "relationships.json").read_text(encoding="utf-8"))
    label_by_file = {item["label"].replace("_", "").lower(): item for item in schema_nodes["labels"]}

    node_ids: dict[str, set[str]] = {}
    duplicate_nodes = []
    node_counts = {}
    for path in sorted((ONTOLOGY / "nodes").glob("*.json")):
        definition = label_by_file[path.stem.replace("_", "").lower()]
        label, primary_key = definition["label"], definition["primary_key"]
        records = json.loads(path.read_text(encoding="utf-8"))
        ids = [str(record[primary_key]) for record in records]
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        duplicate_nodes.extend({"label": label, "key": key} for key in duplicates)
        node_ids[label] = set(ids)
        node_counts[label] = len(ids)

    allowed_pairs = {
        (rel["type"], pair["from_label"], pair["to_label"])
        for rel in schema_rels["relationships"] if rel["implementation"] == "edge"
        for pair in rel["pairs"]
    }
    broken_endpoints, invalid_schema_edges, duplicate_edges = [], [], []
    edge_counts = Counter()
    seen_edges = set()

    for path in sorted((ONTOLOGY / "relationships").glob("*.json")):
        for index, edge in enumerate(json.loads(path.read_text(encoding="utf-8"))):
            rel_type = edge["type"]
            from_label, from_key = edge["from"]["label"], str(edge["from"]["key"])
            to_label, to_key = edge["to"]["label"], str(edge["to"]["key"])
            edge_counts[rel_type] += 1
            if from_key not in node_ids.get(from_label, set()):
                broken_endpoints.append({"file": path.name, "index": index, "side": "from", "label": from_label, "key": from_key})
            if to_key not in node_ids.get(to_label, set()):
                broken_endpoints.append({"file": path.name, "index": index, "side": "to", "label": to_label, "key": to_key})
            if (rel_type, from_label, to_label) not in allowed_pairs:
                invalid_schema_edges.append({"file": path.name, "index": index, "type": rel_type, "from": from_label, "to": to_label})
            signature = (rel_type, from_label, from_key, to_label, to_key)
            if signature in seen_edges:
                duplicate_edges.append({"type": rel_type, "from": from_key, "to": to_key})
            seen_edges.add(signature)

    result = {
        "node_total": sum(node_counts.values()),
        "edge_total": sum(edge_counts.values()),
        "node_type_count": len(node_counts),
        "relationship_type_count": len(edge_counts),
        "directed_schema_link_count": len(allowed_pairs),
        "node_counts": dict(sorted(node_counts.items())),
        "relationship_counts": dict(sorted(edge_counts.items())),
        "duplicate_nodes": duplicate_nodes,
        "duplicate_edges": duplicate_edges,
        "broken_endpoints": broken_endpoints,
        "invalid_schema_edges": invalid_schema_edges,
        "passed": not any((duplicate_nodes, duplicate_edges, broken_endpoints, invalid_schema_edges)),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    summary_keys = (
        "node_total", "edge_total", "node_type_count", "relationship_type_count",
        "directed_schema_link_count", "duplicate_nodes", "duplicate_edges",
        "broken_endpoints", "invalid_schema_edges", "passed",
    )
    print(json.dumps({key: result[key] for key in summary_keys}, indent=2))
