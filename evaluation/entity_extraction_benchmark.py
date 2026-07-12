"""Reproducible 25-document canonical entity-reference extraction benchmark.

The benchmark deliberately measures the capability that exists today: extracting explicit,
plant-canonical identifiers (equipment, procedures, deviations, failures, RCAs, coils, etc.)
from manuals, SOPs and deviation reports. Gold labels are produced independently by matching
the locked ontology's complete ID inventory against each document. Predictions come from the
runtime regex extractor below. This is not a claim about implicit/name-only NER.
"""
from __future__ import annotations

import json
import re
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES = ROOT / "ontology" / "nodes"
DOCUMENTS = ROOT / "data" / "unstructured" / "documents"
RESULTS = Path(__file__).with_name("entity_extraction_results.json")
GOLD = Path(__file__).with_name("entity_extraction_gold.json")

SAMPLE = {
    "equipment_manual": [
        "DOC1001", "DOC1004", "DOC1011", "DOC1016", "DOC1033",
        "DOC1060", "DOC1061", "DOC1062", "DOC1063",
    ],
    "sop": [
        "DOC1008", "DOC1009", "DOC1013", "DOC1025",
        "DOC1026", "DOC1027", "DOC1028", "DOC1031",
    ],
    "deviation_report": [
        "DOC1003", "DOC1010", "DOC1021", "DOC1022",
        "DOC1023", "DOC1029", "DOC1035", "DOC1037",
    ],
}

# Candidate extraction is intentionally independent of the ontology inventory.
ENTITY_ID = re.compile(
    r"(?<![A-Z0-9-])(?:EQ-[A-Z0-9-]+|PROC-\d+|DEV\d+|RCA\d+|F\d+|"
    r"C\d+|RM\d+|DOC\d+|STD-[A-Z0-9-]+|TECH-?\d+|TEST-?\d+)(?![A-Z0-9-])",
    re.IGNORECASE,
)


def ontology_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted(NODES.glob("*.json")):
        for record in json.loads(path.read_text(encoding="utf-8")):
            for key, value in record.items():
                if key.endswith("_id") and isinstance(value, str):
                    ids.add(value.upper())
                    break
    return ids


def extract_candidates(text: str) -> set[str]:
    return {m.group(0).upper() for m in ENTITY_ID.finditer(text)}


def extract(text: str, inventory: set[str]) -> set[str]:
    """Extract candidates and resolve them against the locked plant ontology."""
    return extract_candidates(text) & inventory


def scores(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positives": tp, "false_positives": fp, "false_negatives": fn,
        "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
    }


def run() -> dict:
    inventory = ontology_ids()
    gold_manifest = json.loads(GOLD.read_text(encoding="utf-8"))
    annotations = gold_manifest["documents"]
    manifest_ids = set(annotations)
    expected_ids = {doc_id for doc_ids in SAMPLE.values() for doc_id in doc_ids}
    if manifest_ids != expected_ids:
        raise ValueError(f"gold manifest/sample mismatch: missing={sorted(expected_ids-manifest_ids)} extra={sorted(manifest_ids-expected_ids)}")
    totals = Counter()
    by_type = defaultdict(Counter)
    unknown_totals = Counter()
    documents = []

    for doc_type, doc_ids in SAMPLE.items():
        for doc_id in doc_ids:
            path = DOCUMENTS / f"{doc_id}.md"
            text = path.read_text(encoding="utf-8")
            candidates = extract_candidates(text)
            annotation = annotations[doc_id]
            if annotation["document_type"] != doc_type:
                raise ValueError(f"annotation type mismatch for {doc_id}")
            gold = {value.upper() for value in annotation["accepted_canonical_ids"]}
            expected_unknown = {value.upper() for value in annotation["expected_unknown_ids"]}
            predicted = extract(text, inventory)
            predicted_unknown = candidates - inventory
            tp, fp, fn = gold & predicted, predicted - gold, gold - predicted
            unknown_tp = expected_unknown & predicted_unknown
            unknown_fp = predicted_unknown - expected_unknown
            unknown_fn = expected_unknown - predicted_unknown
            row = {
                "document_id": doc_id, "document_type": doc_type,
                "gold_count": len(gold), "predicted_count": len(predicted),
                "true_positives": sorted(tp), "false_positives": sorted(fp),
                "false_negatives": sorted(fn),
                "rejected_unknown_candidates": sorted(predicted_unknown),
                "expected_unknown_candidates": sorted(expected_unknown),
                "unknown_candidate_true_positives": sorted(unknown_tp),
                "unknown_candidate_false_positives": sorted(unknown_fp),
                "unknown_candidate_false_negatives": sorted(unknown_fn),
            }
            documents.append(row)
            counts = Counter(tp=len(tp), fp=len(fp), fn=len(fn))
            totals.update(counts)
            by_type[doc_type].update(counts)
            unknown_totals.update(tp=len(unknown_tp), fp=len(unknown_fp), fn=len(unknown_fn))

    result = {
        "benchmark": "explicit canonical entity-reference extraction",
        "scope_note": "Gold labels are locked reviewer annotations. Measures explicit canonical IDs and stale-ID rejection; does not measure implicit or name-only entity recognition.",
        "gold_annotation_file": str(GOLD.relative_to(ROOT)).replace("\\", "/"),
        "gold_annotation_sha256": hashlib.sha256(GOLD.read_bytes()).hexdigest(),
        "gold_annotation_method": gold_manifest["annotation_method"],
        "sample_size": len(documents),
        "sample_distribution": {key: len(value) for key, value in SAMPLE.items()},
        "ontology_inventory_size": len(inventory),
        "overall": scores(totals["tp"], totals["fp"], totals["fn"]),
        "unknown_candidate_rejection": scores(unknown_totals["tp"], unknown_totals["fp"], unknown_totals["fn"]),
        "by_document_type": {
            key: scores(value["tp"], value["fp"], value["fn"])
            for key, value in by_type.items()
        },
        "documents": documents,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({key: result[key] for key in (
        "benchmark", "sample_size", "sample_distribution", "ontology_inventory_size",
        "overall", "by_document_type",
    )}, indent=2))
