# Synapse domain-expert answer scorecard

This scorecard freezes the exact post-fix answers in `answer_quality_regression_results.json` (SHA-256 `a7628988f07a41b7a99160f2244c99f06bad8c8170dad339efefbe8dd02dd79d`).

## Reviewer and scoring instructions

Reviewer name / identifier: ____________________  Role: ____________________

Review date: ____________________  Relevant plant/domain experience: ____________________

Score each dimension from 1 to 5: **1 = unsafe or materially wrong**, **3 = usable with correction**, **5 = correct, traceable and immediately actionable**. Mark `critical error = yes` if acting on the answer could cause a safety, quality or compliance failure.

## Case 1: `rhf_cooling_circuit_rca`

**Question:** What caused failure F1186, what procedure gap contributed, and what should Maintenance do next?

**Locked ground-truth reference:** `ontology/nodes/failure.json:F1186 + ontology/nodes/rca.json:RCA1186`

### Synapse answer under review

**Direct answer:** F1186 on Reheating Furnace #1 (EQ-RHF-01) was diagnosed by RCA1186. The recorded root cause was insufficient heat dissipation: cooling airflow and coolant flow were below the required rate while process temperature rose relative to ambient, exceeding the tool's thermal limit. Contributing factors included clogged cooling passages and degraded coolant. The linked procedure finding was PROC-022: Step 4 of PROC-022 ("Record final temperatures and any anomalies in the shift log.") — cooling/lubrication verification was not completed at the required interval before the event.

**Insight:** The failure, RCA, procedure finding and corrective work are linked by exact IDs across the audited graph and its work-order document. **High confidence**: this is a direct event chain, not a statistical inference. The operational risk is recurrence of the same heat dissipation failure if the recorded procedure gap remains open.

**Recommended action for Maintenance:** The recorded corrective work was: Cleaned and restored cooling circuit, replaced coolant, and added a temperature-differential alarm to the monitoring system. Confirm that this work and the cited PROC-022 step are complete and documented, validate the repair under normal load, and review the next operating cycle before returning the asset to unrestricted service.

**Sources used:**
- [Graph: EXPERIENCED -> DIAGNOSED_BY -> PROCEDURE_REVIEWED] F1186, RCA1186, PROC-022.
- [RAG: DOC1242] exact linked work-order narrative.

**So what:** Closing the recorded procedure gap reduces repeat downtime and makes the repair auditable.

### Reviewer scores

| Dimension | Score (1–5) | Reviewer note |
|---|---:|---|
| Factual correctness |  |  |
| Evidence traceability |  |  |
| Operational usefulness |  |  |
| Role/action appropriateness |  |  |
| Confidence calibration |  |  |

Critical error (yes/no): ________

Required correction or missing evidence: ________________________________________________

## Case 2: `coil_equipment_lineage`

**Question:** Which equipment produced coil C10234, and what is the operational implication?

**Locked ground-truth reference:** `ontology/nodes/coil.json:C10234`

### Synapse answer under review

**Direct answer:** Coil C10234 was produced at EQ-FMS-01 (Finishing Mill Stand F1) through the `PRODUCED_AT` relationship.

**Insight:** This is an exact coil-to-equipment lineage link. The same neighborhood includes 1 deviation record(s). **Medium confidence** for operational implication: the lineage is definitive, but attributing any quality risk to the stand requires corroborating roll-condition and batch history.

**Recommended action for Operations:** Use EQ-FMS-01 as the starting asset for shift-log, setup and maintenance checks; have QA compare nearby coils before escalating to a line-wide hold.

**Sources used:**
- [Graph: Coil -[:PRODUCED_AT]-> Equipment] C10234 -> EQ-FMS-01.

**So what:** Exact lineage narrows a cross-system investigation to the responsible production asset in one step.

### Reviewer scores

| Dimension | Score (1–5) | Reviewer note |
|---|---:|---|
| Factual correctness |  |  |
| Evidence traceability |  |  |
| Operational usefulness |  |  |
| Role/action appropriateness |  |  |
| Confidence calibration |  |  |

Critical error (yes/no): ________

Required correction or missing evidence: ________________________________________________

## Case 3: `is2062_scope_and_action`

**Question:** What does IS 2062 cover, what risk does non-compliance create, and what should QA verify?

**Locked ground-truth reference:** `data/unstructured/standards/is_2062.md + DOC1058`

### Synapse answer under review

**Direct answer:** IS 2062 covers hot-rolled medium and high-tensile structural steel supplied as plates, strips, sections, flats and bars. It defines grade/sub-quality requirements covering manufacture, chemical composition, mechanical properties and testing [RAG: DOC1058].

**Insight:** Non-compliance creates a structural assurance risk: strength, ductility, weldability and toughness may not be demonstrated for the declared grade. **High confidence** on scope; exact numeric limits are intentionally omitted from this summary and must be checked in the licensed BIS text [RAG: DOC1058].

**Recommended action for QA:** Verify grade and sub-quality, heat/mill certificate traceability, chemical analysis, mechanical test results, dimensions and surface acceptance against the licensed current edition before release.

**Sources used:**
- [RAG: DOC1058] BIS IS 2062 scope and classification reference.

**So what:** A documented IS 2062 verification prevents structurally unsuitable material from moving into fabrication or dispatch.

### Reviewer scores

| Dimension | Score (1–5) | Reviewer note |
|---|---:|---|
| Factual correctness |  |  |
| Evidence traceability |  |  |
| Operational usefulness |  |  |
| Role/action appropriateness |  |  |
| Confidence calibration |  |  |

Critical error (yes/no): ________

Required correction or missing evidence: ________________________________________________

## Overall decision

Approved for demo (yes/no): ________

Reviewer signature / acknowledgement: ____________________

A review is considered complete only when every score is present, no critical-error field is blank, and the reviewer identity/role/date are recorded. Automated regression scores must not be substituted for this human assessment.
