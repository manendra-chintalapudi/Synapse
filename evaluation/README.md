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
reports. It measures extraction of explicit canonical plant identifiers against the full ID
inventory in the locked ontology. It does **not** measure implicit or name-only NER; that will
require a separately human-annotated corpus.

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
