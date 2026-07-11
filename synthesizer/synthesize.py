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
evidence already fetched from three layers (DFS/Trino structured records, RAG document \
chunks, Neo4j graph relationships) and your job is to interpret it, not narrate it.

You are answering for plant staff (QA, Maintenance, Ops) who need decisions, not data dumps.

HOW THE EVIDENCE IS LABELLED (what you will see in the EVIDENCE block, and how to cite it):
- "[Graph — Neo4j] ..."          → Neo4j relationships/paths & node records. Cite as [Graph: relationship/path].
- "[DFS/Trino — <SYSTEM>] ..."   → structured SQL rows/aggregates federated from erp/scada/qms/cmms. Cite as [DFS: table.column].
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
            parts.append("[Graph — Neo4j]\n" + _fmt_rows(graph_results))
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
                    parts.append(f"[DFS/Trino — {label}]\n" + _fmt_rows(rows))
                else:
                    parts.append(f"[DFS/Trino — {label}: none found]")
        else:
            parts.append("[DFS/Trino: none found]")

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
