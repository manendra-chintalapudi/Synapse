"""Build a human-review scorecard from the locked post-fix answer regression."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / "answer_quality_regression_results.json"
OUTPUT = HERE / "domain_expert_scorecard.md"


def run() -> str:
    results = json.loads(INPUT.read_text(encoding="utf-8"))
    digest = hashlib.sha256(INPUT.read_bytes()).hexdigest()
    lines = [
        "# Synapse domain-expert answer scorecard",
        "",
        "This scorecard freezes the exact post-fix answers in "
        f"`answer_quality_regression_results.json` (SHA-256 `{digest}`).",
        "",
        "## Reviewer and scoring instructions",
        "",
        "Reviewer name / identifier: ____________________  Role: ____________________",
        "",
        "Review date: ____________________  Relevant plant/domain experience: ____________________",
        "",
        "Score each dimension from 1 to 5: **1 = unsafe or materially wrong**, "
        "**3 = usable with correction**, **5 = correct, traceable and immediately actionable**. "
        "Mark `critical error = yes` if acting on the answer could cause a safety, quality or compliance failure.",
        "",
    ]
    for index, case in enumerate(results["cases"], start=1):
        response = case["response"]
        lines.extend([
            f"## Case {index}: `{case['id']}`",
            "",
            f"**Question:** {case['question']}",
            "",
            f"**Locked ground-truth reference:** `{case['ground_truth']}`",
            "",
            "### Synapse answer under review",
            "",
            response["answer"],
            "",
            "### Reviewer scores",
            "",
            "| Dimension | Score (1–5) | Reviewer note |",
            "|---|---:|---|",
            "| Factual correctness |  |  |",
            "| Evidence traceability |  |  |",
            "| Operational usefulness |  |  |",
            "| Role/action appropriateness |  |  |",
            "| Confidence calibration |  |  |",
            "",
            "Critical error (yes/no): ________",
            "",
            "Required correction or missing evidence: ________________________________________________",
            "",
        ])
    lines.extend([
        "## Overall decision",
        "",
        "Approved for demo (yes/no): ________",
        "",
        "Reviewer signature / acknowledgement: ____________________",
        "",
        "A review is considered complete only when every score is present, no critical-error field is blank, "
        "and the reviewer identity/role/date are recorded. Automated regression scores must not be substituted "
        "for this human assessment.",
        "",
    ])
    text = "\n".join(lines)
    OUTPUT.write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    run()
    print(f"wrote {OUTPUT}")
