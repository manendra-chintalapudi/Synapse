"""Validate that the judging dashboard is faithful to every consumed source artifact."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATION = ROOT / "evaluation"
DATA = ROOT / "frontend" / "assets" / "evaluation_data.json"
RESULTS = EVALUATION / "evaluation_dashboard_validation_results.json"


def load(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def percent(value: float, digits: int = 1) -> float:
    return round(float(value or 0) * 100, digits)


def answer_sections(answer: str) -> dict:
    """Project a benchmark answer exactly as the dashboard builder does."""
    sections = {"direct": "", "insight": "", "action": "", "sources": [], "so_what": ""}
    for block in (answer or "").split("\n\n"):
        block = block.strip()
        if block.startswith("**Direct answer:**"):
            sections["direct"] = block.replace("**Direct answer:**", "", 1).strip()
        elif block.startswith("**Insight:**"):
            sections["insight"] = block.replace("**Insight:**", "", 1).strip()
        elif block.startswith("**Recommended action"):
            sections["action"] = re.sub(
                r"^\*\*Recommended action(?: for [^*]+)?:\*\*\s*", "", block
            ).strip()
        elif block.startswith("**Sources used:**"):
            sections["sources"] = [
                line[2:].strip()
                for line in block.splitlines()[1:]
                if line.strip().startswith("- ")
            ]
        elif block.startswith("**So what:**"):
            sections["so_what"] = block.replace("**So what:**", "", 1).strip()
    return sections


def expected_showcase(case: dict) -> dict:
    """Return every evidence-derived field rendered in a showcase answer."""
    score = case.get("automated_score", {})
    response = case.get("response", {})
    return {
        "id": case.get("id"),
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
    }


def has_all(text: str, values: list[object]) -> bool:
    rendered = str(text or "")
    return all(str(value) in rendered for value in values)


def run() -> dict:
    dashboard = load(DATA)
    entity = load(EVALUATION / "entity_extraction_results.json")
    runtime = load(EVALUATION / "canonical_id_runtime_results.json")
    graph = load(EVALUATION / "graph_completeness_results.json")
    live_graph = load(EVALUATION / "live_graph_parity_results.json")
    answers = load(EVALUATION / "answer_quality_regression_results.json")
    compliance = load(EVALUATION / "compliance_failure_results.json")
    compliance_accuracy = load(EVALUATION / "compliance_detection_accuracy_results.json")
    compliance_validation = load(EVALUATION / "compliance_validation_results.json")
    provenance = load(EVALUATION / "data_provenance_results.json")
    latency = load(EVALUATION / "latency_results.json")
    fast_paths = load(EVALUATION / "deterministic_fastpath_results.json")

    cards = {card["id"]: card for card in dashboard.get("cards", [])}
    expected_ids = {"entity_extraction", "answers", "graph", "latency", "compliance", "discovery"}
    runtime_summary = runtime.get("summary", {})
    answer_case_count = answers.get("case_count", 0)
    answer_passed_count = sum(
        case.get("automated_score", {}).get("automated_check_count", 0) > 0
        and case.get("automated_score", {}).get("automated_pass_count")
        == case.get("automated_score", {}).get("automated_check_count")
        for case in answers.get("cases", [])
    )
    answers_passed = bool(answer_case_count) and answer_passed_count == answer_case_count
    expected_answer_status = (
        "scoped_verified" if answers_passed and answers.get("expert_validation_complete")
        else "partial" if answers_passed else "method_gap"
    )
    answer_cases = {case.get("id"): case for case in answers.get("cases", [])}
    expected_showcase_ids = {
        "rhf_cooling_circuit_rca",
        "is1786_failure_pattern",
        "dev1050_full_chain",
        "f1186_causality_boundary",
    }
    dashboard_showcases = {
        row.get("id"): row for row in dashboard.get("answer_benchmark", {}).get("showcase_answers", [])
    }
    showcase_source_fidelity = set(dashboard_showcases) == expected_showcase_ids and all(
        case_id in answer_cases
        and all(
            dashboard_showcases[case_id].get(field) == value
            for field, value in expected_showcase(answer_cases[case_id]).items()
        )
        and dashboard_showcases[case_id].get("corpus_status")
        == "locked_synthetic_demo_evidence"
        for case_id in expected_showcase_ids
    )
    expected_all_cases = [
        {
            "id": case.get("id"),
            "question": case.get("question"),
            "pass_rate_pct": percent(
                case.get("automated_score", {}).get("automated_pass_rate", 0), 0
            ),
            "expert_status": case.get("expert_review", {}).get("status", "pending"),
        }
        for case in answers.get("cases", [])
    ]

    is1786 = compliance["patterns"]["IS:1786"]
    is1786_detail = compliance_validation["detail_pattern"]
    is1786_dashboard = dashboard.get("compliance", {}).get("is1786", {})
    expected_is1786_dashboard = {
        "deviation_cohort_n": is1786.get("deviation_cohort_n", 0),
        "failure_linked_n": is1786.get("failure_linked_n", 0),
        "downstream_n": is1786.get("preceded_failure_within_30d_n", 0),
        "rate_among_linked_pct": percent(
            is1786.get("preceded_failure_rate_among_linked"), 2
        ),
        "rate_full_cohort_pct": is1786_detail.get("downstream_rate_full_cohort_pct", 0),
        "wilson_95pct": [
            percent(value, 2)
            for value in is1786.get("preceded_failure_rate_95pct_wilson", [])
        ],
        "confidence": is1786.get("confidence"),
        "top_root_cause": is1786_detail.get("most_common_root_cause"),
        "top_root_cause_n": is1786_detail.get("most_common_root_cause_n", 0),
    }
    correct_temporal = (
        compliance_accuracy["overall"]["true_positive"]
        + compliance_accuracy["overall"]["true_negative"]
    )
    entity_passed = (
        entity.get("sample_size", 0) > 0
        and entity["overall"]["precision"] == 1.0
        and entity["overall"]["recall"] == 1.0
        and entity["overall"]["false_positives"] == 0
        and entity["overall"]["false_negatives"] == 0
        and runtime.get("passed") is True
    )
    graph_passed = graph.get("passed") is True and live_graph.get("passed") is True
    compliance_passed = (
        compliance_validation.get("passed") is True
        and compliance_accuracy["overall"]["n"] > 0
        and compliance_accuracy["overall"]["accuracy"] == 1.0
        and is1786["failure_linked_n"] == is1786_detail["failure_linked_n"]
        and is1786["preceded_failure_within_30d_n"] == is1786_detail["downstream_failure_n"]
    )

    manual_pattern = compliance_validation.get("manual_pattern", {})
    manual_top_cause = compliance_validation.get("manual_top_cause", {})
    compliance_sources_reconcile = (
        manual_pattern.get("deviationCohort") == is1786.get("deviation_cohort_n")
        and manual_pattern.get("failureLinked") == is1786.get("failure_linked_n")
        and manual_pattern.get("downstream30d")
        == is1786.get("preceded_failure_within_30d_n")
        and is1786_detail.get("deviation_cohort_n") == is1786.get("deviation_cohort_n")
        and is1786_detail.get("failure_linked_n") == is1786.get("failure_linked_n")
        and is1786_detail.get("downstream_failure_n")
        == is1786.get("preceded_failure_within_30d_n")
        and is1786_detail.get("downstream_rate_among_linked_pct")
        == percent(is1786.get("preceded_failure_rate_among_linked"), 2)
        and is1786_detail.get("downstream_rate_full_cohort_pct")
        == round(
            100
            * is1786.get("preceded_failure_within_30d_n", 0)
            / max(is1786.get("deviation_cohort_n", 0), 1),
            2,
        )
        and is1786_detail.get("wilson_95pct")
        == [
            percent(value, 2)
            for value in is1786.get("preceded_failure_rate_95pct_wilson", [])
        ]
        and is1786_detail.get("most_common_root_cause")
        == manual_top_cause.get("rootCause")
        and is1786_detail.get("most_common_root_cause_n")
        == manual_top_cause.get("count")
    )

    dashboard_datasets = {row["name"]: row for row in dashboard["provenance"]["datasets"]}
    named_sources = provenance["named_dataset_claims"]
    energy_path = named_sources["Steel Industry Energy Consumption"]["paths"][0]
    energy_rows = next(row["rows"] for row in provenance["files"] if row["path"] == energy_path)
    required_artifacts = {
        "evaluation/entity_extraction_results.json",
        "evaluation/canonical_id_runtime_results.json",
        "evaluation/graph_completeness_results.json",
        "evaluation/live_graph_parity_results.json",
        "evaluation/answer_quality_regression_results.json",
        "evaluation/compliance_failure_results.json",
        "evaluation/compliance_validation_results.json",
        "evaluation/compliance_detection_accuracy_results.json",
        "evaluation/latency_results.json",
        "evaluation/deterministic_fastpath_results.json",
        "evaluation/data_provenance_results.json",
    }
    listed_artifacts = {row["file"] for row in dashboard.get("artifacts", [])}

    deep_rca_s = next(
        (
            case.get("first", {}).get("server", {}).get("total_s", 0)
            for case in latency.get("cases", [])
            if case.get("id") == "deep_rca"
        ),
        0,
    )
    is1786_wilson = expected_is1786_dashboard["wilson_95pct"] or [0, 0]
    expected_card_statuses = {
        "entity_extraction": "scoped_verified" if entity_passed else "method_gap",
        "answers": expected_answer_status,
        "graph": "scoped_verified" if graph_passed else "partial",
        "latency": "partial",
        "compliance": "scoped_verified" if compliance_passed else "partial",
        "discovery": "partial",
    }
    card_source_claims = (
        all(cards[card_id].get("status") == status for card_id, status in expected_card_statuses.items())
        and cards["entity_extraction"].get("value")
        == f"{percent(entity['overall']['precision'], 0):.0f}% / {percent(entity['overall']['recall'], 0):.0f}%"
        and has_all(
            cards["entity_extraction"].get("detail"),
            [
                entity.get("sample_size", 0),
                entity["overall"].get("true_positives", 0),
                f"{runtime_summary.get('valid_type_cases_passed', 0)}/{runtime_summary.get('valid_type_case_count', 0)}",
            ],
        )
        and cards["entity_extraction"].get("caveat") == entity.get("scope_note")
        and cards["answers"].get("value") == f"{answer_passed_count}/{answer_case_count}"
        and cards["answers"].get("caveat") == answers.get("scope_note")
        and cards["graph"].get("value") == f"{graph.get('node_total', 0):,} / {graph.get('edge_total', 0):,}"
        and has_all(
            cards["graph"].get("detail"),
            [
                graph.get("node_type_count", 0),
                graph.get("relationship_type_count", 0),
                graph.get("directed_schema_link_count", 0),
                len(graph.get("broken_endpoints", [])),
            ],
        )
        and cards["latency"].get("value")
        == f"{latency.get('cold_uncached', {}).get('median_s', 0):.2f}s"
        and has_all(
            cards["latency"].get("detail"),
            [
                f"{deep_rca_s:.2f}s",
                f"{latency.get('cached_repeat', {}).get('median_s', 0):.2f}s",
            ],
        )
        and str(latency.get("sample_size", 0)) in cards["latency"].get("metric", "")
        and cards["latency"].get("caveat") == latency.get("scope_note")
        and cards["compliance"].get("value")
        == f"{expected_is1786_dashboard['rate_among_linked_pct']:.2f}%"
        and has_all(
            cards["compliance"].get("detail"),
            [
                f"{expected_is1786_dashboard['downstream_n']} of {expected_is1786_dashboard['failure_linked_n']}",
                f"{is1786_wilson[0]:.2f}",
                f"{is1786_wilson[1]:.2f}%",
                f"{correct_temporal}/{compliance_accuracy['overall']['n']}",
            ],
        )
        and cards["discovery"].get("value") == "4 + 2"
        and has_all(
            cards["discovery"].get("detail", "").lower(),
            ["erp", "scada", "qms", "cmms", "neo4j", "document"],
        )
        and "upstream provenance" in cards["discovery"].get("caveat", "").lower()
        and "independently verif" in cards["discovery"].get("caveat", "").lower()
        and "synthetic" in cards["discovery"].get("caveat", "").lower()
    )

    checks = {
        "schema_version": dashboard.get("schema_version") == 2,
        "six_criteria": set(cards) == expected_ids and dashboard["headline"]["criterion_count"] == 6,
        "headline_status_counts": (
            dashboard["headline"]["verified_or_scoped_count"]
            == sum(card["status"] in {"verified", "scoped_verified"} for card in cards.values())
            and dashboard["headline"]["partial_count"]
            == sum(card["status"] == "partial" for card in cards.values())
        ),
        "entity_and_runtime": (
            dashboard["entity_extraction"]["sample_size"] == entity["sample_size"]
            and dashboard["entity_extraction"]["true_positives"] == entity["overall"]["true_positives"]
            and dashboard["entity_extraction"]["precision_pct"] == percent(entity["overall"]["precision"], 0)
            and dashboard["entity_extraction"]["recall_pct"] == percent(entity["overall"]["recall"], 0)
            and dashboard["entity_extraction"]["runtime_contract"] == runtime
            and f"{runtime_summary['valid_type_cases_passed']}/{runtime_summary['valid_type_case_count']}" in cards["entity_extraction"]["detail"]
            and cards["entity_extraction"]["status"] == ("scoped_verified" if entity_passed else "method_gap")
        ),
        "graph_structural_scope": (
            dashboard["graph"]["node_total"] == graph["node_total"]
            and dashboard["graph"]["edge_total"] == graph["edge_total"]
            and dashboard["graph"]["relationship_type_count"] == graph["relationship_type_count"]
            and dashboard["graph"]["directed_schema_link_count"] == graph["directed_schema_link_count"]
            and dashboard["graph"]["live_parity"] == live_graph
            and cards["graph"]["status"] == ("scoped_verified" if graph_passed else "partial")
            and "structural integrity" in cards["graph"]["label"].lower()
            and "domain-coverage recall" in cards["graph"]["caveat"].lower()
        ),
        "answer_scope": (
            dashboard["answer_benchmark"]["case_count"] == answer_case_count
            and dashboard["answer_benchmark"]["automated_mean_pass_rate_pct"] == percent(answers["automated_mean_pass_rate"], 0)
            and dashboard["answer_benchmark"]["expert_validation_complete"] == answers["expert_validation_complete"]
            and dashboard["headline"]["expert_validation_complete"] == answers["expert_validation_complete"]
            and cards["answers"]["value"] == f"{answer_passed_count}/{answer_case_count}"
            and cards["answers"]["status"] == expected_answer_status
        ),
        "answer_showcase_source_fidelity": (
            showcase_source_fidelity
            and dashboard.get("answer_benchmark", {}).get("all_cases") == expected_all_cases
        ),
        "latency_and_fast_path": (
            dashboard["latency"]["sample_size"] == latency["sample_size"]
            and dashboard["latency"]["cold_uncached"] == latency["cold_uncached"]
            and dashboard["latency"]["cached_repeat"] == latency["cached_repeat"]
            and dashboard["latency"]["fast_path"]["case_count"] == fast_paths["case_count"]
            and dashboard["latency"]["fast_path"]["passed"] == fast_paths["passed"]
            and dashboard["latency"]["fast_path"]["max_total_s"] == fast_paths["max_total_s"]
            and dashboard["latency"]["fast_path"]["cases"] == fast_paths["cases"]
            and cards["latency"]["status"] == "partial"
        ),
        "compliance_scope": (
            dashboard["compliance"].get("window_days") == compliance.get("window_days")
            and dashboard["compliance"].get("patterns") == compliance.get("patterns")
            and dashboard["compliance"].get("accuracy_scope")
            == compliance_accuracy.get("scope_note")
            and is1786_dashboard == expected_is1786_dashboard
            and compliance_sources_reconcile
            and dashboard["compliance"]["is1786"]["deviation_cohort_n"] == is1786["deviation_cohort_n"]
            and dashboard["compliance"]["is1786"]["failure_linked_n"] == is1786["failure_linked_n"]
            and dashboard["compliance"]["is1786"]["downstream_n"] == is1786["preceded_failure_within_30d_n"]
            and dashboard["compliance"]["is1786"]["top_root_cause_n"] == is1786_detail["most_common_root_cause_n"]
            and dashboard["compliance"]["accuracy"] == compliance_accuracy["overall"]
            and f"{correct_temporal}/{compliance_accuracy['overall']['n']} locked temporal labels matched" in cards["compliance"]["detail"]
            and cards["compliance"]["status"] == ("scoped_verified" if compliance_passed else "partial")
        ),
        "card_source_claims": card_source_claims,
        "provenance_scope": (
            dashboard["provenance"]["real_csv_file_count"] == provenance["real_csv_file_count"]
            and dashboard["provenance"]["unique_real_payload_count"]
            == len({row["sha256"] for row in provenance["files"]})
            and dashboard_datasets["Steel Plates Faults"]["rows"] == named_sources["Steel Plates Faults"]["rows"]
            and dashboard_datasets["Steel Industry Energy Consumption"]["rows"] == energy_rows
            and dashboard_datasets["Steel Plates Faults"]["status"] == "locally_designated_real_source"
            and dashboard_datasets["Steel Industry Energy Consumption"]["status"] == "locally_designated_real_source"
            and named_sources["Steel Plates Faults"]["external_provenance_verified"] is False
            and named_sources["Steel Industry Energy Consumption"]["external_provenance_verified"] is False
        ),
        "artifact_coverage": (
            required_artifacts.issubset(listed_artifacts)
            and all((ROOT / row["file"]).exists() for row in dashboard.get("artifacts", []))
        ),
    }
    serialized = json.dumps(dashboard).lower()
    prohibited_claims = {
        "domain-expert validated": "domain-expert validated" in serialized,
        "17 relationship types": "17 relationship types" in serialized,
        "7 systems": "7 systems" in serialized,
        "validated on real plant documents": "validated on real plant documents" in serialized,
        "real plant document benchmark": "real plant document benchmark" in serialized,
        "real-source industrial datasets": "real-source industrial datasets" in serialized,
        "hours saved": "hours saved" in serialized,
    }
    passed = all(checks.values()) and not any(prohibited_claims.values())
    result = {
        "benchmark": "evaluation dashboard source fidelity",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "checks": checks,
        "prohibited_claims_present": prohibited_claims,
        "scope_note": "This validates committed dashboard claims against every consumed evidence artifact; it does not replace external expert review, upstream source verification or a user study.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
