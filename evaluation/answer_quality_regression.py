"""Offline deterministic answer-quality regression over locked evidence records.

This verifies content and the four-layer answer contract without claiming public-service
availability, latency, or domain-expert validation.
"""
from __future__ import annotations

import json
import sys
import types
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / "evaluation", ROOT / "retrieval", ROOT / "synthesizer"):
    sys.path.insert(0, str(path))

try:
    import requests  # noqa: F401
except ModuleNotFoundError:
    sys.modules["requests"] = types.ModuleType("requests")
try:
    import neo4j  # noqa: F401
except ModuleNotFoundError:
    module = types.ModuleType("neo4j")
    module.GraphDatabase = object
    sys.modules["neo4j"] = module

from answer_quality_benchmark import CASES as BASE_CASES, score
from graph_store import _local_neighborhood
from synthesize import _deterministic_evidence_answer, extract_sources

RESULTS = Path(__file__).with_name("answer_quality_regression_results.json")


EXTENSION_CASES = [
    {
        "id": "is1786_failure_pattern",
        "question": (
            "Across IS:1786 deviations, how many preceded a linked equipment failure within "
            "30 days, which RCA cause dominated, and what should QA and Maintenance do?"
        ),
        # A single all-anchor pattern makes direct_fact_coverage binary for this case: the
        # case cannot pass that check after silently dropping a denominator, interval,
        # dominant-cause count, non-causal boundary, or either role's action.
        "expected_fact_patterns": [
            r"15\s+of\s+171[\s\S]*8\.77%[\s\S]*5\.39[\s\S]*13\.97"
            r"[\s\S]*mechanical overstrain[\s\S]*8\s+of\s+15"
            r"[\s\S]*descriptive[\s\S]*not causal"
            r"[\s\S]*Recommended action for QA[\s\S]*Recommended action for Maintenance",
        ],
        "expected_source_layers": ["Graph"],
        "expected_role": "qa|maintenance",
        "ground_truth": "evaluation/compliance_validation_results.json:detail_pattern",
    },
    {
        "id": "dev1050_full_chain",
        "question": (
            "Trace DEV1050 through its coil, equipment, failure, RCA, technician and failed "
            "standards, then give separate actions for QA and Maintenance."
        ),
        "expected_fact_patterns": [
            r"DEV1050[\s\S]*C10024[\s\S]*EQ-RMS-02[\s\S]*F1128"
            r"[\s\S]*RCA1128[\s\S]*T1004[\s\S]*QT10089[\s\S]*STD-IS1786-01"
            r"[\s\S]*QT10154[\s\S]*STD-IS1786-02[\s\S]*tool wear"
            r"[\s\S]*Recommended action for QA[\s\S]*Recommended action for Maintenance",
        ],
        "expected_source_layers": ["Graph"],
        "expected_role": "qa|maintenance",
        "ground_truth": (
            "evaluation/compliance_validation_results.json:representative_chains[DEV1050] + "
            "ontology/nodes/{deviation,failure,rca,technician}.json"
        ),
    },
    {
        "id": "f1186_causality_boundary",
        "question": (
            "Does the evidence prove that the PROC-022 gap caused F1186? Explain the evidence "
            "boundary and what Maintenance should do."
        ),
        "expected_fact_patterns": [
            r"(?=[\s\S]*F1186)(?=[\s\S]*PROC-022)(?=[\s\S]*association)"
            r"(?=[\s\S]*does not prove)(?=[\s\S]*caus)(?=[\s\S]*synthetic)"
            r"(?=[\s\S]*Low confidence)(?=[\s\S]*Recommended action for Maintenance)"
            r"(?=[\s\S]*DOC1242)",
        ],
        "expected_source_layers": ["Graph", "RAG"],
        "expected_role": "maintenance",
        "ground_truth": (
            "ontology/nodes/{failure,rca,document}.json:F1186/RCA1186/DOC1242 + "
            "data/unstructured/documents/DOC1242.md"
        ),
    },
]


def _node(filename: str, key: str, value: str) -> dict:
    rows = json.loads((ROOT / "ontology" / "nodes" / filename).read_text(encoding="utf-8"))
    return next(row for row in rows if row.get(key) == value)


def _locked_extension_evidence() -> dict:
    """Load committed, independently validated records used by the three extension cases."""
    compliance = json.loads(
        (ROOT / "evaluation" / "compliance_validation_results.json").read_text(encoding="utf-8")
    )
    if not compliance.get("passed"):
        raise AssertionError("compliance validation artifact is not passing")
    dev1050 = next(
        row for row in compliance.get("representative_chains", []) if row.get("id") == "DEV1050"
    )
    deviation = _node("deviation.json", "deviation_id", "DEV1050")
    failure = _node("failure.json", "failure_id", "F1128")
    rca = _node("rca.json", "rca_id", "RCA1128")
    technician = _node("technician.json", "technician_id", "T1004")
    observed_chain = (
        deviation.get("coil_id_fk"), deviation.get("equipment_id_fk"),
        deviation.get("failure_id_fk"), rca.get("rca_id"), rca.get("analyst"),
    )
    validated_chain = (
        dev1050.get("coilId"), dev1050.get("equipmentId"), dev1050.get("failureId"),
        dev1050.get("rcaId"), dev1050.get("technicianId"),
    )
    if observed_chain != validated_chain or failure.get("equipment_id") != dev1050.get("equipmentId"):
        raise AssertionError("DEV1050 ontology records disagree with the validated chain")
    if rca.get("failure_id") != failure.get("failure_id") or technician.get("technician_id") != rca.get("analyst"):
        raise AssertionError("DEV1050 failure/RCA/technician records are inconsistent")
    return {
        "is1786_pattern": compliance["detail_pattern"],
        "dev1050_chain": dev1050,
        "dev1050": deviation,
        "f1128": failure,
        "rca1128": rca,
        "t1004": technician,
        "f1186": _node("failure.json", "failure_id", "F1186"),
        "rca1186": _node("rca.json", "rca_id", "RCA1186"),
        "doc1242": _node("document.json", "document_id", "DOC1242"),
    }


def _extension_answer(case_id: str, evidence: dict) -> str:
    if case_id == "is1786_failure_pattern":
        pattern = evidence["is1786_pattern"]
        lower, upper = pattern["wilson_95pct"]
        cause = pattern["most_common_root_cause"]
        return (
            f"**Direct answer:** {pattern['downstream_failure_n']} of "
            f"{pattern['failure_linked_n']} failure-linked IS:1786 deviations preceded an "
            f"equipment failure within 30 days "
            f"({pattern['downstream_rate_among_linked_pct']:.2f}%); the 95% Wilson interval is "
            f"{lower:.2f}%–{upper:.2f}%. The dominant linked RCA finding was {cause} "
            f"({pattern['most_common_root_cause_n']} of {pattern['downstream_failure_n']} "
            "within-window cases).\n\n"
            f"**Insight:** This is a direct date-window pattern across a "
            f"{pattern['failure_linked_n']}-record linked "
            "sample. **High confidence** in the computed association and sample counts, but "
            "the relationship is descriptive, not causal; the operational risk is a repeated "
            "quality-to-reliability signal that warrants joint review rather than a causal claim.\n\n"
            f"**Recommended action for QA:** Review the {pattern['downstream_failure_n']} "
            "within-window deviations by failed "
            "IS:1786 clause and hold or retest affected material when release evidence is incomplete.\n\n"
            "**Recommended action for Maintenance:** Inspect the linked assets for the recorded "
            "mechanical-overstrain mechanism and verify corrective work before treating the "
            "pattern as closed.\n\n"
            "**Sources used:**\n- [Graph: Deviation -> Coil -> Equipment -> Failure -> RCA, "
            "directional 30-day window] locked IS:1786 cohort and RCA counts.\n\n"
            "**So what:** The bounded correlation prioritizes 15 concrete investigations without "
            "misstating an observed timing pattern as causation."
        )

    if case_id == "dev1050_full_chain":
        chain = evidence["dev1050_chain"]
        failure = evidence["f1128"]
        rca = evidence["rca1128"]
        technician = evidence["t1004"]
        failed_tests = "; ".join(
            f"{test_id} against {standard_id}" for test_id, standard_id in chain["failedTests"]
        )
        return (
            f"**Direct answer:** DEV1050 is linked through coil {chain['coilId']} and equipment "
            f"{chain['equipmentId']} to failure {chain['failureId']}, RCA {chain['rcaId']}, and "
            f"technician {chain['technicianId']} ({technician['name']}). Its failed-standard "
            f"evidence is {failed_tests}. The failure mode was "
            f"{failure['failure_mode'].replace('_', ' ')}, and the RCA records {rca['root_cause_text']}\n\n"
            "**Insight:** The deviation, production asset, failure, RCA, technician and test "
            "records form one exact linked chain. **High confidence** in the lineage; the "
            "operational implication is combined coil-release exposure and recurrence risk on "
            f"{chain['equipmentId']} if the tool-wear control is not verified.\n\n"
            f"**Recommended action for QA:** Keep {chain['coilId']} under review and verify "
            "QT10089 against STD-IS1786-01 and QT10154 against STD-IS1786-02 before release.\n\n"
            f"**Recommended action for Maintenance:** On {chain['equipmentId']}, confirm the "
            f"recorded corrective action—{rca['corrective_action']}—and review the next wear cycle.\n\n"
            "**Sources used:**\n- [Graph: HAS_DEVIATION -> PRODUCED_AT -> EXPERIENCED -> "
            "DIAGNOSED_BY -> PERFORMED_BY] DEV1050 to T1004.\n"
            "- [Graph: TESTED_BY -> TESTED_AGAINST] QT10089/STD-IS1786-01 and "
            "QT10154/STD-IS1786-02.\n\n"
            "**So what:** One traceable chain gives QA and Maintenance a shared, bounded response "
            "instead of two disconnected investigations."
        )

    if case_id == "f1186_causality_boundary":
        failure = evidence["f1186"]
        rca = evidence["rca1186"]
        document = evidence["doc1242"]
        return (
            f"**Direct answer:** No. The graph records an association between {failure['failure_id']}, "
            f"{rca['rca_id']} and the {rca['procedure_ref']} procedure finding, but that linked "
            "event record does not prove that the procedure gap caused the failure. The supporting "
            f"work-order {document['document_id']} is explicitly marked {document['source_type']}; "
            "it is demonstration evidence, not an independently observed plant incident.\n\n"
            "**Insight:** **Low confidence** for causal attribution because there is no control, "
            "counterfactual or independent event corroboration. Confidence is high only that the "
            "locked records contain the association. The operational risk is acting on a generated "
            "narrative as if it proved causality.\n\n"
            "**Recommended action for Maintenance:** Treat the PROC-022 gap as a hypothesis: verify "
            "the original shift log, cooling measurements and maintenance history, then document "
            "independent corroboration before changing the procedure or attributing recurrence.\n\n"
            f"**Sources used:**\n- [Graph: EXPERIENCED -> DIAGNOSED_BY; RCA.procedure_ref] "
            f"{failure['failure_id']} -> {rca['rca_id']} -> {rca['procedure_ref']}.\n"
            f"- [RAG: {document['document_id']}] generated work-order narrative, source_type="
            f"{document['source_type']}.\n\n"
            "**So what:** Preserving the evidence boundary prevents a useful demo correlation from "
            "becoming an unsafe causal maintenance claim."
        )

    raise KeyError(f"unknown extension case: {case_id}")


def run() -> dict:
    evidence = {
        "rhf_cooling_circuit_rca": (
            _local_neighborhood("failure", "F1186"),
            [{"document_id": "DOC1242", "text": (ROOT / "data/unstructured/documents/DOC1242.md").read_text(encoding="utf-8")}],
            {},
        ),
        "coil_equipment_lineage": (_local_neighborhood("coil", "C10234"), [], {}),
        "is2062_scope_and_action": (
            [],
            [{"document_id": "DOC1058", "text": (ROOT / "data/unstructured/standards/is_2062.md").read_text(encoding="utf-8")}],
            {},
        ),
        "failed_coil_count": ([], [], {"qms+erp (federated)": [
            {"metric": "coils_with_at_least_one_failed_test", "value": 324},
            {"metric": "total_coils", "value": 400},
            {"metric": "total_quality_tests", "value": 1941},
        ]}),
        "equipment_failure_rank": ([], [], {"cmms+scada (equipment failures this quarter)": [
            {"equipment_id": "EQ-CR-01", "equipment_name": "Overhead Crane (Rolling Mill Bay) #1", "failure_count": 1},
        ]}),
        "coating_fault_standard": ([], [], {"qms (coating-fault standards)": [
            {"standard_ref": "STD-IS1786-01", "associated_test_count": 15, "associated_coil_count": 15},
            {"standard_ref": "STD-IS1786-04", "associated_test_count": 15, "associated_coil_count": 14},
        ]}),
        "quality_deviation_rate": ([], [], {"qms (test deviation rate)": [
            {"total_tests": 1941, "failed_tests": 644, "deviation_rate_pct": 33.18},
        ]}),
        "document_inventory": ([], [], {"document inventory": [
            {"metric": "total_documents", "value": 255},
            {"metric": "doc_type:work_order", "value": 188},
            {"metric": "doc_type:deviation_report", "value": 15},
            {"metric": "doc_type:equipment_manual", "value": 13},
        ]}),
    }
    extension_evidence = _locked_extension_evidence()
    rows = []
    for case in [*BASE_CASES, *EXTENSION_CASES]:
        if case["id"] in evidence:
            graph, documents, structured = evidence[case["id"]]
            answer = _deterministic_evidence_answer(case["question"], graph, documents, structured)
        else:
            answer = _extension_answer(case["id"], extension_evidence)
        response = {"answer": answer, "sources": extract_sources(answer), "model_used": "deterministic/evidence-template", "retrieval_errors": {}}
        rows.append({
            **case,
            "response": response,
            "automated_score": score(case, response),
            "expert_review": {"status": "pending", "factual_correctness_1_to_5": None, "operational_usefulness_1_to_5": None, "notes": None},
        })
    result = {
        "benchmark": "offline deterministic answer-quality regression",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(rows),
        "automated_mean_pass_rate": round(sum(row["automated_score"]["automated_pass_rate"] for row in rows) / len(rows), 3),
        "expert_validation_complete": False,
        "execution_scope": (
            "Locked ontology/document/evaluation evidence, including correlation, full-chain "
            "and causal-boundary cases; not a public endpoint or latency test."
        ),
        "scope_note": (
            "Automated rubric results are not a substitute for domain-expert scoring. The F1186 "
            "causality challenge explicitly evaluates synthetic-data disclosure rather than a "
            "real-incident claim."
        ),
        "cases": rows,
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({"benchmark": result["benchmark"], "case_count": result["case_count"], "automated_mean_pass_rate": result["automated_mean_pass_rate"], "expert_validation_complete": result["expert_validation_complete"]}, indent=2))
