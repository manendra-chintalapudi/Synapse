# Synapse evaluation evidence

This directory contains reproducible evaluation artifacts for the hackathon criteria.
Metrics must be generated from scripts and committed result files; presentation claims must
not exceed the scope stated by the corresponding benchmark.

## Entity extraction

Run:

```bash
python evaluation/entity_extraction_benchmark.py
```

The benchmark uses a locked 25-document synthetic/demo sample: 9 equipment manuals, 8 SOPs and
8 deviation reports. Its ontology-assisted label manifest is locked in
`entity_extraction_gold.json`; independent annotator-agreement and adjudication records are not
available. Predictions use the same explicit-ID candidate extractor as the production Tier-1
router (`router/canonical_ids.py`). It measures explicit canonical IDs and stale-ID rejection.
It does **not** measure implicit or name-only NER and is not evidence of performance on real plant
documents.

Candidate IDs are resolved against the locked ontology. Unknown references are retained in the
per-document result as `rejected_unknown_candidates`, making stale document references auditable
without allowing them to become extracted plant entities.

Run the separate production-path contract after router changes:

```bash
python evaluation/canonical_id_runtime_regression.py
```

This exercises the shared candidate parser through the production entity index and Tier-1
matcher for all 11 ontology ID types, lowercase normalization and valid-looking stale IDs. It is
a deterministic runtime contract, not a broader document-NER or answer-quality benchmark.

## Knowledge graph structural integrity

Run:

```bash
python evaluation/graph_completeness_audit.py
```

The audit verifies node/edge totals, primary-key uniqueness, relationship uniqueness, endpoint
existence and conformance to every allowed directed pair in the locked ontology schema.

With Neo4j credentials available, compare the deployed graph to the locked ontology:

```bash
python evaluation/live_graph_parity.py
```

This verifies deployed totals, label and relationship distributions, and primary-ID uniqueness.
Semantic equality of every property is deliberately outside that parity check.

## Domain-expert answer quality

Run the reproducible offline evidence regression:

```bash
python evaluation/answer_quality_regression.py
```

This verifies eleven deterministic answers against exact locked evidence and the six automated
contract checks. It covers the three golden paths, common count/ranking/compliance questions,
an IS:1786 temporal pattern, a full Deviation-to-RCA chain and an explicit causality/synthetic-
evidence boundary check. It does not measure public availability or latency.

Run the three golden-path questions against a deployment:

```bash
set SYNAPSE_BENCHMARK_TOKEN=<short-lived Supabase access token>
python evaluation/answer_quality_benchmark.py --base-url https://your-synapse.example
```

The automated rubric checks factual anchors, citations, the four-layer synthesis contract and
execution health. It does not masquerade as expert validation: factual correctness and
operational usefulness remain explicitly `pending` until a domain expert supplies 1–5 scores.

Generate the frozen human-review packet:

```bash
python evaluation/build_domain_expert_scorecard.py
```

The resulting `domain_expert_scorecard.md` includes the exact current answers, locked
ground-truth references, anchored five-dimension scoring and critical-error checks. A reviewer
must complete every field before Synapse may claim domain-expert validation.

## Compliance-to-failure patterns

Run:

```bash
python evaluation/compliance_failure_patterns.py
```

This reports 30-day directional timing patterns for IS:1786, IS:2062 and ASTM A370
deviation cohorts, with explicit sample sizes and Wilson 95% confidence intervals. These are
descriptive linkage metrics—not causal claims. Temporal date-rule agreement is reported
separately against the locked date-labelled sample below.

Run the balanced temporal-linkage accuracy test:

```bash
python evaluation/compliance_detection_accuracy.py
```

The locked date-labelled sample contains 30 linked events (15 within-window and 15 outside-window),
balanced across IS 2062, ASTM A370 and IS 1786. It measures agreement with the directional 30-day
date rule only; it is not a general compliance-gap classifier and is not evidence that a deviation
caused a failure. Independent annotation-agreement metadata is not available.

## Data provenance

Run:

```bash
python evaluation/data_provenance_audit.py
```

This inventories every CSV under a `real_data` directory with row counts and SHA-256 hashes and
detects duplicate files. It identifies two named, locally designated source dataset families:
Steel Plates Faults and Steel Industry Energy Consumption. That designation is repository metadata,
not independent upstream verification: the repository does not yet pin upstream URLs, licenses,
citations or expected source hashes for either family. AI4I 2020 is ingested as an official UCI
synthetic reference (10,000 rows, CC BY 4.0, DOI 10.24432/C5HS5C) and is never described as real
plant measurements.

## Time to answer

Run:

```bash
set SYNAPSE_BENCHMARK_TOKEN=<short-lived Supabase access token>
python evaluation/latency_benchmark.py --base-url https://your-synapse.example
```

This measures public wall-clock latency for simple graph, document QA and deep RCA questions,
then immediately repeats each query to measure the bounded in-process cache. The sample is
deliberately labelled `n=3`; it is not presented as a controlled manual-work comparison.

Run the routine deterministic fast-path check separately:

```bash
python evaluation/deterministic_fastpath_benchmark.py
```

It verifies that five frequent count, ranking and compliance questions produce cited answers
with `synthesis_s = 0` and without an OpenRouter call. Answer correctness remains gated by the
expanded deterministic answer-quality regression above.

The committed `latency_results.json` records an authenticated production-UI run. Its values are
the server latency displayed by the response panel (routing + retrieval + synthesis), not browser
rendering or network transit. Cache-busting benchmark prefixes ensured the first pass was uncached;
the exact same prompts were then repeated to verify the application cache.

## Evaluation dashboard data

Run after any benchmark changes:

```bash
python evaluation/build_dashboard_data.py
```

This creates `frontend/assets/evaluation_data.json`, a browser-safe summary with explicit
verified, baseline and pending statuses. It contains no secrets or raw industrial records.

Then validate the generated dashboard contract:

```bash
python evaluation/evaluation_dashboard_validation.py
```

The validator requires exactly six criteria, reconciles the headline counts, checks graph and
live-parity evidence, and rejects known overclaims such as calling AI4I real plant data or
describing 17 schema pairs as 17 implemented relationship names. The Evaluation Lab renders this
artifact with reusable React, Radix, Motion, Recharts and Lucide components without making LLM
calls.

## RCA & Failures browser

At the time of inspection, the deployed Neo4j density precheck reported 200 failures, 200 linked
RCAs and 200 linked technicians. These aggregate counts are operational context, not a committed
benchmark; the dedicated artifact below validates a three-failure sample. The literal
`RCA-[:FOLLOWS_PROCEDURE]->Procedure` count in that precheck was zero because the locked ontology
models procedure linkage from Equipment. Where a matching procedure is available, the UI resolves
it through `Failure <-[:EXPERIENCED]- Equipment -[:FOLLOWS_PROCEDURE]-> Procedure`, selected by the
RCA's `procedure_ref`, and labels this path explicitly rather than inventing an RCA edge.

Validate the detail projection against independent direct Cypher with:

```bash
python evaluation/rca_failure_validation.py
```

The committed result checks `F1114`, `F1019` and `F1186`, including equipment, RCA, technician,
procedure, deviation, quality-test, standard and document cardinalities. The page and endpoints
are read-only and never call the LLM synthesizer.

## Compliance browser

The Compliance browser can display a live global enrichment precheck, but this README does not
treat those aggregate totals as validated because no dedicated committed artifact currently
reconciles them. The committed evidence below is deliberately scoped to the IS:1786 family. Its
30-day timing statistic is a directional association, not a causal claim.

Validate the highest-deviation family projection with:

```bash
python evaluation/compliance_validation.py
```

The committed result independently checks IS:1786 at 338 cohort deviations, 171 failure-linked,
15 downstream within 30 days and mechanical overstrain as the top linked RCA cause (8/15). It also
checks three representative Deviation → Coil → Equipment → Failure → RCA graph-record chains and
the frontend navigation contract that jumps from Compliance to the corresponding RCA detail. All
Compliance endpoints are authenticated, cached read-only Cypher and never invoke the synthesizer.
