"""
Tier 1: entity matcher (no LLM).

match_entities(question, index) -> [{"entity_type", "entity_id", "matched_text"}, ...]

Two passes:
  1. ID fast-path -- one regex per ID shape (C10001, EQ-RHF-01, STD-IS2062-01, T1001,
     DOC1001) checked against the index by set membership.
  2. Alias pass -- case-insensitive word-boundary search of every name/alias (len >= 3)
     against the question; e.g. "reheating furnace" and "EQ-RHF-01" both match Equipment.

Dedupes to one hit per (entity_type, entity_id), keeping the longest matched text.
"""
import re

ID_PATTERNS = {
    "coil": re.compile(r"\bC\d{5}\b", re.IGNORECASE),
    "equipment": re.compile(r"\bEQ-[A-Z]{2,4}-\d{2}\b", re.IGNORECASE),
    "failure": re.compile(r"\bF\d{4}\b", re.IGNORECASE),
    "standard": re.compile(r"\bSTD-[A-Z0-9]+-\d{2}\b", re.IGNORECASE),
    "technician": re.compile(r"\bT\d{4}\b", re.IGNORECASE),
}


def _alias_regex(alias):
    return re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE)


_ALIAS_CACHE = {}


def _compiled_aliases(index):
    """Compile (and cache) alias regexes for the non-ID entity names."""
    key = id(index)
    if key not in _ALIAS_CACHE:
        compiled = []
        for etype, items in index.items():
            for item in items:
                for alias in item["aliases"]:
                    if len(alias) >= 3 and not ID_PATTERNS.get(etype, re.compile(r"$^")).fullmatch(alias.upper()):
                        compiled.append((etype, item["id"], _alias_regex(alias)))
        _ALIAS_CACHE[key] = compiled
    return _ALIAS_CACHE[key]


def match_entities(question: str, index: dict) -> list:
    """Case-insensitive substring/regex matching of the question against IDs and names."""
    hits = {}  # (entity_type, entity_id) -> matched_text (longest wins)

    def record(etype, eid, text):
        k = (etype, eid)
        if k not in hits or len(text) > len(hits[k]):
            hits[k] = text

    # pass 1: explicit IDs
    id_sets = {etype: {item["id"].upper() for item in items} for etype, items in index.items()}
    for etype, pattern in ID_PATTERNS.items():
        for m in pattern.finditer(question):
            token = m.group(0).upper()
            if token in id_sets.get(etype, set()):
                record(etype, token, m.group(0))

    # pass 2: names / aliases
    for etype, eid, rx in _compiled_aliases(index):
        m = rx.search(question)
        if m:
            record(etype, eid, m.group(0))

    return [
        {"entity_type": etype, "entity_id": eid, "matched_text": text}
        for (etype, eid), text in sorted(hits.items())
    ]


if __name__ == "__main__":
    from entity_index import build_entity_index
    idx = build_entity_index()
    for q in ["Which equipment produced coil C10234?",
              "Has EQ-RHF-01 had any recent failures?",
              "What does IS 2062 cover?",
              "Show me the SOP for the reheating furnace"]:
        print(q, "->", match_entities(q, idx))
