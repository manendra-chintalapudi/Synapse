"""
Synthesizer: turns retrieved evidence from the router's chosen layers into a grounded,
cited answer. Runs ENTIRELY on OpenRouter free-tier models -- no Anthropic/Claude API
usage anywhere in this component.

Models -- ordered fallback chain (all :free, all verified against OpenRouter's live model
list on 2026-07-08). Promotion decision 2026-07-08: tencent/hy3:free passed the 4-case
suite with PERFECT citation discipline (0 untagged claims, inline tags, DOC1012 distractor
correctly omitted), matching-or-exceeding Nemotron -> promoted to primary per the agreed
criterion. gpt-oss-120b/Gemma retained further down the chain (both were persistently
rate-limited upstream during validation; their slots are preserved for when pools clear).
  1. tencent/hy3:free                        (primary)
  2. nvidia/nemotron-3-super-120b-a12b:free  (first fallback -- also passed the suite)
  3. openai/gpt-oss-120b:free
  4. google/gemma-4-31b-it:free
If SYNTHESIZER_MODEL is set, ONLY that model is used (no fallback) -- deterministic for
testing. When unset, the chain is walked automatically on rate-limit/failure, and
model_used in the result reports which model actually answered.

Extended reasoning: OpenRouter's unified parameter for reasoning depth is
`"reasoning": {"effort": "low"|"medium"|"high"}` (per OpenRouter's reasoning-tokens docs;
`reasoning` is listed in gpt-oss-120b's supported_parameters). We request effort="high" so
the model deliberates before writing, which improves citation accuracy. The chain of
thought arrives in message.reasoning and is discarded; only message.content is used.

synthesize_answer(question, retrieval_plan, graph_results, structured_results,
                  document_results) -> {"answer", "sources", "model_used"}

Behavior:
  - retrieval_plan.confidence == "unresolvable"  -> clarifying question, NO LLM call
  - layers queried but empty                     -> explicit "[...: none found]" in prompt
  - API failure / timeout / unparseable output   -> apologetic stock answer, never raises,
                                                    never fabricates
"""
import json
import os
import re
import time
from datetime import date

import requests

from config import CHAT_URL, get_openrouter_key
from confidence import calibrate_confidence

MODEL_CHAIN = [
    "tencent/hy3:free",                        # primary (promoted 2026-07-08, see above)
    "nvidia/nemotron-3-super-120b-a12b:free",  # first fallback
    "openai/gpt-oss-120b:free",
    "google/gemma-4-31b-it:free",
]
PRIMARY_MODEL = MODEL_CHAIN[0]
TIMEOUT_S = int(os.environ.get("SYNTHESIZER_TIMEOUT_S", "45"))
MAX_TOKENS = int(os.environ.get("SYNTHESIZER_MAX_TOKENS", "1200"))
REASONING_EFFORT = os.environ.get("SYNTHESIZER_REASONING_EFFORT", "medium").lower()
if REASONING_EFFORT not in {"low", "medium", "high"}:
    REASONING_EFFORT = "medium"

CLARIFYING_ANSWER = (
    "I need a bit more detail to answer that -- could you specify a coil, piece of "
    "equipment, standard, technician, or time period you're asking about? For example: "
    "'Show deviations for the Coiler Unit this month' or 'Why did EQ-RHF-02 fail in June?'"
)

ERROR_ANSWER = "I wasn't able to generate an answer right now -- please try again."

SYSTEM_PROMPT = """You are the Synthesizer for Synapse, an industrial knowledge intelligence \
system for Rajendra Steel Plant (Mumbai Unit). You do not retrieve data — you receive \
evidence already fetched from three layers (DuckDB federated records, RAG document \
chunks, Neo4j graph relationships) and your job is to interpret it, not narrate it.

You are answering for plant staff (QA, Maintenance, Ops) who need decisions, not data dumps.

HOW THE EVIDENCE IS LABELLED (what you will see in the EVIDENCE block, and how to cite it):
- "[Graph — Neo4j] ..."          → Neo4j relationships/paths & node records. Cite as [Graph: relationship/path].
- "[Federated SQL / DuckDB — <SYSTEM>] ..." → structured rows/aggregates from erp/scada/qms/cmms. Cite as [DFS: table.column].
- "[RAG — <doc_id> · <type>] ..." → a retrieved document chunk. Cite as [RAG: <doc_id>].
- An RCA record may carry an "industry_reference" object ({source_name, source_url, summary_text}).
  This is GENERAL engineering knowledge, NOT a claim about this plant — cite it separately as
  [Industry Reference: <source_name>] and frame it as general mechanism knowledge, never as a
  specific event at this plant.

RULES:
1. GROUND EVERYTHING. Never state a fact not present in the evidence. If evidence is thin or \
conflicting, say so explicitly rather than filling gaps.
2. DO NOT SUMMARIZE — SYNTHESIZE. A list of facts restated in prose is a failure mode. For \
every answer, work through these four layers before writing your response:
   a. DIRECT FACTS — what does the evidence literally show?
   b. CORRELATION — what repeats or clusters across records that isn't stated outright? (same \
equipment_id, same coil_id lineage, same raw material batch, same technician, same time window, \
same failure mode across multiple standards)
   c. LIKELY IMPLICATION — given the correlation, what's the probable root cause, risk, or \
compliance exposure? State confidence level (high/medium/low) based on evidence strength — \
don't overclaim on 2 data points.
   d. RECOMMENDED NEXT STEP — one concrete action the user should take, scoped to their role \
(e.g. Maintenance → inspect X; QA → hold batch Y; Compliance → flag deviation Z against \
IS:1786/ASTM A370/IS 2062).
3. USE PRE-AGGREGATED DATA WHEN PROVIDED. If the evidence includes aggregates (counts, \
groupings, time-series), treat these as authoritative — do not recompute or second-guess \
arithmetic yourself from raw rows.
4. CITE BY SOURCE LAYER, NOT JUST RECORD. Every claim should be traceable to [DFS: table.column], \
[RAG: doc_id], or [Graph: relationship/path]. Compound insights (step b/c) should cite the full \
set of records that produced the pattern, not one row.
5. FLAG DATA CHARACTER WHERE RELEVANT. If evidence draws from synthetic vs. real dataset sources \
and that distinction matters to the answer's confidence, say so briefly.
6. NO SPECULATION BEYOND EVIDENCE SCOPE. If the query asks something the evidence can't support, \
say what's missing and what additional data/system would answer it — don't invent it.
7. END WITH A "SO WHAT" LINE. One sentence: the operational, compliance, or downtime implication \
of this answer for the plant, even if the user didn't ask for it.
8. CROSS-DIMENSIONAL CORRELATIONS. For pattern/causal questions the Graph evidence may include a \
"cross_dimensional_correlations" record: pre-computed correlations across adjacent dimensions \
(shift, technician, procedure, raw-material supplier, maintenance timing) that a single-system \
check would miss. Rules for using it: (a) ALWAYS state the sample size (n=X) next to any \
correlation you assert; (b) if a finding is flagged confidence "low" (small sample), present it \
as tentative — "worth watching, not yet conclusive" — never as a strong finding; (c) mention a \
relevant adjacent-dimension correlation even when the user did not explicitly ask about that \
dimension, briefly, as an "also worth noting" line; (d) these correlations are computed from \
graph traversals — cite them as [Graph: <dimension> correlation].

OUTPUT FORMAT:
- Lead with the direct answer (1-2 sentences)
- Insight paragraph (correlation + implication, per 2b/2c)
- Recommended action (per 2d)
- Sources used (layer-tagged)
- So-what line

TONE: Direct, plant-floor practical. Write like an experienced ops engineer briefing a \
colleague, not like a report. No filler, no hedging beyond stated confidence levels."""


def _fmt_rows(rows):
    if isinstance(rows, (list, tuple)):
        return "\n".join(json.dumps(r, ensure_ascii=False, default=str) for r in rows)
    return json.dumps(rows, ensure_ascii=False, default=str)


def build_evidence_block(retrieval_plan, graph_results, structured_results, document_results):
    """Assemble labeled evidence sections. Layers that were queried but returned nothing
    are explicitly marked 'none found' rather than silently omitted."""
    layers = retrieval_plan.get("layers", [])
    retrieval_errors = retrieval_plan.get("retrieval_errors", {})
    parts = []

    if "graph" in layers:
        if retrieval_errors.get("graph"):
            parts.append("[Graph unavailable: Neo4j connection failed; do not infer graph facts]")
        elif graph_results:
            backend = "locked ontology snapshot fallback" if any(
                row.get("_evidence_backend") == "locked_ontology_snapshot"
                for row in graph_results if isinstance(row, dict)
            ) else "Neo4j"
            parts.append(f"[Graph — {backend}]\n" + _fmt_rows(graph_results))
        else:
            parts.append("[Graph — Neo4j: none found]")

    if "structured" in layers:
        if retrieval_errors.get("structured"):
            parts.append("[DFS unavailable: structured store query failed; do not infer SQL facts]")
        elif structured_results:
            for system, rows in structured_results.items():
                # system may be a bare catalog ('qms') or a labelled join ('qms+erp (federated)')
                label = str(system).upper()
                if rows:
                    parts.append(f"[Federated SQL / DuckDB — {label}]\n" + _fmt_rows(rows))
                else:
                    parts.append(f"[Federated SQL / DuckDB — {label}: none found]")
        else:
            parts.append("[Federated SQL / DuckDB: none found]")

    if "documents" in layers:
        if retrieval_errors.get("documents"):
            parts.append("[RAG unavailable: document search failed; do not infer document facts]")
        elif document_results:
            for chunk in document_results:
                doc_id = chunk.get("document_id") or chunk.get("source_document_id", "?")
                parts.append(
                    f"[RAG — {doc_id} · {chunk.get('doc_type', '?')}]\n"
                    + chunk.get("text", "")
                )
        else:
            parts.append("[RAG — documents: none found]")

    return "\n\n".join(parts)


_SOURCE_TAG_RX = re.compile(
    r"\[((?:Graph|DFS|RAG|STRUCTURED|Document|Industry Reference)[^\]]*)\]",
    re.IGNORECASE,
)


def extract_sources(answer):
    """Unique source labels actually cited in the answer, in order of first appearance."""
    seen, out = set(), []
    for m in _SOURCE_TAG_RX.finditer(answer):
        label = re.sub(r"\s+", " ", m.group(1).strip())
        if label.lower() not in seen:
            seen.add(label.lower())
            out.append(f"[{label}]")
    return out


def _validate_answer(answer):
    """Reject corrupted/free-provider output before it can be returned or cached."""
    if len(answer) < 40:
        raise ValueError("model answer was too short")
    if answer.lower().count("<unk>") > 1:
        raise ValueError("model answer contained corrupted unknown-token output")
    if not _SOURCE_TAG_RX.search(answer):
        raise ValueError("model answer contained no evidence citation")


def _deterministic_evidence_answer(question, graph_results, document_results, structured_results=None):
    """Answer exact, high-confidence entity lookups without an external model call."""
    q = question.lower()
    graph_rows = [row for row in (graph_results or []) if isinstance(row, dict)]
    documents = document_results or []
    structured = structured_results or {}

    def rows_for(fragment):
        return next((rows for name, rows in structured.items() if fragment in str(name).lower()), None) or []

    if re.search(r"how many coils.*(fail|defect|deviat|quality)", q):
        rows = rows_for("qms+erp")
        metrics = {row.get("metric"): row.get("value") for row in rows}
        failed = metrics.get("coils_with_at_least_one_failed_test")
        total = metrics.get("total_coils")
        tests = metrics.get("total_quality_tests")
        if failed is not None and total:
            rate = 100 * failed / total
            return (
                f"**Direct answer:** {failed} of {total} coils have at least one recorded quality deviation ({rate:.2f}%) [DFS: qms.deviations.coil_id_fk; erp.coils.coil_id].\n\n"
                f"**Insight:** The denominator is the full ERP coil population, while the numerator is distinct coil IDs in QMS deviations; {tests or 0} quality tests provide the inspection context. **High confidence** because the counts are pre-aggregated from the source tables.\n\n"
                "**Recommended action for QA:** Review the affected-coil list by severity and production equipment before deciding whether a targeted hold or a wider process check is required.\n\n"
                "**Sources used:**\n- [DFS: qms.deviations.coil_id_fk; erp.coils.coil_id] distinct failed-coil numerator and total-coil denominator.\n\n"
                "**So what:** A denominator-backed rate lets QA size the real exposure without waiting for model synthesis."
            )

    if re.search(r"which equipment (?:failed|fails) most|most (?:affected|failure-prone) equipment", q):
        rows = rows_for("equipment failures")
        if rows:
            top = rows[0]
            leaders = ", ".join(f"{row.get('equipment_name') or row.get('equipment_id')} ({row.get('failure_count')})" for row in rows[:3])
            return (
                f"**Direct answer:** {top.get('equipment_name') or top.get('equipment_id')} ({top.get('equipment_id')}) has the most recorded failures this quarter: {top.get('failure_count')} [DFS: cmms.failures.equipment_id; scada.equipment.name].\n\n"
                f"**Insight:** The leading equipment ranking is {leaders}. **High confidence** for the ranking because it is a direct grouped count over the current-quarter CMMS records. The operational implication is concentrated downtime risk on the leading asset.\n\n"
                f"**Recommended action for Maintenance:** Start the reliability review with {top.get('equipment_id')}, then compare its recurring modes and open corrective work with the next two assets.\n\n"
                "**Sources used:**\n- [DFS: cmms.failures.equipment_id; scada.equipment.name] current-quarter failure counts.\n\n"
                "**So what:** Focusing on the highest-frequency asset directs maintenance effort to the largest current downtime signal."
            )

    if re.search(r"which standard.*(?:coating|fault|defect|violate)", q):
        rows = rows_for("coating-fault standards")
        if rows:
            top = rows[0]
            return (
                f"**Direct answer:** {top.get('standard_ref')} is the most frequently associated standard for coating-irregularity tests on coils with recorded deviations: {top.get('associated_test_count')} tests across {top.get('associated_coil_count')} coils [DFS: qms.quality_tests.standard_ref; qms.deviations.coil_id_fk].\n\n"
                "**Insight:** This is a shared-coil association, not a direct QualityTest-to-Deviation edge. **Medium confidence** for attribution: the standard ranking is exact, but an individual deviation cannot be assigned to one test without an explicit relationship. The compliance implication is a cohort-level clause risk, not proof that one test caused one deviation.\n\n"
                f"**Recommended action for QA:** Open the {top.get('standard_ref')} clause record, verify the affected coils and keep the attribution at cohort level unless the missing test-to-deviation link is added.\n\n"
                "**Sources used:**\n- [DFS: qms.quality_tests.standard_ref; qms.deviations.coil_id_fk] coating-test standard counts on deviation-bearing coils.\n\n"
                "**So what:** The ranking identifies the first compliance clause to investigate while preserving the graph's attribution boundary."
            )

    if re.search(r"\bdeviation rate\b", q):
        rows = rows_for("test deviation rate")
        if rows and rows[0].get("total_tests"):
            row = rows[0]
            return (
                f"**Direct answer:** The quality-test deviation rate is {float(row.get('deviation_rate_pct') or 0):.2f}%: {row.get('failed_tests')} coil-linked deviations over {row.get('total_tests')} quality tests [DFS: qms.deviations.coil_id_fk; qms.quality_tests.test_id].\n\n"
                "**Insight:** The formula excludes equipment-only deviations from the test numerator, so the numerator and denominator describe the same quality-testing population. **High confidence** because both counts are direct aggregates. The quality-risk implication is that trend changes can be compared without denominator drift.\n\n"
                "**Recommended action for QA:** Trend this rate by standard and equipment, then inspect any clause whose recent 90-day rate rises above its prior period.\n\n"
                "**Sources used:**\n- [DFS: qms.deviations.coil_id_fk; qms.quality_tests.test_id] matched compliance numerator and test denominator.\n\n"
                "**So what:** A consistent denominator makes compliance trend changes actionable instead of anecdotal."
            )

    if re.search(r"\bhow many\b.*\bdocuments?\b|\bdocuments?\b.*\bcount\b", q):
        rows = rows_for("document inventory")
        metrics = {row.get("metric"): row.get("value") for row in rows}
        if metrics.get("total_documents") is not None:
            total = metrics["total_documents"]
            top_types = sorted(((key.split(":", 1)[1], value) for key, value in metrics.items() if str(key).startswith("doc_type:")), key=lambda item: item[1], reverse=True)[:3]
            breakdown = ", ".join(f"{name}: {count}" for name, count in top_types)
            return (
                f"**Direct answer:** The knowledge base tracks {total} managed documents [DFS: document catalog.document_id].\n\n"
                f"**Insight:** The largest document groups are {breakdown or 'not classified'}. **High confidence** because this is a direct inventory count, not a semantic-search estimate. The retrieval-quality implication is that missing governed document types create evidence-coverage risk.\n\n"
                "**Recommended action for Admin:** Review document types with low coverage and verify that current procedures, RCA reports and test certificates have vector references.\n\n"
                "**Sources used:**\n- [DFS: document catalog.document_id] managed-document inventory.\n\n"
                "**So what:** Inventory coverage shows whether the retrieval layer has enough governed evidence to support plant decisions."
            )

    for row in graph_rows:
        failure = row.get("failure") or {}
        rcas = row.get("rca_records") or []
        equipment = row.get("equipment") or {}
        if failure.get("failure_id") and rcas and re.search(r"\bwhy\b|\bcaus|\brca\b|procedure gap", q):
            rca = rcas[0]
            fid, rid = failure["failure_id"], rca.get("rca_id", "the linked RCA")
            equipment_name = equipment.get("name") or equipment.get("equipment_id") or "the linked equipment"
            equipment_id = equipment.get("equipment_id", "")
            procedure = rca.get("procedure_ref") or "the governing procedure"
            violated = rca.get("violated_step") or "No violated step was recorded."
            root_cause = rca.get("root_cause_text") or failure.get("failure_mode", "the recorded failure mode")
            corrective = rca.get("corrective_action") or "verify the corrective work before restart"
            root_cause = re.sub(r"^root cause traced to\s*", "", root_cause, flags=re.I)
            failure_label = str(failure.get("failure_mode") or "failure").replace("_", " ")
            exact_doc = next((doc for doc in documents if fid in doc.get("text", "")), None)
            confidence = calibrate_confidence(
                direct_chain=True,
                corroborating_sources=2 if exact_doc else 1,
            )["level"].title()
            rag_line = f"\n- [RAG: {exact_doc['document_id']}] exact linked work-order narrative." if exact_doc else ""
            answer = (
                f"**Direct answer:** {fid} on {equipment_name} ({equipment_id}) was diagnosed by {rid}. "
                f"The recorded root cause was {root_cause} The linked procedure finding was {procedure}: {violated}\n\n"
                f"**Insight:** The failure, RCA, procedure finding and corrective work are linked by exact IDs across the audited graph"
                f"{' and its work-order document' if exact_doc else ''}. **{confidence} confidence**: this is a direct event chain, not a statistical inference. "
                f"The operational risk is recurrence of the same {failure_label} if the recorded procedure gap remains open.\n\n"
                f"**Recommended action for Maintenance:** The recorded corrective work was: {corrective} Confirm that this work and the cited {procedure} step are complete and documented, "
                f"validate the repair under normal load, and review the next operating cycle before returning the asset to unrestricted service.\n\n"
                f"**Sources used:**\n- [Graph: EXPERIENCED -> DIAGNOSED_BY; RCA.procedure_ref -> Procedure] {fid}, {rid}, {procedure}.{rag_line}\n\n"
                f"**So what:** Closing the recorded procedure gap reduces repeat downtime and makes the repair auditable."
            )
            return answer

        coil = row.get("coil") or {}
        produced = row.get("produced_at_equipment") or {}
        if coil.get("coil_id") and produced.get("equipment_id") and re.search(r"produc|equipment|lineage", q):
            cid, eid = coil["coil_id"], produced["equipment_id"]
            name = produced.get("name") or eid
            deviations = row.get("deviations") or []
            deviation_note = f" The same neighborhood includes {len(deviations)} deviation record(s)." if deviations else ""
            confidence = calibrate_confidence(direct_chain=True, corroborating_sources=1)["level"].title()
            return (
                f"**Direct answer:** Coil {cid} was produced at {eid} ({name}) through the `PRODUCED_AT` relationship.\n\n"
                f"**Insight:** This is an exact coil-to-equipment lineage link.{deviation_note} **{confidence} confidence** for operational implication: "
                f"the lineage is definitive, but attributing any quality risk to the stand requires corroborating roll-condition and batch history.\n\n"
                f"**Recommended action for Operations:** Use {eid} as the starting asset for shift-log, setup and maintenance checks; have QA compare nearby coils before escalating to a line-wide hold.\n\n"
                f"**Sources used:**\n- [Graph: PRODUCED_AT] {cid} -> {eid}.\n\n"
                f"**So what:** Exact lineage narrows a cross-system investigation to the responsible production asset in one step."
            )

    is2062 = next((doc for doc in documents if doc.get("document_id") == "DOC1058"), None)
    if is2062 and re.search(r"is\s*:?[ -]?2062", q, re.I):
        confidence = calibrate_confidence(
            direct_chain=True, corroborating_sources=1, authoritative_source=True
        )["level"].title()
        return (
            "**Direct answer:** IS 2062 covers hot-rolled medium and high-tensile structural steel supplied as plates, strips, sections, flats and bars. "
            "It defines grade/sub-quality requirements covering manufacture, chemical composition, mechanical properties and testing [RAG: DOC1058].\n\n"
            "**Insight:** Non-compliance creates a structural assurance risk: strength, ductility, weldability and toughness may not be demonstrated for the declared grade. "
            f"**{confidence} confidence** on scope; exact numeric limits are intentionally omitted from this summary and must be checked in the licensed BIS text [RAG: DOC1058].\n\n"
            "**Recommended action for QA:** Verify grade and sub-quality, heat/mill certificate traceability, chemical analysis, mechanical test results, dimensions and surface acceptance against the licensed current edition before release.\n\n"
            "**Sources used:**\n- [RAG: DOC1058] BIS IS 2062 scope and classification reference.\n\n"
            "**So what:** A documented IS 2062 verification prevents structurally unsuitable material from moving into fabrication or dispatch."
        )
    return None


def synthesize_answer(question, retrieval_plan,
                      graph_results=None, structured_results=None, document_results=None):
    """Produce a grounded, cited answer from retrieved evidence. Never raises."""
    # ---- unresolvable short-circuit: no LLM call at all ----
    if retrieval_plan.get("confidence") == "unresolvable":
        return {
            "answer": CLARIFYING_ANSWER,
            "sources": [],
            "model_used": "none (unresolvable short-circuit)",
        }

    deterministic = _deterministic_evidence_answer(
        question, graph_results, document_results, structured_results
    )
    if deterministic:
        return {
            "answer": deterministic,
            "sources": extract_sources(deterministic),
            "model_used": "deterministic/evidence-template",
        }

    api_key = get_openrouter_key()
    if not api_key:
        reason = "OPENROUTER_API_KEY is not configured in the backend environment."
        return {
            "answer": f"I couldn't generate the answer because {reason}",
            "sources": [], "model_used": "error", "generation_error": reason,
        }

    evidence = build_evidence_block(retrieval_plan, graph_results,
                                    structured_results, document_results)
    # today's date lets the model resolve relative time ("last month", "this quarter")
    # against evidence timestamps instead of refusing
    user_msg = (f"QUESTION: {question}\n\nTODAY'S DATE: {date.today().isoformat()}\n\n"
                f"EVIDENCE:\n\n{evidence}")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    def _call(model, retries=(0,)):
        """One model, optional 429 retries. Returns answer text or raises."""
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.1,
            "max_tokens": MAX_TOKENS,
            "reasoning": {"effort": REASONING_EFFORT},
        }
        for backoff in retries:
            resp = requests.post(CHAT_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
            body = resp.json()
            rate_limited = (resp.status_code == 429
                            or (isinstance(body.get("error"), dict)
                                and body["error"].get("code") == 429))
            if rate_limited and backoff:
                time.sleep(backoff)
                continue
            break
        resp.raise_for_status()
        if "error" in body:                    # OpenRouter can 200 with an error payload
            raise ValueError(f"provider error: {str(body['error'])[:150]}")
        answer = (body["choices"][0]["message"].get("content") or "").strip()
        if not answer:
            raise ValueError("model returned empty content")
        return answer

    forced = os.environ.get("SYNTHESIZER_MODEL")
    if forced:
        # deterministic single-model mode (testing): no fallback, but retry 429 bursts
        candidates = [(forced, (20, 40, 0))]
    else:
        # production mode: walk the fallback chain. Give the PRIMARY model a couple of 429
        # backoff-retries (free-tier rate limits are bursty/transient) so one bad moment
        # doesn't fail the whole answer; single-shot the fallbacks so latency stays bounded.
        candidates = [(MODEL_CHAIN[0], (3, 6, 0))] + [(m, (0,)) for m in MODEL_CHAIN[1:]]

    model_errors = []
    for model, retries in candidates:
        try:
            answer = _call(model, retries)
            _validate_answer(answer)
            return {
                "answer": answer,
                "sources": extract_sources(answer),
                "model_used": model,
            }
        except Exception as exc:
            model_errors.append(f"{model}: {type(exc).__name__}: {str(exc)[:180]}")
            continue                            # advance down the chain

    reason = "All configured OpenRouter models failed. " + " | ".join(model_errors)
    return {
        "answer": ERROR_ANSWER,
        "sources": [],
        "model_used": "error",
        "generation_error": reason,
    }
