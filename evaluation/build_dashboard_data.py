"""Build the browser-safe judging evidence consumed by the Evaluation Lab."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "evaluation"
OUTPUT = ROOT / "frontend" / "assets" / "evaluation_data.json"
REPOSITORY_BASE = "https://github.com/manendra-chintalapudi/Synapse/blob/main/"


def read(name: str) -> dict:
    path = EVALUATION / name
    if not path.exists():
        raise FileNotFoundError(f"Required evaluation artifact is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Evaluation artifact must contain a JSON object: {path}")
    return payload


def percent(value, digits=1) -> float:
    return round(float(value or 0) * 100, digits)


def clean_question(question: str) -> str:
    return re.sub(r"^Benchmark \d{4}-\d{2}-\d{2} [A-Z]:\s*", "", question or "")


def answer_sections(answer: str) -> dict:
    sections = {"direct": "", "insight": "", "action": "", "sources": [], "so_what": ""}
    for block in (answer or "").split("\n\n"):
        block = block.strip()
        if block.startswith("**Direct answer:**"):
            sections["direct"] = block.replace("**Direct answer:**", "", 1).strip()
        elif block.startswith("**Insight:**"):
            sections["insight"] = block.replace("**Insight:**", "", 1).strip()
        elif block.startswith("**Recommended action"):
            sections["action"] = re.sub(r"^\*\*Recommended action(?: for [^*]+)?:\*\*\s*", "", block).strip()
        elif block.startswith("**Sources used:**"):
            sections["sources"] = [
                line[2:].strip() for line in block.splitlines()[1:] if line.strip().startswith("- ")
            ]
        elif block.startswith("**So what:**"):
            sections["so_what"] = block.replace("**So what:**", "", 1).strip()
    return sections


def artifact(label: str, file_name: str, status: str, scope: str) -> dict:
    return {
        "label": label,
        "file": f"evaluation/{file_name}",
        "url": f"{REPOSITORY_BASE}evaluation/{file_name}",
        "status": status,
        "scope": scope,
    }


def run() -> dict:
    entity = read("entity_extraction_results.json")
    entity_runtime = read("canonical_id_runtime_results.json")
    graph = read("graph_completeness_results.json")
    live_graph = read("live_graph_parity_results.json")
    answers = read("answer_quality_regression_results.json")
    compliance = read("compliance_failure_results.json")
    compliance_accuracy = read("compliance_detection_accuracy_results.json")
    compliance_validation = read("compliance_validation_results.json")
    provenance = read("data_provenance_results.json")
    latency = read("latency_results.json")
    fast_paths = read("deterministic_fastpath_results.json")

    overall_entity = entity.get("overall", {})
    is1786 = compliance.get("patterns", {}).get("IS:1786", {})
    is1786_validation = compliance_validation.get("detail_pattern", {})
    named_data = provenance.get("named_dataset_claims", {})
    provenance_files = {row.get("path"): row for row in provenance.get("files", [])}
    energy_path = (named_data.get("Steel Industry Energy Consumption", {}).get("paths") or [""])[0]
    energy_rows = provenance_files.get(energy_path, {}).get("rows", 0)

    showcase_ids = [
        "rhf_cooling_circuit_rca",
        "is1786_failure_pattern",
        "dev1050_full_chain",
        "f1186_causality_boundary",
    ]
    cases_by_id = {case.get("id"): case for case in answers.get("cases", [])}
    answer_case_count = answers.get("case_count", 0)
    answer_passed_count = sum(
        bool(case.get("automated_score", {}).get("automated_check_count"))
        and case.get("automated_score", {}).get("automated_pass_count")
        == case.get("automated_score", {}).get("automated_check_count")
        for case in answers.get("cases", [])
    )
    answer_automated_passed = bool(answer_case_count) and answer_passed_count == answer_case_count
    showcase_answers = []
    for case_id in showcase_ids:
        case = cases_by_id.get(case_id)
        if not case:
            continue
        score = case.get("automated_score", {})
        response = case.get("response", {})
        showcase_answers.append({
            "id": case_id,
            "question": case.get("question"),
            "role": case.get("expected_role"),
            "source_layers": case.get("expected_source_layers", []),
            "ground_truth": case.get("ground_truth"),
            "model": response.get("model_used"),
            "sections": answer_sections(response.get("answer", "")),
            "score": {
                "pass_count": score.get("automated_pass_count", 0),
                "check_count": score.get("automated_check_count", 0),
                "pass_rate_pct": percent(score.get("automated_pass_rate", 0), 0),
                "fact_coverage_pct": percent(score.get("direct_fact_coverage", 0), 0),
                "insight": bool(score.get("correlation_or_insight")),
                "confidence": bool(score.get("implication_with_confidence")),
                "role_action": bool(score.get("role_scoped_action")),
                "citations": bool(score.get("all_required_layers_cited")),
                "healthy_execution": bool(score.get("healthy_execution")),
            },
            "expert_status": case.get("expert_review", {}).get("status", "pending"),
            "corpus_status": "locked_synthetic_demo_evidence",
            "routes": {
                "chat": "#/chat",
                "rca": (
                    "#/rca/F1128" if case_id == "dev1050_full_chain"
                    else "#/rca/F1186" if case_id in {"rhf_cooling_circuit_rca", "f1186_causality_boundary"}
                    else None
                ),
                "compliance": "#/compliance/is-1786" if case_id in {"is1786_failure_pattern", "dev1050_full_chain"} else None,
            },
        })

    entity_breakdown = []
    for key, label in (
        ("equipment_manual", "Equipment manuals"),
        ("sop", "SOPs"),
        ("deviation_report", "Deviation reports"),
    ):
        score = entity.get("by_document_type", {}).get(key, {})
        entity_breakdown.append({
            "id": key,
            "label": label,
            "documents": entity.get("sample_distribution", {}).get(key, 0),
            "references": score.get("true_positives", 0),
            "precision_pct": percent(score.get("precision", 0), 0),
            "recall_pct": percent(score.get("recall", 0), 0),
            "false_positives": score.get("false_positives", 0),
            "false_negatives": score.get("false_negatives", 0),
        })

    latency_cases = []
    for case in latency.get("cases", []):
        first = case.get("first", {}).get("server", {})
        repeat = case.get("repeat", {}).get("server", {})
        latency_cases.append({
            "id": case.get("id"),
            "question": clean_question(case.get("question", "")),
            "total_s": first.get("total_s", 0),
            "routing_s": first.get("routing_s", 0),
            "retrieval_s": first.get("retrieval_s", 0),
            "synthesis_s": first.get("synthesis_s", 0),
            "cached_repeat_s": repeat.get("total_s", 0),
            "layers": case.get("first", {}).get("layers", []),
            "model": case.get("first", {}).get("model"),
        })

    runtime_summary = entity_runtime.get("summary", {})
    runtime_types_passed = runtime_summary.get("valid_type_cases_passed", 0)
    runtime_type_count = runtime_summary.get("valid_type_case_count", 0) or entity_runtime.get("ontology_type_count", 0)
    entity_benchmark_passed = bool(entity.get("sample_size")) and all(
        overall_entity.get(key) == expected
        for key, expected in (("precision", 1.0), ("recall", 1.0), ("false_positives", 0), ("false_negatives", 0))
    )
    entity_contract_passed = entity_benchmark_passed and bool(entity_runtime.get("passed"))
    graph_contract_passed = bool(graph.get("passed")) and bool(live_graph.get("passed"))
    compliance_contract_passed = (
        bool(compliance_validation.get("passed"))
        and compliance_accuracy.get("overall", {}).get("n", 0) > 0
        and compliance_accuracy.get("overall", {}).get("accuracy") == 1.0
        and is1786.get("failure_linked_n") == is1786_validation.get("failure_linked_n")
        and is1786.get("preceded_failure_within_30d_n") == is1786_validation.get("downstream_failure_n")
    )
    expert_complete = bool(answers.get("expert_validation_complete"))

    cards = [
        {
            "id": "entity_extraction", "criterion": 1, "label": "Canonical ID extraction",
            "status": "scoped_verified" if entity_contract_passed else "method_gap",
            "status_label": "Scoped verified" if entity_contract_passed else "Contract failed",
            "value": f"{percent(overall_entity.get('precision'), 0):.0f}% / {percent(overall_entity.get('recall'), 0):.0f}%",
            "metric": "precision / recall",
            "detail": f"{entity.get('sample_size', 0)} demo documents · {overall_entity.get('true_positives', 0)} references · production runtime recognizes {runtime_types_passed}/{runtime_type_count} ontology ID types",
            "caveat": entity.get("scope_note"),
            "next_gate": "Independent span/type annotation for implicit and name-only entities.",
        },
        {
            "id": "answers", "criterion": 2, "label": "Answer quality",
            "status": "scoped_verified" if answer_automated_passed and expert_complete else ("partial" if answer_automated_passed else "method_gap"),
            "status_label": "Expert + automated verified" if answer_automated_passed and expert_complete else ("Automated verified" if answer_automated_passed else "Automated gaps"),
            "value": f"{answer_passed_count}/{answer_case_count}",
            "metric": "locked-evidence cases passed",
            "detail": "Six checks per answer: direct facts, insight, confidence, role action, citations and execution health.",
            "caveat": answers.get("scope_note"),
            "next_gate": "Repeat independent expert review on future benchmark changes." if expert_complete else "A domain expert must complete the frozen five-dimension scorecard.",
        },
        {
            "id": "graph", "criterion": 3, "label": "Knowledge graph structural integrity",
            "status": "scoped_verified" if graph_contract_passed else "partial",
            "status_label": "Scoped verified" if graph_contract_passed else "Parity gap",
            "value": f"{graph.get('node_total', 0):,} / {graph.get('edge_total', 0):,}",
            "metric": "nodes / relationships",
            "detail": f"{graph.get('node_type_count', 0)} node types · {graph.get('relationship_type_count', 0)} relationship names · {graph.get('directed_schema_link_count', 0)} directed schema links · {len(graph.get('broken_endpoints', []))} broken endpoints",
            "caveat": f"{live_graph.get('scope_note') or 'Deployed parity is not available.'} Domain-coverage recall against an external plant truth set is not measured.",
            "next_gate": "External domain coverage review and semantic property-level parity.",
        },
        {
            "id": "latency", "criterion": 4, "label": "Time to answer",
            "status": "partial", "status_label": "Operational baseline",
            "value": f"{latency.get('cold_uncached', {}).get('median_s', 0):.2f}s",
            "metric": "production server median · n=3",
            "detail": f"Deep RCA {next((row['total_s'] for row in latency_cases if row['id'] == 'deep_rca'), 0):.2f}s · exact cached repeats {latency.get('cached_repeat', {}).get('median_s', 0):.2f}s",
            "caveat": latency.get("scope_note"),
            "next_gate": "Controlled user study for manual-search time and correctness.",
        },
        {
            "id": "compliance", "criterion": 5, "label": "Compliance gap detection",
            "value": f"{percent(is1786.get('preceded_failure_rate_among_linked'), 2):.2f}%",
            "metric": "IS:1786 linked deviations → failure ≤30d",
            "status": "scoped_verified" if compliance_contract_passed else "partial", "status_label": "Scoped verified" if compliance_contract_passed else "Validation gap",
            "detail": f"{is1786.get('preceded_failure_within_30d_n', 0)} of {is1786.get('failure_linked_n', 0)} · Wilson 95% {percent((is1786.get('preceded_failure_rate_95pct_wilson') or [0, 0])[0], 2):.2f}–{percent((is1786.get('preceded_failure_rate_95pct_wilson') or [0, 0])[1], 2):.2f}% · {compliance_accuracy.get('overall', {}).get('true_positive', 0) + compliance_accuracy.get('overall', {}).get('true_negative', 0)}/{compliance_accuracy.get('overall', {}).get('n', 0)} locked temporal labels matched",
            "caveat": f"{compliance.get('scope_note', '')} {compliance_accuracy.get('scope_note', '')}".strip(),
            "next_gate": "Prospective validation is required before treating the association as predictive.",
        },
        {
            "id": "discovery", "criterion": 6, "label": "Cross-functional discovery",
            "status": "partial", "status_label": "Integration demonstrated",
            "value": "4 + 2",
            "metric": "operational catalogs + graph/RAG layers",
            "detail": "ERP, SCADA, QMS and CMMS can be joined with Neo4j graph and document evidence; two named, locally designated source dataset families are present and used as project evidence.",
            "caveat": "No before/after user study exists. Local naming and presence do not independently verify upstream provenance for either named dataset family; AI4I is synthetic and the extraction corpus is demo/synthetic.",
            "next_gate": "Measure discovery time and correctness with QA, Maintenance and Operations users on real documents.",
        },
    ]

    data = {
        "schema_version": 2,
        "generated_from": "committed reproducible evaluation artifacts",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_base": REPOSITORY_BASE,
        "headline": {
            "criterion_count": 6,
            "verified_or_scoped_count": sum(card["status"] in {"verified", "scoped_verified"} for card in cards),
            "partial_count": sum(card["status"] == "partial" for card in cards),
            "expert_validation_complete": expert_complete,
            "statement": "Every headline is tied to a committed artifact and every missing external gate stays visible.",
        },
        "cards": cards,
        "entity_extraction": {
            "sample_size": entity.get("sample_size", 0),
            "precision_pct": percent(overall_entity.get("precision"), 0),
            "recall_pct": percent(overall_entity.get("recall"), 0),
            "f1_pct": percent(overall_entity.get("f1"), 0),
            "true_positives": overall_entity.get("true_positives", 0),
            "false_positives": overall_entity.get("false_positives", 0),
            "false_negatives": overall_entity.get("false_negatives", 0),
            "self_document_id_count": entity.get("self_document_id_count", 0),
            "non_self_reference_count": entity.get("non_self_reference_count", 0),
            "unknown_rejection": entity.get("unknown_candidate_rejection", {}),
            "breakdown": entity_breakdown,
            "entity_type_support": entity.get("entity_type_support", {}),
            "gold_sha256": entity.get("gold_annotation_sha256"),
            "annotation_method": entity.get("gold_annotation_method"),
            "extractor_module": entity.get("extractor_module"),
            "production_usage": entity.get("production_usage"),
            "runtime_contract": entity_runtime,
            "corpus_label": entity.get("corpus_label"),
            "limitations": [
                "Explicit canonical identifiers only; implicit/name-only entity recognition is not scored.",
                "The corpus is synthetic/demo documentation, not a real-plant document sample.",
                "Independent annotator agreement and adjudication records are not available.",
            ],
        },
        "answer_benchmark": {
            "case_count": answers.get("case_count", 0),
            "automated_mean_pass_rate_pct": percent(answers.get("automated_mean_pass_rate"), 0),
            "expert_validation_complete": bool(answers.get("expert_validation_complete")),
            "generated_at": answers.get("generated_at"),
            "execution_scope": answers.get("execution_scope"),
            "showcase_answers": showcase_answers,
            "all_cases": [
                {
                    "id": case.get("id"),
                    "question": case.get("question"),
                    "pass_rate_pct": percent(case.get("automated_score", {}).get("automated_pass_rate"), 0),
                    "expert_status": case.get("expert_review", {}).get("status", "pending"),
                }
                for case in answers.get("cases", [])
            ],
        },
        "graph": {
            "node_total": graph.get("node_total", 0),
            "edge_total": graph.get("edge_total", 0),
            "node_type_count": graph.get("node_type_count", 0),
            "relationship_type_count": graph.get("relationship_type_count", 0),
            "directed_schema_link_count": graph.get("directed_schema_link_count", 0),
            "node_counts": graph.get("node_counts", {}),
            "relationship_counts": graph.get("relationship_counts", {}),
            "checks": {
                "duplicate_nodes": len(graph.get("duplicate_nodes", [])),
                "duplicate_edges": len(graph.get("duplicate_edges", [])),
                "broken_endpoints": len(graph.get("broken_endpoints", [])),
                "invalid_schema_edges": len(graph.get("invalid_schema_edges", [])),
            },
            "passed": bool(graph.get("passed")),
            "live_parity": live_graph,
        },
        "latency": {
            "measurement_surface": latency.get("measurement_surface"),
            "generated_at": latency.get("generated_at"),
            "sample_size": latency.get("sample_size", 0),
            "cold_uncached": latency.get("cold_uncached", {}),
            "cached_repeat": latency.get("cached_repeat", {}),
            "cases": latency_cases,
            "scope_note": latency.get("scope_note"),
            "fast_path": {
                "case_count": fast_paths.get("case_count", 0),
                "passed": bool(fast_paths.get("passed")),
                "max_total_s": fast_paths.get("max_total_s", 0),
                "cases": fast_paths.get("cases", []),
                "scope_note": fast_paths.get("scope_note"),
            },
        },
        "compliance": {
            "window_days": compliance.get("window_days", 30),
            "patterns": compliance.get("patterns", {}),
            "accuracy": compliance_accuracy.get("overall", {}),
            "accuracy_scope": compliance_accuracy.get("scope_note"),
            "is1786": {
                "deviation_cohort_n": is1786.get("deviation_cohort_n", 0),
                "failure_linked_n": is1786.get("failure_linked_n", 0),
                "downstream_n": is1786.get("preceded_failure_within_30d_n", 0),
                "rate_among_linked_pct": percent(is1786.get("preceded_failure_rate_among_linked"), 2),
                "rate_full_cohort_pct": is1786_validation.get("downstream_rate_full_cohort_pct", 0),
                "wilson_95pct": [percent(value, 2) for value in is1786.get("preceded_failure_rate_95pct_wilson", [])],
                "confidence": is1786.get("confidence"),
                "top_root_cause": is1786_validation.get("most_common_root_cause"),
                "top_root_cause_n": is1786_validation.get("most_common_root_cause_n", 0),
            },
        },
        "provenance": {
            "real_csv_file_count": provenance.get("real_csv_file_count", 0),
            "unique_real_payload_count": len({row.get("sha256") for row in provenance.get("files", []) if row.get("sha256")}),
            "document_source_labels": provenance.get("document_source_labels", {}),
            "datasets": [
                {
                    "name": "Steel Plates Faults",
                    "status": "locally_designated_real_source",
                    "rows": named_data.get("Steel Plates Faults", {}).get("rows", 0),
                    "used_as": named_data.get("Steel Plates Faults", {}).get("used_as"),
                    "note": named_data.get("Steel Plates Faults", {}).get("provenance_note"),
                },
                {
                    "name": "Steel Industry Energy Consumption",
                    "status": "locally_designated_real_source",
                    "rows": energy_rows,
                    "used_as": named_data.get("Steel Industry Energy Consumption", {}).get("used_as"),
                    "note": named_data.get("Steel Industry Energy Consumption", {}).get("note"),
                },
                {
                    "name": "AI4I 2020 Predictive Maintenance",
                    "status": "official_synthetic_reference",
                    "rows": named_data.get("AI4I 2020 Predictive Maintenance", {}).get("rows", 0),
                    "machine_failures": named_data.get("AI4I 2020 Predictive Maintenance", {}).get("duckdb_validation", {}).get("machine_failures", 0),
                    "doi": named_data.get("AI4I 2020 Predictive Maintenance", {}).get("doi"),
                    "license": named_data.get("AI4I 2020 Predictive Maintenance", {}).get("license"),
                    "used_as": named_data.get("AI4I 2020 Predictive Maintenance", {}).get("used_as"),
                },
            ],
        },
        "artifacts": [
            artifact("Canonical ID benchmark", "entity_extraction_results.json", "scoped_verified" if entity_benchmark_passed else "method_gap", "25-document explicit-ID resolution"),
            artifact("Production ID runtime contract", "canonical_id_runtime_results.json", "verified" if entity_runtime.get("passed") else "method_gap", "All 11 ontology ID types and stale-ID rejection"),
            artifact("Locked extraction labels", "entity_extraction_gold.json", "method_gap", "Ontology-assisted manifest; no inter-annotator agreement record"),
            artifact("Graph integrity audit", "graph_completeness_results.json", "scoped_verified" if graph.get("passed") else "method_gap", "Locked local ontology structural integrity"),
            artifact("Live graph parity", "live_graph_parity_results.json", "scoped_verified" if live_graph.get("passed") else "partial", "Deployed totals, distributions and primary-ID integrity"),
            artifact("Answer regression", "answer_quality_regression_results.json", "scoped_verified" if answer_automated_passed and expert_complete else ("partial" if answer_automated_passed else "method_gap"), "Offline deterministic evidence contract"),
            artifact("Expert scorecard", "domain_expert_scorecard.md", "verified" if expert_complete else "pending", "Independent domain review complete" if expert_complete else "Requires an independent domain reviewer"),
            artifact("Compliance pattern cohort", "compliance_failure_results.json", "scoped_verified" if compliance_contract_passed else "partial", "30-day directional timing with denominators and intervals"),
            artifact("Compliance correlation", "compliance_validation_results.json", "scoped_verified" if compliance_validation.get("passed") else "partial", "Direct Cypher and 30-day directional timing"),
            artifact("Compliance temporal-rule test", "compliance_detection_accuracy_results.json", "scoped_verified" if compliance_accuracy.get("overall", {}).get("accuracy") == 1.0 else "partial", "Balanced n=30 locked time-window labels"),
            artifact("Production latency", "latency_results.json", "partial", "Server timing n=3; no manual comparison"),
            artifact("Deterministic fast paths", "deterministic_fastpath_results.json", "scoped_verified" if fast_paths.get("passed") else "partial", "Five local cited routine-answer contracts"),
            artifact("Data provenance", "data_provenance_results.json", "partial", "Named source audit and synthetic-reference disclosure"),
        ],
    }
    OUTPUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


if __name__ == "__main__":
    result = run()
    print(f"wrote {OUTPUT} ({len(result['cards'])} judging criteria)")
