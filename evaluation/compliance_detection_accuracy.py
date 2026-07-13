"""Evaluate 30-day temporal compliance-gap linkage against locked date-rule labels."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = Path(__file__).with_name("compliance_detection_gold.json")
RESULTS = Path(__file__).with_name("compliance_detection_accuracy_results.json")


def metrics(counts: Counter) -> dict:
    tp, fp, tn, fn = (counts[key] for key in ("tp", "fp", "tn", "fn"))
    total = tp + fp + tn + fn
    return {
        "n": total, "true_positive": tp, "false_positive": fp, "true_negative": tn, "false_negative": fn,
        "accuracy": round((tp + tn) / total, 4) if total else 0,
        "precision": round(tp / (tp + fp), 4) if tp + fp else 1,
        "recall": round(tp / (tp + fn), 4) if tp + fn else 1,
        "specificity": round(tn / (tn + fp), 4) if tn + fp else 1,
    }


def run() -> dict:
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    deviations = {row["deviation_id"]: row for row in json.loads((ROOT / "ontology/nodes/deviation.json").read_text(encoding="utf-8"))}
    failures = {row["failure_id"]: row for row in json.loads((ROOT / "ontology/nodes/failure.json").read_text(encoding="utf-8"))}
    overall, families, rows = Counter(), defaultdict(Counter), []
    for event in gold["events"]:
        deviation, failure = deviations[event["deviation_id"]], failures[event["failure_id"]]
        flagged = date.fromisoformat(event["date_flagged"])
        failed = date.fromisoformat(event["failure_date"])
        if deviation.get("failure_id_fk") != event["failure_id"] or datetime.fromisoformat(failure["timestamp"]).date() != failed:
            raise ValueError(f"locked evidence drift for {event['deviation_id']}")
        delta = (failed - flagged).days
        predicted = 0 <= delta <= 30
        expected = event["within_30d"]
        bucket = "tp" if predicted and expected else "fp" if predicted else "fn" if expected else "tn"
        overall[bucket] += 1; families[event["standard_family"]][bucket] += 1
        rows.append({**event, "predicted_within_30d": predicted, "delta_days": delta, "correct": predicted == expected})
    result = {
        "benchmark": "30-day compliance-to-failure temporal linkage detection",
        "gold_file": str(GOLD.relative_to(ROOT)).replace("\\", "/"),
        "gold_sha256": hashlib.sha256(GOLD.read_bytes()).hexdigest(),
        "annotation_method": gold["annotation_method"],
        "overall": metrics(overall),
        "by_standard_family": {name: metrics(counts) for name, counts in families.items()},
        "scope_note": gold["scope"],
        "events": rows,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({"benchmark": result["benchmark"], "overall": result["overall"], "by_standard_family": result["by_standard_family"], "scope_note": result["scope_note"]}, indent=2))
