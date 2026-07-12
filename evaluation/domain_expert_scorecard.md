# Synapse domain-expert answer scorecard

This scorecard freezes the exact post-fix answers in `answer_quality_regression_results.json` (SHA-256 `fcc69dfe4e3d227c2225d5658c69d192a3290f7b7aeb5600a08fc48625156f53`).

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
- [Graph: EXPERIENCED -> DIAGNOSED_BY; RCA.procedure_ref -> Procedure] F1186, RCA1186, PROC-022.
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

## Overall decision

Approved for demo (yes/no): ________

Reviewer signature / acknowledgement: ____________________

A review is considered complete only when every score is present, no critical-error field is blank, and the reviewer identity/role/date are recorded. Automated regression scores must not be substituted for this human assessment.
