"""Run a reproducible, evidence-grounded answer-quality benchmark against Synapse.

Automated checks cover factual anchors, citations and the four-layer answer contract. The
result intentionally keeps a separate `expert_review` field: automated structure checks are
not represented as domain-expert validation.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RESULTS = Path(__file__).with_name("answer_quality_results.json")

CASES = [
    {
        "id": "rhf_cooling_circuit_rca",
        "question": "What caused failure F1186, what procedure gap contributed, and what should Maintenance do next?",
        "expected_fact_patterns": [
            r"F1186", r"RCA1186", r"EQ-RHF-01|Reheating Furnace #?1",
            r"insufficient heat dissipation|cooling (?:airflow|flow)", r"PROC-022",
            r"cooling/lubrication verification|Step 4", r"temperature-differential alarm|restored cooling circuit",
        ],
        "expected_source_layers": ["Graph", "RAG"],
        "expected_role": "maintenance",
        "ground_truth": "ontology/nodes/failure.json:F1186 + ontology/nodes/rca.json:RCA1186",
    },
    {
        "id": "coil_equipment_lineage",
        "question": "Which equipment produced coil C10234, and what is the operational implication?",
        "expected_fact_patterns": [
            r"C10234", r"EQ-FMS-01|Finishing Mill Stand F1", r"PRODUCED_AT",
        ],
        "expected_source_layers": ["Graph"],
        "expected_role": "operations",
        "ground_truth": "ontology/nodes/coil.json:C10234",
    },
    {
        "id": "is2062_scope_and_action",
        "question": "What does IS 2062 cover, what risk does non-compliance create, and what should QA verify?",
        "expected_fact_patterns": [
            r"IS\s*:?[ -]?2062", r"hot.?rolled", r"structural steel", r"chemical|mechanical", r"test",
        ],
        "expected_source_layers": ["RAG"],
        "expected_role": "qa|quality",
        "ground_truth": "data/unstructured/standards/is_2062.md + DOC1058",
    },
]


def post_question(base_url: str, question: str, timeout: int, token: str = "") -> dict:
    payload = json.dumps({"question": question}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/ask", data=payload,
        headers=headers, method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    body["observed_wall_time_s"] = round(time.perf_counter() - started, 2)
    return body


def score(case: dict, response: dict) -> dict:
    answer = response.get("answer", "")
    facts = [bool(re.search(pattern, answer, re.I)) for pattern in case["expected_fact_patterns"]]
    cited_layers = {
        layer for layer in case["expected_source_layers"]
        if re.search(rf"\[{re.escape(layer)}\s*:", answer, re.I)
    }
    checks = {
        "direct_fact_coverage": round(sum(facts) / len(facts), 3),
        "correlation_or_insight": bool(re.search(r"\binsight\b|\bcorrelat|\bpattern\b|\bacross\b|\blink(?:ed)?\b", answer, re.I)),
        "implication_with_confidence": bool(re.search(r"\b(?:high|medium|low) confidence\b|\bconfidence\s*[:=-]", answer, re.I))
            and bool(re.search(r"\bimplication\b|\brisk\b|\bexposure\b|\bimpact\b", answer, re.I)),
        "role_scoped_action": bool(re.search(r"\brecommend|\bnext step|\baction\b", answer, re.I))
            and bool(re.search(case["expected_role"], answer, re.I)),
        "required_source_layers": sorted(cited_layers),
        "all_required_layers_cited": len(cited_layers) == len(case["expected_source_layers"]),
        "healthy_execution": response.get("model_used") not in (None, "error")
            and not response.get("retrieval_errors") and "<unk>" not in answer.lower(),
    }
    binary = [
        checks["direct_fact_coverage"] >= 0.75,
        checks["correlation_or_insight"], checks["implication_with_confidence"],
        checks["role_scoped_action"], checks["all_required_layers_cited"], checks["healthy_execution"],
    ]
    checks["automated_pass_count"] = sum(binary)
    checks["automated_check_count"] = len(binary)
    checks["automated_pass_rate"] = round(sum(binary) / len(binary), 3)
    return checks


def run(base_url: str, timeout: int, token: str = "") -> dict:
    rows = []
    for case in CASES:
        try:
            response = post_question(base_url, case["question"], timeout, token)
            row = {**case, "response": response, "automated_score": score(case, response)}
        except Exception as exc:
            row = {**case, "error": f"{type(exc).__name__}: {exc}", "automated_score": {"automated_pass_rate": 0}}
        row["expert_review"] = {
            "status": "pending",
            "factual_correctness_1_to_5": None,
            "operational_usefulness_1_to_5": None,
            "notes": None,
        }
        rows.append(row)

    result = {
        "benchmark": "domain-expert answer quality",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "case_count": len(rows),
        "automated_mean_pass_rate": round(sum(r["automated_score"]["automated_pass_rate"] for r in rows) / len(rows), 3),
        "expert_validation_complete": False,
        "scope_note": "Automated rubric results are not a substitute for domain-expert scoring.",
        "cases": rows,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://web-production-a9e7.up.railway.app")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--token", default=os.environ.get("SYNAPSE_BENCHMARK_TOKEN", ""), help="Supabase access token; prefer SYNAPSE_BENCHMARK_TOKEN")
    args = parser.parse_args()
    result = run(args.base_url, args.timeout, args.token)
    print(json.dumps({
        "benchmark": result["benchmark"],
        "case_count": result["case_count"],
        "automated_mean_pass_rate": result["automated_mean_pass_rate"],
        "expert_validation_complete": result["expert_validation_complete"],
        "cases": [{"id": row["id"], "score": row["automated_score"], "error": row.get("error")} for row in result["cases"]],
    }, indent=2))
