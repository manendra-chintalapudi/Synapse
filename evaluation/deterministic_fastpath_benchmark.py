"""Measure routine deterministic questions without calling the LLM synthesizer."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import ask_synapse  # noqa: E402

RESULTS = Path(__file__).with_name("deterministic_fastpath_results.json")
QUESTIONS = [
    "How many coils failed quality testing?",
    "Which equipment failed most this quarter?",
    "Which standard do coating faults violate?",
    "What is the quality-test deviation rate?",
    "How many documents are in the knowledge base?",
]


def run() -> dict:
    cases = []
    for question in QUESTIONS:
        response = ask_synapse(question)
        latency = response["latency"]
        cases.append({
            "question": question,
            "model_used": response.get("model_used"),
            "latency": latency,
            "citation_count": len(response.get("sources") or []),
            "passed": response.get("model_used") == "deterministic/evidence-template"
                      and latency.get("synthesis_s") == 0
                      and bool(response.get("sources")),
        })
    result = {
        "benchmark": "routine deterministic fast paths",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "passed": all(row["passed"] for row in cases),
        "max_total_s": max(row["latency"]["total_s"] for row in cases),
        "cases": cases,
        "scope_note": "Local direct structured/ontology retrieval; public network latency and expert review are separate gates.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
