"""Deterministic runtime regression for explicit canonical-ID Tier-1 matching.

This is deliberately separate from the 25-document extraction benchmark.  It exercises the
production ``build_entity_index`` + ``match_entities`` path and proves that each of the eleven
locked ontology entity types accepts a real ID (including lower-case input) while a valid-shaped
but absent ID is observed by the shared candidate parser and rejected by ontology resolution.

No database, network, LLM, randomness, or clock is used, so repeated runs over the same checkout
produce byte-identical JSON.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "router"
RESULTS = Path(__file__).with_name("canonical_id_runtime_results.json")

if str(ROUTER) not in sys.path:
    sys.path.insert(0, str(ROUTER))

from canonical_ids import extract_id_candidates  # noqa: E402
from entity_index import build_entity_index  # noqa: E402
from tier1_matcher import match_entities  # noqa: E402


# These are the eleven labels in ontology/schema/node_labels.json, expressed using the runtime
# entity-type vocabulary.  doc_type is routing vocabulary and intentionally is not an ontology
# entity type.
ONTOLOGY_TYPES = (
    "coil",
    "equipment",
    "failure",
    "rca",
    "procedure",
    "technician",
    "quality_test",
    "standard",
    "deviation",
    "raw_material",
    "document",
)

# Each stale fixture has the right lexical shape for its type but is absent from the locked
# ontology.  The test verifies both properties before asking the production matcher to reject it.
STALE_IDS = {
    "coil": "C999999",
    "equipment": "EQ-ZZZ-99",
    "failure": "F999999",
    "rca": "RCA999999",
    "procedure": "PROC-999999",
    "technician": "T999999",
    "quality_test": "QT999999",
    "standard": "STD-NOTREAL-99",
    "deviation": "DEV999999",
    "raw_material": "RM999999",
    "document": "DOC999999",
}

SOURCE_FILES = (
    "router/canonical_ids.py",
    "router/entity_index.py",
    "router/tier1_matcher.py",
    "ontology/schema/node_labels.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _combined_sha256(paths: list[Path]) -> str:
    """Hash both relative names and bytes so the locked inventory is reproducibly identified."""
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _pairs(hits: list[dict]) -> list[list[str]]:
    """Stable JSON representation of runtime entity hits."""
    return sorted([[hit["entity_type"], hit["entity_id"]] for hit in hits])


def run() -> dict:
    index = build_entity_index()
    failures: list[str] = []

    actual_types = set(index) - {"doc_type"}
    expected_types = set(ONTOLOGY_TYPES)
    if actual_types != expected_types:
        failures.append(
            "runtime index type mismatch: "
            f"missing={sorted(expected_types - actual_types)} "
            f"extra={sorted(actual_types - expected_types)}"
        )

    selected_ids: dict[str, str] = {}
    inventory_counts: dict[str, int] = {}
    valid_cases = []
    stale_cases = []

    for entity_type in ONTOLOGY_TYPES:
        items = index.get(entity_type, [])
        inventory = sorted({str(item["id"]).upper() for item in items})
        inventory_counts[entity_type] = len(inventory)
        if not inventory:
            failures.append(f"{entity_type}: runtime inventory is empty")
            continue

        fixture_id = inventory[0]
        selected_ids[entity_type] = fixture_id
        expected = [[entity_type, fixture_id]]

        upper_query = f"Lookup {fixture_id}."
        upper_hits = _pairs(match_entities(upper_query, index))
        upper_pass = upper_hits == expected
        if not upper_pass:
            failures.append(
                f"{entity_type}: uppercase runtime match expected {expected}, got {upper_hits}"
            )

        lower_surface = fixture_id.lower()
        lower_query = f"Lookup {lower_surface}."
        lower_hits = _pairs(match_entities(lower_query, index))
        lower_pass = lower_hits == expected
        if not lower_pass:
            failures.append(
                f"{entity_type}: lowercase runtime match expected {expected}, got {lower_hits}"
            )

        valid_cases.append({
            "entity_type": entity_type,
            "fixture_id": fixture_id,
            "uppercase_input": {
                "surface": fixture_id,
                "predicted": upper_hits,
                "passed": upper_pass,
            },
            "lowercase_input": {
                "surface": lower_surface,
                "predicted": lower_hits,
                "passed": lower_pass,
            },
        })

        stale_id = STALE_IDS[entity_type]
        candidate_pairs = sorted([
            [candidate["entity_type"], candidate["entity_id"]]
            for candidate in extract_id_candidates(stale_id)
        ])
        expected_candidate = [[entity_type, stale_id]]
        shape_recognized = candidate_pairs == expected_candidate
        absent_from_inventory = stale_id not in inventory
        stale_hits = _pairs(match_entities(f"Lookup {stale_id}.", index))
        rejected = stale_hits == []
        stale_pass = shape_recognized and absent_from_inventory and rejected
        if not stale_pass:
            failures.append(
                f"{entity_type}: stale fixture failure "
                f"shape_recognized={shape_recognized} "
                f"absent_from_inventory={absent_from_inventory} hits={stale_hits}"
            )
        stale_cases.append({
            "entity_type": entity_type,
            "stale_id": stale_id,
            "candidate_parser_output": candidate_pairs,
            "absent_from_inventory": absent_from_inventory,
            "runtime_predictions": stale_hits,
            "passed": stale_pass,
        })

    expected_combined = sorted([[key, value] for key, value in selected_ids.items()])
    valid_combined_query = "Lookup " + ", ".join(
        selected_ids[entity_type] for entity_type in ONTOLOGY_TYPES if entity_type in selected_ids
    ) + "."
    valid_combined_hits = _pairs(match_entities(valid_combined_query, index))
    valid_combined_pass = valid_combined_hits == expected_combined
    if not valid_combined_pass:
        failures.append(
            f"combined valid-ID runtime match expected {expected_combined}, got {valid_combined_hits}"
        )

    stale_combined_query = "Lookup " + ", ".join(
        STALE_IDS[entity_type] for entity_type in ONTOLOGY_TYPES
    ) + "."
    stale_combined_hits = _pairs(match_entities(stale_combined_query, index))
    stale_combined_pass = stale_combined_hits == []
    if not stale_combined_pass:
        failures.append(f"combined stale-ID query produced runtime hits: {stale_combined_hits}")

    result = {
        "benchmark": "production Tier-1 canonical-ID runtime regression",
        "scope_note": (
            "Exercises explicit canonical IDs through the production entity index and Tier-1 "
            "matcher. It is not a document-extraction accuracy, alias/name-recognition, implicit "
            "NER, retrieval, or answer-quality metric."
        ),
        "deterministic": True,
        "production_path": [
            "router/canonical_ids.py:extract_id_candidates",
            "router/entity_index.py:build_entity_index",
            "router/tier1_matcher.py:match_entities",
        ],
        "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_FILES},
        "ontology_nodes_sha256": _combined_sha256(
            list((ROOT / "ontology" / "nodes").glob("*.json"))
        ),
        "ontology_type_count": len(ONTOLOGY_TYPES),
        "ontology_types": list(ONTOLOGY_TYPES),
        "runtime_index_types": sorted(actual_types),
        "inventory_counts": inventory_counts,
        "fixture_selection": "lexicographically first canonical ID in each runtime inventory",
        "selected_valid_ids": selected_ids,
        "selected_stale_ids": STALE_IDS,
        "summary": {
            "index_type_contract_passed": actual_types == expected_types,
            "valid_type_cases_passed": sum(case["uppercase_input"]["passed"] for case in valid_cases),
            "valid_type_case_count": len(ONTOLOGY_TYPES),
            "lowercase_type_cases_passed": sum(case["lowercase_input"]["passed"] for case in valid_cases),
            "lowercase_type_case_count": len(ONTOLOGY_TYPES),
            "stale_type_cases_passed": sum(case["passed"] for case in stale_cases),
            "stale_type_case_count": len(ONTOLOGY_TYPES),
            "combined_valid_query_passed": valid_combined_pass,
            "combined_stale_query_passed": stale_combined_pass,
        },
        "combined_valid_case": {
            "expected": expected_combined,
            "predicted": valid_combined_hits,
            "passed": valid_combined_pass,
        },
        "combined_stale_case": {
            "predicted": stale_combined_hits,
            "passed": stale_combined_pass,
        },
        "valid_cases": valid_cases,
        "stale_cases": stale_cases,
        "failures": failures,
        "passed": not failures,
    }
    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if failures:
        raise AssertionError("; ".join(failures))
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "benchmark": result["benchmark"],
        "ontology_type_count": result["ontology_type_count"],
        "summary": result["summary"],
        "passed": result["passed"],
    }, indent=2))
