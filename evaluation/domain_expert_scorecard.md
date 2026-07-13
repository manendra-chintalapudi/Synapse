# Synapse domain-expert answer scorecard

This scorecard freezes the exact post-fix answers in `answer_quality_regression_results.json` (SHA-256 `af6a2dab188602243930574e5376acd19f2b1cb9a74a76ab5928131277b0ed52`).

## Reviewer and scoring instructions

Reviewer name / identifier: ____________________  Role: ____________________

Review date: ____________________  Relevant plant/domain experience: ____________________

Score each dimension from 1 to 5: **1 = unsafe or materially wrong**, **3 = usable with correction**, **5 = correct, traceable and immediately actionable**. Mark `critical error = yes` if acting on the answer could cause a safety, quality or compliance failure.

## Case 1: `rhf_cooling_circuit_rca`

**Question:** What caused failure F1186, what procedure gap contributed, and what should Maintenance do next?

**Locked ground-truth reference:** `ontology/nodes/failure.json:F1186 + ontology/nodes/rca.json:RCA1186`

### Synapse answer under review

**Direct answer:** F1186 on Reheating Furnace #1 (EQ-RHF-01) has the recorded diagnosis RCA1186: insufficient heat dissipation: cooling airflow and coolant flow were below the required rate while process temperature rose relative to ambient, exceeding the tool's thermal limit. Contributing factors included clogged cooling passages and degraded coolant. The records associate that event with the PROC-022 procedure finding: Step 4 of PROC-022 ("Record final temperatures and any anomalies in the shift log.") — cooling/lubrication verification was not completed at the required interval before the event. This linked record does not prove that the procedure gap caused the failure.

**Insight:** The failure, RCA, procedure finding and corrective work are linked by exact IDs across the audited graph and its work-order document. **High confidence in the record lineage and recorded fields only.** **Low confidence for causal attribution**: one associated event chain has no control, counterfactual, or independent incident corroboration. The linked work-order narrative is explicitly synthetic/demo evidence, not an independently observed plant incident. The operational risk is treating a recorded association as proof about the heat dissipation failure.

**Recommended action for Maintenance:** Treat the recorded PROC-022 procedure gap as a hypothesis. Verify the original shift log, cooling-airflow and coolant-flow measurements, and maintenance history independently. The recorded corrective work was: Cleaned and restored cooling circuit, replaced coolant, and added a temperature-differential alarm to the monitoring system. Confirm and validate that work under normal load, but do not attribute recurrence or change the procedure until independent evidence corroborates the mechanism.

**Sources used:**
- [Graph: EXPERIENCED -> DIAGNOSED_BY; RCA.procedure_ref -> Procedure] F1186, RCA1186, PROC-022.
- [RAG: DOC1242] exact linked work-order narrative.

**So what:** If independent records corroborate the procedure gap, correcting it may reduce recurrence risk; the evidence here does not establish that effect.

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
- [Graph: PRODUCED_AT] C10234 -> EQ-FMS-01.

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

## Case 4: `failed_coil_count`

**Question:** How many coils failed quality testing?

**Locked ground-truth reference:** `qms.deviations.coil_id_fk + erp.coils.coil_id`

### Synapse answer under review

**Direct answer:** 324 of 400 coils have at least one recorded quality deviation (81.00%) [DFS: qms.deviations.coil_id_fk; erp.coils.coil_id].

**Insight:** The denominator is the full ERP coil population, while the numerator is distinct coil IDs in QMS deviations; 1941 quality tests provide the inspection context. **High confidence** because the counts are pre-aggregated from the source tables.

**Recommended action for QA:** Review the affected-coil list by severity and production equipment before deciding whether a targeted hold or a wider process check is required.

**Sources used:**
- [DFS: qms.deviations.coil_id_fk; erp.coils.coil_id] distinct failed-coil numerator and total-coil denominator.

**So what:** A denominator-backed rate lets QA size the real exposure without waiting for model synthesis.

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

## Case 5: `equipment_failure_rank`

**Question:** Which equipment failed most this quarter?

**Locked ground-truth reference:** `cmms.failures + scada.equipment current-quarter aggregate`

### Synapse answer under review

**Direct answer:** Overhead Crane (Rolling Mill Bay) #1 (EQ-CR-01) has the most recorded failures this quarter: 1 [DFS: cmms.failures.equipment_id; scada.equipment.name].

**Insight:** The leading equipment ranking is Overhead Crane (Rolling Mill Bay) #1 (1). **High confidence** for the ranking because it is a direct grouped count over the current-quarter CMMS records. The operational implication is concentrated downtime risk on the leading asset.

**Recommended action for Maintenance:** Start the reliability review with EQ-CR-01, then compare its recurring modes and open corrective work with the next two assets.

**Sources used:**
- [DFS: cmms.failures.equipment_id; scada.equipment.name] current-quarter failure counts.

**So what:** Focusing on the highest-frequency asset directs maintenance effort to the largest current downtime signal.

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

## Case 6: `coating_fault_standard`

**Question:** Which standard do coating faults violate?

**Locked ground-truth reference:** `qms.quality_tests.standard_ref + qms.deviations.coil_id_fk`

### Synapse answer under review

**Direct answer:** STD-IS1786-01 is the most frequently associated standard for coating-irregularity tests on coils with recorded deviations: 15 tests across 15 coils [DFS: qms.quality_tests.standard_ref; qms.deviations.coil_id_fk].

**Insight:** This is a shared-coil association, not a direct QualityTest-to-Deviation edge. **Medium confidence** for attribution: the standard ranking is exact, but an individual deviation cannot be assigned to one test without an explicit relationship. The compliance implication is a cohort-level clause risk, not proof that one test caused one deviation.

**Recommended action for QA:** Open the STD-IS1786-01 clause record, verify the affected coils and keep the attribution at cohort level unless the missing test-to-deviation link is added.

**Sources used:**
- [DFS: qms.quality_tests.standard_ref; qms.deviations.coil_id_fk] coating-test standard counts on deviation-bearing coils.

**So what:** The ranking identifies the first compliance clause to investigate while preserving the graph's attribution boundary.

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

## Case 7: `quality_deviation_rate`

**Question:** What is the quality-test deviation rate?

**Locked ground-truth reference:** `644 coil-linked deviations / 1,941 quality tests`

### Synapse answer under review

**Direct answer:** The quality-test deviation rate is 33.18%: 644 coil-linked deviations over 1941 quality tests [DFS: qms.deviations.coil_id_fk; qms.quality_tests.test_id].

**Insight:** The formula excludes equipment-only deviations from the test numerator, so the numerator and denominator describe the same quality-testing population. **High confidence** because both counts are direct aggregates. The quality-risk implication is that trend changes can be compared without denominator drift.

**Recommended action for QA:** Trend this rate by standard and equipment, then inspect any clause whose recent 90-day rate rises above its prior period.

**Sources used:**
- [DFS: qms.deviations.coil_id_fk; qms.quality_tests.test_id] matched compliance numerator and test denominator.

**So what:** A consistent denominator makes compliance trend changes actionable instead of anecdotal.

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

## Case 8: `document_inventory`

**Question:** How many documents are in the knowledge base?

**Locked ground-truth reference:** `ontology/nodes/document.json`

### Synapse answer under review

**Direct answer:** The knowledge base tracks 255 managed documents [DFS: document catalog.document_id].

**Insight:** The largest document groups are work_order: 188, deviation_report: 15, equipment_manual: 13. **High confidence** because this is a direct inventory count, not a semantic-search estimate. The retrieval-quality implication is that missing governed document types create evidence-coverage risk.

**Recommended action for Admin:** Review document types with low coverage and verify that current procedures, RCA reports and test certificates have vector references.

**Sources used:**
- [DFS: document catalog.document_id] managed-document inventory.

**So what:** Inventory coverage shows whether the retrieval layer has enough governed evidence to support plant decisions.

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

## Case 9: `is1786_failure_pattern`

**Question:** Across IS:1786 deviations, how many preceded a linked equipment failure within 30 days, which RCA cause dominated, and what should QA and Maintenance do?

**Locked ground-truth reference:** `evaluation/compliance_validation_results.json:detail_pattern`

### Synapse answer under review

**Direct answer:** 15 of 171 failure-linked IS:1786 deviations preceded an equipment failure within 30 days (8.77%); the 95% Wilson interval is 5.39%–13.97%. The dominant linked RCA finding was Root cause identified as mechanical overstrain: the product of tool wear and applied torque exceeded the overstrain threshold for the material variant being processed. Worn tooling combined with high torque demand drove the strain beyond safe limits. (8 of 15 within-window cases).

**Insight:** This is a direct date-window pattern across a 171-record linked sample. **High confidence** in the computed association and sample counts, but the relationship is descriptive, not causal; the operational risk is a repeated quality-to-reliability signal that warrants joint review rather than a causal claim.

**Recommended action for QA:** Review the 15 within-window deviations by failed IS:1786 clause and hold or retest affected material when release evidence is incomplete.

**Recommended action for Maintenance:** Inspect the linked assets for the recorded mechanical-overstrain mechanism and verify corrective work before treating the pattern as closed.

**Sources used:**
- [Graph: Deviation -> Coil -> Equipment -> Failure -> RCA, directional 30-day window] locked IS:1786 cohort and RCA counts.

**So what:** The bounded correlation prioritizes 15 concrete investigations without misstating an observed timing pattern as causation.

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

## Case 10: `dev1050_full_chain`

**Question:** Trace DEV1050 through its coil, equipment, failure, RCA, technician and failed standards, then give separate actions for QA and Maintenance.

**Locked ground-truth reference:** `evaluation/compliance_validation_results.json:representative_chains[DEV1050] + ontology/nodes/{deviation,failure,rca,technician}.json`

### Synapse answer under review

**Direct answer:** DEV1050 is linked through coil C10024 and equipment EQ-RMS-02 to failure F1128, RCA RCA1128, and technician T1004 (Shalini Naidu). Its failed-standard evidence is QT10089 against STD-IS1786-01; QT10154 against STD-IS1786-02. The failure mode was tool wear failure, and the RCA records Root cause was excessive tool wear: accumulated tool-wear minutes exceeded the qualified service life, degrading process capability and surface quality before scheduled replacement. Extended run time between changes was the main driver.

**Insight:** The deviation, production asset, failure, RCA, technician and test records form one exact linked chain. **High confidence** in the lineage; the operational implication is combined coil-release exposure and recurrence risk on EQ-RMS-02 if the tool-wear control is not verified.

**Recommended action for QA:** Keep C10024 under review and verify QT10089 against STD-IS1786-01 and QT10154 against STD-IS1786-02 before release.

**Recommended action for Maintenance:** On EQ-RMS-02, confirm the recorded corrective action—Replaced the worn tool and implemented tool-wear-based (rather than purely time-based) replacement scheduling.—and review the next wear cycle.

**Sources used:**
- [Graph: HAS_DEVIATION -> PRODUCED_AT -> EXPERIENCED -> DIAGNOSED_BY -> PERFORMED_BY] DEV1050 to T1004.
- [Graph: TESTED_BY -> TESTED_AGAINST] QT10089/STD-IS1786-01 and QT10154/STD-IS1786-02.

**So what:** One traceable chain gives QA and Maintenance a shared, bounded response instead of two disconnected investigations.

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

## Case 11: `f1186_causality_boundary`

**Question:** Does the evidence prove that the PROC-022 gap caused F1186? Explain the evidence boundary and what Maintenance should do.

**Locked ground-truth reference:** `ontology/nodes/{failure,rca,document}.json:F1186/RCA1186/DOC1242 + data/unstructured/documents/DOC1242.md`

### Synapse answer under review

**Direct answer:** No. The graph records an association between F1186, RCA1186 and the PROC-022 procedure finding, but that linked event record does not prove that the procedure gap caused the failure. The supporting work-order DOC1242 is explicitly marked synthetic; it is demonstration evidence, not an independently observed plant incident.

**Insight:** **Low confidence** for causal attribution because there is no control, counterfactual or independent event corroboration. Confidence is high only that the locked records contain the association. The operational risk is acting on a generated narrative as if it proved causality.

**Recommended action for Maintenance:** Treat the PROC-022 gap as a hypothesis: verify the original shift log, cooling measurements and maintenance history, then document independent corroboration before changing the procedure or attributing recurrence.

**Sources used:**
- [Graph: EXPERIENCED -> DIAGNOSED_BY; RCA.procedure_ref] F1186 -> RCA1186 -> PROC-022.
- [RAG: DOC1242] generated work-order narrative, source_type=synthetic.

**So what:** Preserving the evidence boundary prevents a useful demo correlation from becoming an unsafe causal maintenance claim.

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
