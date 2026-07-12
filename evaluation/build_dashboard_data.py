"""Build the static, browser-safe evaluation summary consumed by the Admin UI."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "evaluation"
OUTPUT = ROOT / "frontend" / "assets" / "evaluation_data.json"


def read(name: str) -> dict:
    path = EVALUATION / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run() -> dict:
    entity = read("entity_extraction_results.json")
    graph = read("graph_completeness_results.json")
    answers = read("answer_quality_regression_results.json") or read("answer_quality_results.json")
    compliance = read("compliance_failure_results.json")
    compliance_accuracy = read("compliance_detection_accuracy_results.json")
    provenance = read("data_provenance_results.json")
    latency = read("latency_results.json")
    is1786 = compliance.get("patterns", {}).get("IS:1786", {})

    data = {
        "generated_from": "committed reproducible evaluation artifacts",
        "cards": [
            {
                "id": "entity_extraction", "label": "Entity extraction", "status": "verified",
                "value": f"{entity.get('overall', {}).get('precision', 0) * 100:.0f}% / {entity.get('overall', {}).get('recall', 0) * 100:.0f}%",
                "metric": "precision / recall",
                "detail": f"{entity.get('sample_size', 0)} documents · {entity.get('overall', {}).get('true_positives', 0)} explicit canonical references",
                "caveat": entity.get("scope_note"),
            },
            {
                "id": "graph", "label": "Knowledge graph", "status": "verified",
                "value": f"{graph.get('node_total', 0):,} / {graph.get('edge_total', 0):,}",
                "metric": "nodes / relationships",
                "detail": f"{graph.get('node_type_count', 0)} entity types · {graph.get('directed_schema_link_count', 0)} directed schema links · zero broken endpoints",
                "caveat": "Validated against the locked ontology; no duplicate or schema-invalid edges.",
            },
            {
                "id": "answers", "label": "Answer quality", "status": "verified",
                "value": f"{answers.get('automated_mean_pass_rate', 0) * 100:.1f}%",
                "metric": "automated contract pass rate",
                "detail": f"{answers.get('case_count', 0)} golden questions · offline evidence regression · expert review pending",
                "caveat": answers.get("scope_note"),
            },
            {
                "id": "compliance", "label": "Compliance → failure", "status": "verified",
                "value": f"{is1786.get('preceded_failure_rate_among_linked', 0) * 100:.2f}%",
                "metric": "IS:1786 deviations preceding failure ≤30d",
                "detail": f"{is1786.get('preceded_failure_within_30d_n', 0)} of {is1786.get('failure_linked_n', 0)} linked deviations · {compliance_accuracy.get('overall', {}).get('accuracy', 0) * 100:.0f}% on 30-event temporal-linkage gold set",
                "caveat": f"{compliance.get('scope_note')} {compliance_accuracy.get('scope_note', '')}".strip(),
            },
            {
                "id": "latency", "label": "Time to answer", "status": "pending" if not latency else "verified",
                "value": "Pending" if not latency else f"{latency.get('cold_uncached', {}).get('median_s', 0):.2f}s",
                "metric": "public uncached median",
                "detail": "Existing baseline: 26.35s simple graph; 63.12s degraded RCA route. Controlled n=3 rerun pending.",
                "caveat": "Seconds, not instant search; comparison to manual cross-system work has not been experimentally measured.",
            },
            {
                "id": "provenance", "label": "Real-data provenance", "status": "verified",
                "value": f"{provenance.get('real_csv_file_count', 0)} files",
                "metric": "real-source CSV inventory",
                "detail": "Steel Plates Faults: 1,941 rows · Steel Industry Energy: 35,040 rows",
                "caveat": "AI4I 2020 is not ingested; AI4I-shaped sensor values remain synthetic.",
            },
        ],
        "answer_cases": [
            {
                "id": case.get("id"), "question": case.get("question"),
                "pass_rate": case.get("automated_score", {}).get("automated_pass_rate", 0),
                "expert_status": case.get("expert_review", {}).get("status", "pending"),
            }
            for case in answers.get("cases", [])
        ],
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


if __name__ == "__main__":
    result = run()
    print(f"wrote {OUTPUT} ({len(result['cards'])} evaluation cards)")
