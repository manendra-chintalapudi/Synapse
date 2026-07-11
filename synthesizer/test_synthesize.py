"""
Synthesizer test harness -- 4 manually constructed cases with realistic evidence shapes,
populated from the REAL node/chunk files so values match what the stores would return.

Case (b) is the critical citation-discipline test: graph facts about failure F1099 on
EQ-RHF-02 plus two document chunks -- the RHF equipment manual (relevant) and DOC1012, an
RCA report about a heat-dissipation failure on DIFFERENT equipment (EQ-HBS-02). A reliable
synthesizer must not blend DOC1012's content into claims about the Reheating Furnace.
"""
import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")   # Windows console: model output may contain
                                           # non-cp1252 chars (e.g. U+2011)

import synthesize
from synthesize import synthesize_answer

INTER_CASE_SLEEP_S = 30   # space out calls: free-tier pools rate-limit bursts

ROOT = Path(__file__).resolve().parent.parent
NODES = ROOT / "ontology" / "nodes"
CHUNKS = ROOT / "data" / "unstructured" / "chunks"


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def chunk_for(doc_id, must_contain=None):
    """Pick the chunk of a document containing `must_contain` (else chunk 0), shaped like
    a vector-store hit."""
    chunks = jload(CHUNKS / f"{doc_id}.json")
    chosen = chunks[0]
    if must_contain:
        for ch in chunks:
            if must_contain.lower() in ch["text"].lower():
                chosen = ch
                break
    return {
        "document_id": chosen["source_document_id"],
        "doc_type": chosen["metadata"]["doc_type"],
        "chunk_id": chosen["chunk_id"],
        "text": chosen["text"],
        "score": 0.31,
    }


# ---------------------------------------------------------------------------
# build realistic evidence from real records
# ---------------------------------------------------------------------------
coil = next(c for c in jload(NODES / "coil.json") if c["coil_id"] == "C10234")
equip = {e["equipment_id"]: e for e in jload(NODES / "equipment.json")}
fail = next(f for f in jload(NODES / "failure.json") if f["failure_id"] == "F1099")
rca = next(r for r in jload(NODES / "rca.json") if r["rca_id"] == "RCA1099")

CASES = {
    "a_graph_only": {
        "question": "Which equipment produced coil C10234?",
        "plan": {"layers": ["graph"], "confidence": "confident", "tier": "tier2"},
        "graph": [{
            "coil_id": coil["coil_id"], "grade": coil["grade"],
            "production_date": coil["production_date"],
            "relationship": "PRODUCED_AT",
            "equipment_id": coil["equipment_id"],
            "equipment_name": equip[coil["equipment_id"]]["name"],
            "equipment_type": equip[coil["equipment_id"]]["type"],
        }],
        "structured": None, "documents": None,
    },
    "b_graph_plus_documents": {
        "question": "Why did the Reheating Furnace fail last month?",
        "plan": {"layers": ["graph", "documents"], "confidence": "confident", "tier": "tier2"},
        "graph": [
            {"equipment_id": fail["equipment_id"],
             "equipment_name": equip[fail["equipment_id"]]["name"],
             "relationship": "EXPERIENCED",
             "failure_id": fail["failure_id"], "failure_mode": fail["failure_mode"],
             "timestamp": fail["timestamp"], "sensor_values": fail["sensor_values"]},
            {"failure_id": rca["failure_id"], "relationship": "DIAGNOSED_BY",
             "rca_id": rca["rca_id"], "rca_date": rca["rca_date"],
             "root_cause_text": rca["root_cause_text"],
             "corrective_action": rca["corrective_action"]},
        ],
        "structured": None,
        "documents": [
            chunk_for("DOC1061", must_contain="failure modes"),   # RHF equipment manual
            chunk_for("DOC1012", must_contain="root cause"),      # RCA report, OTHER equipment
        ],
    },
    "c_documents_only": {
        "question": "What does IS 2062 cover?",
        "plan": {"layers": ["documents"], "confidence": "confident", "tier": "tier2"},
        "graph": None, "structured": None,
        "documents": [chunk_for("DOC1058"), chunk_for("DOC1058", must_contain="purpose")],
    },
    "d_unresolvable": {
        "question": "Is everything okay?",
        "plan": {"layers": ["graph", "structured", "documents"],
                 "confidence": "unresolvable", "tier": "tier3"},
        "graph": None, "structured": None, "documents": None,
    },
}


def citation_audit(answer):
    """Sentences (>4 words) lacking any source tag = unattributed claims.
    A tag placed just after the closing period (e.g. 'failed on X. [GRAPH]') belongs to
    the preceding sentence, so tag-only fragments are merged backwards before checking."""
    body = answer.replace("\n", " ")
    raw = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    sentences = []
    for s in raw:
        if sentences and re.fullmatch(r"(\[[^\]]+\][\s.]*)+", s):
            sentences[-1] += " " + s          # tag-only fragment -> previous sentence
        else:
            sentences.append(s)
    untagged = [s for s in sentences
                if len(s.split()) > 4 and not synthesize._SOURCE_TAG_RX.search(s)]
    return sentences, untagged


if __name__ == "__main__":
    results = {}

    for name, case in CASES.items():
        if name == "d_unresolvable":
            # hard proof of the short-circuit: any HTTP call would raise
            original_post = synthesize.requests.post
            def _boom(*a, **k):
                raise AssertionError("LLM was called for an unresolvable plan!")
            synthesize.requests.post = _boom
            try:
                out = synthesize_answer(case["question"], case["plan"],
                                        case["graph"], case["structured"], case["documents"])
            finally:
                synthesize.requests.post = original_post
        else:
            out = synthesize_answer(case["question"], case["plan"],
                                    case["graph"], case["structured"], case["documents"])
            time.sleep(INTER_CASE_SLEEP_S)        # avoid free-pool burst limits
        results[name] = out

        print("=" * 88)
        print(f"CASE {name}")
        print(f"Q: {case['question']}")
        print(f"model_used: {out['model_used']}")
        print(f"sources cited: {out['sources']}")
        print("answer:")
        print("  " + out["answer"].replace("\n", "\n  "))
        print()

    # ---- case (b) citation-discipline inspection ----
    print("=" * 88)
    print("CASE (b) CITATION AUDIT -- pass/fail signal for gpt-oss-120b as primary")
    print("=" * 88)
    b = results["b_graph_plus_documents"]
    sentences, untagged = citation_audit(b["answer"])
    print(f"  sentences: {len(sentences)} | untagged factual sentences: {len(untagged)}")
    for s in untagged:
        print(f"    UNTAGGED: {s}")
    doc1012_mentioned = "DOC1012" in b["answer"]
    print(f"  DOC1012 (other-equipment RCA trap) cited: {doc1012_mentioned}")
    print("  -> manually inspect above: is DOC1012 presented as being about the Reheating "
          "Furnace (BAD) or correctly scoped/omitted (GOOD)?")

    # ---- verify: zero Anthropic usage in this component ----
    print("\n" + "=" * 88)
    print("ANTHROPIC/CLAUDE USAGE CHECK (synapse/synthesizer/)")
    print("=" * 88)
    hits = []
    for p in Path(__file__).parent.glob("*.py"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"anthropic|claude", line, re.IGNORECASE):
                hits.append(f"{p.name}:{i}: {line.strip()}")
    print("  matches:", hits if hits else "NONE -- component is Anthropic-free")

    print("\nSUMMARY")
    for name, out in results.items():
        ok = "OK" if out["model_used"] != "error" else "ERROR"
        print(f"  {name:<24} model={out['model_used']:<38} sources={len(out['sources'])} [{ok}]")
