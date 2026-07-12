# Synapse evaluation evidence

This directory contains reproducible evaluation artifacts for the hackathon criteria.
Metrics must be generated from scripts and committed result files; presentation claims must
not exceed the scope stated by the corresponding benchmark.

## Entity extraction

Run:

```bash
python evaluation/entity_extraction_benchmark.py
```

The benchmark uses a locked 25-document sample: 9 equipment manuals, 8 SOPs and 8 deviation
reports. Gold labels are locked in `entity_extraction_gold.json` after two-pass reviewer
annotation and ontology-membership review. It measures explicit canonical IDs and stale-ID
rejection. It does **not** measure implicit or name-only NER.

Candidate IDs are resolved against the locked ontology. Unknown references are retained in the
per-document result as `rejected_unknown_candidates`, making stale document references auditable
without allowing them to become extracted plant entities.

## Knowledge graph completeness

Run:

```bash
python evaluation/graph_completeness_audit.py
```

The audit verifies node/edge totals, primary-key uniqueness, relationship uniqueness, endpoint
existence and conformance to every allowed directed pair in the locked ontology schema.

## Domain-expert answer quality

Run the reproducible offline evidence regression:

```bash
python evaluation/answer_quality_regression.py
```

This verifies the three golden answers against exact locked evidence and the six automated
contract checks. It does not measure public availability or latency.

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
descriptive linkage metrics—not causal claims. Temporal-linkage classification accuracy is
reported separately against the locked reviewer-labelled sample below.

Run the balanced temporal-linkage accuracy test:

```bash
python evaluation/compliance_detection_accuracy.py
```

The locked reviewer sample contains 30 linked events (15 within-window and 15 outside-window),
balanced across IS 2062, ASTM A370 and IS 1786. This measures correct directional 30-day
classification only; it is not evidence that a deviation caused a failure.

## Data provenance

Run:

```bash
python evaluation/data_provenance_audit.py
```

This inventories every CSV under a `real_data` directory with row counts and SHA-256 hashes,
detects duplicate files, and enforces honest named-dataset claims. AI4I 2020 is ingested as an
official UCI synthetic reference (10,000 rows, CC BY 4.0, DOI 10.24432/C5HS5C), kept separate
from real-source directories and never described as real plant measurements.

## Time to answer

Run:

```bash
set SYNAPSE_BENCHMARK_TOKEN=<short-lived Supabase access token>
python evaluation/latency_benchmark.py --base-url https://your-synapse.example
```

This measures public wall-clock latency for simple graph, document QA and deep RCA questions,
then immediately repeats each query to measure the bounded in-process cache. The sample is
deliberately labelled `n=3`; it is not presented as a controlled manual-work comparison.

## Evaluation dashboard data

Run after any benchmark changes:

```bash
python evaluation/build_dashboard_data.py
```

This creates `frontend/assets/evaluation_data.json`, a browser-safe summary with explicit
verified, baseline and pending statuses. It contains no secrets or raw industrial records.
