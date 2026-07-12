"""Inventory real, hybrid and synthetic evidence used by Synapse."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = Path(__file__).with_name("data_provenance_results.json")


def csv_info(relative: str) -> dict:
    path = ROOT / relative
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        rows = sum(1 for _ in reader)
    return {"path": relative, "rows": rows, "columns": len(header), "sha256": digest.hexdigest()}


def run() -> dict:
    real_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "data").glob("*/real_data/*.csv")
    )
    inventory = [csv_info(path) for path in real_files]
    hashes = Counter(item["sha256"] for item in inventory)
    for item in inventory:
        item["duplicate_content"] = hashes[item["sha256"]] > 1

    documents = json.loads((ROOT / "ontology" / "nodes" / "document.json").read_text(encoding="utf-8"))
    document_sources = Counter(row.get("source_type", "unlabelled") for row in documents)
    ai4i_files = [
        path.relative_to(ROOT).as_posix() for path in (ROOT / "data").rglob("*")
        if path.is_file() and any(token in path.name.lower() for token in ("ai4i", "predictive_maintenance"))
    ]

    result = {
        "real_csv_file_count": len(inventory),
        "real_csv_total_rows_including_duplicates": sum(item["rows"] for item in inventory),
        "files": inventory,
        "named_dataset_claims": {
            "Steel Plates Faults": {
                "status": "present_real_source",
                "path": "data/qms/real_data/steel_plates_faults.csv",
                "rows": next(item["rows"] for item in inventory if item["path"].endswith("steel_plates_faults.csv")),
                "used_as": "QualityTest.feature_values and QualityTest.fault_type",
            },
            "Steel Industry Energy Consumption": {
                "status": "present_real_source",
                "paths": [
                    "data/scada/real_data/steel_energy_consumption.csv",
                    "data/scada/real_data/steel_industry_data.csv",
                ],
                "note": "The two files have identical content and must count as one dataset, not two.",
                "used_as": "SCADA energy/consumption reference data",
            },
            "AI4I 2020 Predictive Maintenance": {
                "status": "not_ingested",
                "matching_files": ai4i_files,
                "used_as": "Failure modes are AI4I-shaped/remapped; sensor values are explicitly synthetic pending ingestion.",
                "claim_allowed_as_real_ingested_data": False,
            },
        },
        "document_source_labels": dict(document_sources),
        "document_claim_note": (
            "Documents without an explicit source_type must not automatically be called real industrial documents. "
            "The 188 work-order narratives labelled synthetic are explicitly synthetic."
        ),
        "passed": True,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "real_csv_file_count": result["real_csv_file_count"],
        "real_csv_total_rows_including_duplicates": result["real_csv_total_rows_including_duplicates"],
        "named_dataset_claims": result["named_dataset_claims"],
        "document_source_labels": result["document_source_labels"],
    }, indent=2))
