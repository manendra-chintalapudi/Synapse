"""Measure public end-to-end cold and cached query latency without overselling speed."""
from __future__ import annotations

import argparse
import json
import os
import statistics
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RESULTS = Path(__file__).with_name("latency_results.json")
QUESTIONS = [
    {"id": "simple_graph", "question": "Which equipment produced coil C10235?"},
    {"id": "document_qa", "question": "Explain what ASTM A370 covers and what QA should verify."},
    {"id": "deep_rca", "question": "Why did failure F1186 occur, which procedure gap contributed, and what should Maintenance do next?"},
]


def ask(base_url: str, question: str, timeout: int, token: str = "", retries: int = 2) -> dict:
    payload = json.dumps({"question": question}).encode("utf-8")
    last_error = None
    for attempt in range(retries + 1):
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(
            base_url.rstrip("/") + "/api/ask", data=payload,
            headers=headers, method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            body["observed_wall_time_s"] = round(time.perf_counter() - started, 2)
            return body
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 ** attempt)
    raise last_error


def summary(values: list[float]) -> dict:
    return {
        "n": len(values), "min_s": round(min(values), 2), "median_s": round(statistics.median(values), 2),
        "max_s": round(max(values), 2), "mean_s": round(statistics.mean(values), 2),
    } if values else {"n": 0}


def run(base_url: str, timeout: int, token: str = "") -> dict:
    rows = []
    for case in QUESTIONS:
        row = dict(case)
        try:
            first = ask(base_url, case["question"], timeout, token)
            second = ask(base_url, case["question"], timeout, token)
            row.update({
                "first": {"wall_s": first["observed_wall_time_s"], "server": first.get("latency"), "model": first.get("model_used")},
                "repeat": {"wall_s": second["observed_wall_time_s"], "server": second.get("latency"), "model": second.get("model_used")},
            })
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    cold = [r["first"]["wall_s"] for r in rows if r.get("first") and not r["first"]["server"].get("cache_hit")]
    cached = [r["repeat"]["wall_s"] for r in rows if r.get("repeat") and r["repeat"]["server"].get("cache_hit")]
    result = {
        "benchmark": "public end-to-end time to answer",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "cold_uncached": summary(cold),
        "cached_repeat": summary(cached),
        "cases": rows,
        "scope_note": (
            "Wall time includes public network, routing, retrieval and generation. Small n=3 operational benchmark; "
            "not a claim of statistical superiority to web search or a controlled manual-work study."
        ),
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
    print(json.dumps(result, indent=2))
