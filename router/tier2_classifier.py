"""
Tier 2: rule-based intent classifier (no LLM).

classify_intent(question, matched_entities) ->
    {"layers": [...], "details": {...}, "confidence": "confident"|"ambiguous"}

Layers:
  structured -- SQL aggregations over the per-system DuckDB files (erp/scada/qms/cmms)
  graph      -- Neo4j relationship traversal from matched entities
  documents  -- semantic search over the Chroma chunk store

Rules (per spec):
  "how many"/"count of"/"average"/"total"                     -> structured
  "linked to"/"trace"/"which equipment produced"/"connected
   to"/"related"                                              -> graph
  "what does X say"/"explain"/"SOP for"/"manual"/
   "procedure for"                                            -> documents
  "why"/"root cause"                                          -> graph + documents (RCA chain)
  multiple entity types matched, or "why" with "and"/"also"   -> multiple layers combined
Ambiguous when: no entities AND no intent keywords, or a very short/vague question
(< 5 words with no entity match).
"""
import re

STRUCTURED_PATTERNS = [
    r"\bhow many\b", r"\bcount of\b", r"\bnumber of\b",
    r"\baverage\b", r"\bavg\b", r"\btotal\b", r"\bsum of\b", r"\bper (month|week|day|shift)\b",
]
GRAPH_PATTERNS = [
    r"\blinked to\b", r"\btrace\b", r"\bwhich equipment produced\b",
    r"\bconnected to\b", r"\brelated to\b", r"\bwhich .* (produced|made|tested|maintained)\b",
    r"\bmade from\b", r"\bproduced (on|at|by)\b",
]
DOCUMENT_PATTERNS = [
    r"\bwhat does\b.*\b(say|cover|state|require|specify)\b", r"\bexplain\b",
    r"\bsop for\b", r"\bsop\b", r"\bmanual\b", r"\bprocedure for\b",
    r"\baccording to\b", r"\bsummar(y|ise|ize)\b",
]
ROOT_CAUSE_PATTERNS = [r"\bwhy\b", r"\broot cause\b"]      # -> graph + documents

# light hints mapping question vocabulary -> structured systems
SYSTEM_HINTS = [
    ("qms", r"\bquality\b|\btest(s|ing|ed)?\b|\bdeviation(s)?\b|\bdefect(s)?\b|\bfault(s)?\b"),
    ("cmms", r"\bfail(ed|ure|ures)?\b|\bmaintenance\b|\brca\b|\broot cause\b|\btechnician(s)?\b"),
    ("erp", r"\bcoil(s)?\b|\bmaterial(s)?\b|\bproduction\b|\bproduced\b|\bgrade(s)?\b|\bstock\b"),
    ("scada", r"\bequipment\b|\bsensor(s)?\b|\benergy\b|\btemperature\b"),
]

ENTITY_LAYER = {"coil": "graph", "equipment": "graph", "failure": "graph", "standard": "graph",
                "technician": "graph", "doc_type": "documents"}


def _findall(patterns, text):
    return [p for p in patterns if re.search(p, text)]


def classify_intent(question: str, matched_entities: list) -> dict:
    q = question.lower()
    signals = {
        "structured": _findall(STRUCTURED_PATTERNS, q),
        "graph": _findall(GRAPH_PATTERNS, q),
        "documents": _findall(DOCUMENT_PATTERNS, q),
        "root_cause": _findall(ROOT_CAUSE_PATTERNS, q),
    }

    layers = set()
    if signals["structured"]:
        layers.add("structured")
    if signals["graph"]:
        layers.add("graph")
    if signals["documents"]:
        layers.add("documents")
    if signals["root_cause"]:                       # why/root-cause -> failure chain + reports
        layers.update({"graph", "documents"})

    entity_types = {e["entity_type"] for e in matched_entities}

    # multiple entity types matched -> combine the layers each entity type implies
    if len(entity_types) >= 2:
        layers.update(ENTITY_LAYER[t] for t in entity_types)

    # "why" combined with "and"/"also" -> explicitly multi-part question
    if signals["root_cause"] and re.search(r"\b(and|also)\b", q):
        layers.update({"graph", "documents"})

    # entity matched but no intent keywords -> default to entity-centric graph lookup
    if matched_entities and not layers:
        layers.add("graph")

    # ---- confidence ----
    any_signal = any(signals.values())
    word_count = len(question.split())
    ambiguous = (not matched_entities and not any_signal) or (word_count < 5 and not matched_entities)
    confidence = "ambiguous" if ambiguous else "confident"

    # ---- plan details ----
    details = {
        "matched_entities": matched_entities,
        "intent_signals": {k: v for k, v in signals.items() if v},
        "structured_systems": [s for s, rx in SYSTEM_HINTS if re.search(rx, q)] if "structured" in layers else [],
        "graph_start_entities": [e["entity_id"] for e in matched_entities
                                 if e["entity_type"] != "doc_type"] if "graph" in layers else [],
        "document_filters": (
            {"doc_type": next((e["entity_id"] for e in matched_entities if e["entity_type"] == "doc_type"), None)}
            if "documents" in layers else {}
        ),
        "search_text": question,
    }
    if details["document_filters"].get("doc_type") is None:
        details["document_filters"] = {}

    order = ["graph", "structured", "documents"]
    return {
        "layers": [l for l in order if l in layers],
        "details": details,
        "confidence": confidence,
    }
