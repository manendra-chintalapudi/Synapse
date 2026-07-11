"""
Tier 3: LLM fallback planner -- ONLY runs when Tier 2 reports "ambiguous".

Uses OpenRouter's OpenAI-compatible chat-completions API (base_url
https://openrouter.ai/api/v1, endpoint /chat/completions) with a free-tier model to
produce a retrieval_plan in the same {layers, details, confidence} shape as Tier 2.
This is the ONLY place in the router that may call an LLM; it never retrieves data and
never answers questions.

Models (both verified against OpenRouter's live free-model list on 2026-07-08):
  PRIMARY  nvidia/nemotron-3-super-120b-a12b:free -- supports native tool/function
           calling, which improves structured-JSON reliability for the plan output.
  BACKUP   nvidia/nemotron-3-nano-30b-a3b:free -- lighter/faster NVIDIA option; defined
           here for easy manual swap (set OPENROUTER_MODEL) if the primary is
           rate-limited or unavailable. NOT tried automatically.
Override either via the OPENROUTER_MODEL environment variable -- no code change needed.
One OPENROUTER_API_KEY works across all OpenRouter models.

Outcome tagging:
  confidence="ambiguous-resolved"  -- the LLM produced a focused, plannable plan, OR the API
                                      failed/timed out and we fall back to a best-effort
                                      all-layers plan (answering beats stalling)
  confidence="unresolvable"        -- the model responded but the question has no plannable
                                      intent (generic all-layers plan / low self-confidence)
Failure policy: on any API error, timeout, or unparseable JSON -> best-effort all-layers plan
(confidence "ambiguous-resolved", so the pipeline still retrieves + answers rather than
short-circuiting to a clarification). This function NEVER raises to the caller.
"""
import json
import os
import re

import requests

BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_URL = f"{BASE_URL}/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
BACKUP_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"   # manual swap option; not auto-used
TIMEOUT_S = int(os.environ.get("ROUTER_TIMEOUT_S", "30"))
MAX_TOKENS = int(os.environ.get("ROUTER_MAX_TOKENS", "500"))
ALLOWED_LAYERS = {"graph", "structured", "documents"}
ALL_LAYERS = ["graph", "structured", "documents"]

SYSTEM_PROMPT = """You are the query router for Synapse, a steel-plant knowledge system. \
You do NOT answer questions and do NOT retrieve data. You only decide which retrieval \
layer(s) a question should be sent to, and what to look for.

The knowledge base:
- GRAPH layer (Neo4j): 11 node types -- Coil, Equipment, Failure, RCA, Procedure, \
Technician, QualityTest, Standard, Deviation, RawMaterial, Document -- connected by \
relationships (PRODUCED_AT, MADE_FROM, TESTED_BY, FAILED_STANDARD, TESTED_AGAINST, \
HAS_DEVIATION, EXPERIENCED, DIAGNOSED_BY, PERFORMED_BY, MAINTAINED_BY, FOLLOWS_PROCEDURE, \
REFERENCES_STANDARD, DOCUMENTED_IN, VERSION_OF). Use for tracing/linking entities.
- STRUCTURED layer (SQL over 4 systems): erp (coils, raw materials, bill of materials), \
scada (equipment registry), qms (quality tests, deviations, standards), cmms (failures, \
RCA, technicians, procedures). Use for counts, averages, totals, filters, trends.
- DOCUMENTS layer (semantic search): doc_types sop, rca_report, deviation_report, \
equipment_manual, inspection_report, standard_reference. Use for "what does X say", \
explanations, procedures, manuals, standards text.

Reply with ONLY a JSON object, no prose, in exactly this shape:
{"layers": ["graph"|"structured"|"documents", ...],
 "details": {"reason": "<one sentence>",
             "structured_systems": ["erp"|"scada"|"qms"|"cmms", ...],
             "graph_focus": "<what to trace, or empty string>",
             "document_filters": {"doc_type": "<type>"} or {},
             "search_text": "<text to search documents with>"},
 "confidence": "confident" or "ambiguous"}
Pick the smallest set of layers that can answer the question. If the question is too vague \
to route at all (no identifiable subject, timeframe, or metric), use all three layers and \
confidence "ambiguous"."""


def _safe_default(question, error):
    # A transient API failure (429 rate-limit, timeout, network) must NOT be reported as
    # "unresolvable" -- that confidence is reserved for genuinely vague questions and makes the
    # pipeline short-circuit to a clarification ("I need more detail"), which reads as a "dumb"
    # assistant. Instead, proceed with a best-effort all-layers plan so the question is still
    # retrieved and answered. Genuine vagueness is still caught in fallback_plan() when the
    # model DOES respond.
    return {
        "layers": list(ALL_LAYERS),
        "details": {
            "reason": "Tier-3 router LLM unavailable; best-effort all-layers retrieval",
            "error": str(error)[:200],
            "structured_systems": ["erp", "scada", "qms", "cmms"],
            "graph_focus": "",
            "document_filters": {},
            "search_text": question,
        },
        "confidence": "ambiguous-resolved",
        "source": "tier3_degraded",
    }


def _extract_json(text):
    """Parse the model reply leniently: take the first {...} block."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON object in reply: {text[:120]!r}")
    return json.loads(m.group(0))


def _is_focused(layers, details):
    """A plan is 'focused' (plannable) if it narrows anything: a subset of layers, a
    specific structured system, a graph focus, or a document filter."""
    if set(layers) != set(ALL_LAYERS):
        return True
    return bool(
        details.get("structured_systems")
        or (details.get("graph_focus") or "").strip()
        or details.get("document_filters")
    )


def fallback_plan(question: str) -> dict:
    """Ask the OpenRouter model for a retrieval_plan; never raises.

    Returns confidence 'ambiguous-resolved' (focused plan) or 'unresolvable'
    (generic/low-confidence plan, or API failure -> safe default)."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return _safe_default(question, "OPENROUTER_API_KEY not set")

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                "temperature": 0,
                "max_tokens": MAX_TOKENS,
            },
            timeout=TIMEOUT_S,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        plan = _extract_json(content)

        layers = [l for l in plan.get("layers", []) if l in ALLOWED_LAYERS]
        if not layers:
            raise ValueError(f"model returned no valid layers: {plan.get('layers')!r}")

        details = plan.get("details") or {}
        if not details.get("search_text"):        # missing OR empty -> fall back to the question
            details["search_text"] = question

        model_says_ambiguous = plan.get("confidence") != "confident"
        focused = _is_focused(layers, details)
        confidence = "ambiguous-resolved" if (focused and not model_says_ambiguous) else "unresolvable"

        return {
            "layers": [l for l in ALL_LAYERS if l in layers],
            "details": details,
            "confidence": confidence,
            "source": "tier3_llm",
            "model": model,
        }
    except Exception as exc:                      # network, HTTP, JSON, validation
        return _safe_default(question, exc)


if __name__ == "__main__":
    print(json.dumps(fallback_plan("Is everything okay?"), indent=2))
