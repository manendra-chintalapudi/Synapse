"""
ask_synapse(question) -- the complete Synapse query pipeline in one call.

    router.route()  ->  retrieval fan-out (parallel)  ->  synthesizer
      tiers 1-3         graph   : Neo4j  (entity-neighborhood Cypher templates)
                        structured: Trino federated SQL over erp/scada/qms/cmms
                        documents : Chroma semantic search (MiniLM embeddings)

Returns {answer, sources, model_used, retrieval_plan, latency} -- retrieval_plan is
included for demo transparency ("here's what the system decided to check"), latency
carries per-stage timings for demo pacing.

Ready to sit behind a FastAPI endpoint; no web layer here yet.
"""
import os
import re
import sys
import time
import copy
import json
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_BASE = Path(__file__).resolve().parent
for _sub in ("router", "embeddings", "synthesizer", "retrieval"):
    _p = str(_BASE / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import get_openrouter_key          # synthesizer/config.py (.env-aware)

# tier3_fallback reads OPENROUTER_API_KEY from os.environ only -> hydrate it from .env
_key = get_openrouter_key()
if _key:
    os.environ.setdefault("OPENROUTER_API_KEY", _key)

from router import route                       # router/router.py
from graph_store import entity_neighborhood    # retrieval/graph_store.py
from structured_store import query_federated   # retrieval/structured_store.py
from search import search as document_search   # embeddings/search.py
from synthesize import synthesize_answer       # synthesizer/synthesize.py
from patterns import detect_patterns, PATTERN_INTENT_RX   # retrieval/patterns.py

MAX_GRAPH_ENTITIES = 4
DOC_TOP_K = 4
CACHE_TTL_S = int(os.environ.get("QUERY_CACHE_TTL_S", "300"))
CACHE_MAX_ENTRIES = int(os.environ.get("QUERY_CACHE_MAX_ENTRIES", "128"))
_cache = OrderedDict()
_cache_lock = threading.Lock()


def _cache_key(question: str) -> str:
    return " ".join(question.lower().split())


def _cache_get(question: str):
    if CACHE_TTL_S <= 0 or CACHE_MAX_ENTRIES <= 0:
        return None
    key = _cache_key(question)
    now = time.monotonic()
    with _cache_lock:
        item = _cache.get(key)
        if item is None:
            return None
        created, value = item
        if now - created > CACHE_TTL_S:
            del _cache[key]
            return None
        _cache.move_to_end(key)
        return copy.deepcopy(value)


def _cache_put(question: str, value: dict):
    if CACHE_TTL_S <= 0 or CACHE_MAX_ENTRIES <= 0:
        return
    key = _cache_key(question)
    with _cache_lock:
        _cache[key] = (time.monotonic(), copy.deepcopy(value))
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)

# ---------------------------------------------------------------------------
# structured layer: intent-matched SQL templates (same pattern as graph templates)
# ---------------------------------------------------------------------------
COILS_FAILED_QC_SQL = """
SELECT 'coils_with_at_least_one_failed_test' AS metric,
       COUNT(DISTINCT d.coil_id_fk) AS value
FROM qms.main.deviations d WHERE d.coil_id_fk IS NOT NULL
UNION ALL SELECT 'total_coils', COUNT(*) FROM erp.main.coils
UNION ALL SELECT 'total_quality_tests', COUNT(*) FROM qms.main.quality_tests
UNION ALL SELECT 'failed_quality_tests_(with_deviation)', COUNT(*)
          FROM qms.main.deviations WHERE coil_id_fk IS NOT NULL
"""

SYSTEM_SUMMARY_SQL = {
    "qms": ("quality tests by fault type",
            "SELECT fault_type AS metric, COUNT(*) AS value FROM qms.main.quality_tests "
            "GROUP BY fault_type ORDER BY value DESC"),
    "cmms": ("failures by mode",
             "SELECT failure_mode AS metric, COUNT(*) AS value FROM cmms.main.failures "
             "GROUP BY failure_mode ORDER BY value DESC"),
    "erp": ("coils by status",
            "SELECT status AS metric, COUNT(*) AS value FROM erp.main.coils "
            "GROUP BY status ORDER BY value DESC"),
    "scada": ("equipment by type",
              "SELECT type AS metric, COUNT(*) AS value FROM scada.main.equipment "
              "GROUP BY type ORDER BY value DESC"),
}

AI4I_FAILURE_SQL = """
SELECT COUNT(*) AS records,
       SUM(machine_failure) AS machine_failures,
       SUM(tool_wear_failure) AS tool_wear_failures,
       SUM(heat_dissipation_failure) AS heat_dissipation_failures,
       SUM(power_failure) AS power_failures,
       SUM(overstrain_failure) AS overstrain_failures,
       SUM(random_failure) AS random_failures
FROM scada.main.ai4i_events
"""


def structured_retrieval(question, details):
    """Pick intent-matched SQL template(s) and run them federated via Trino."""
    q = question.lower()
    results = {}
    if re.search(r"how many coils.*(fail|defect|deviat|quality)", q):
        results["qms+erp (federated)"] = query_federated(COILS_FAILED_QC_SQL)
        return results
    if re.search(r"\bai4i\b|predictive maintenance|machine failure|sensor failure", q):
        results["scada (AI4I 2020 official synthetic reference)"] = query_federated(AI4I_FAILURE_SQL)
        return results
    # generic per-system summaries for the systems the router hinted at
    systems = details.get("structured_systems") or ["qms", "cmms"]
    for system in systems[:3]:
        label, sql = SYSTEM_SUMMARY_SQL[system]
        results[f"{system} ({label})"] = query_federated(sql)
    return results


def graph_retrieval(details):
    """Entity-neighborhood Cypher per matched entity (typed templates in graph_store)."""
    entities = details.get("matched_entities") or details.get("tier1_entities") or []
    records = []
    for ent in entities[:MAX_GRAPH_ENTITIES]:
        records.extend(entity_neighborhood(ent["entity_type"], ent["entity_id"]))
    return records


def documents_retrieval(question, details):
    """Resolve exact entity-linked documents first, then fill remaining slots semantically."""
    text = details.get("search_text") or question
    doc_filter = details.get("document_filters") or {}
    flt = {"doc_type": doc_filter["doc_type"]} if doc_filter.get("doc_type") else None
    entities = details.get("matched_entities") or details.get("tier1_entities") or []
    entity_ids = {entity.get("entity_id") for entity in entities if entity.get("entity_id")}
    direct = []
    if entity_ids:
        catalog = json.loads((_BASE / "ontology" / "nodes" / "document.json").read_text(encoding="utf-8"))
        for document in catalog:
            if document.get("related_entity_id") not in entity_ids:
                continue
            path = _BASE / document["vector_ref"]
            if path.exists():
                direct.append({
                    "document_id": document["document_id"],
                    "doc_type": document["doc_type"],
                    "chunk_id": "exact-entity-link",
                    "text": path.read_text(encoding="utf-8"),
                    "score": 1.0,
                    "retrieval_mode": "exact_entity_link",
                })
    direct = direct[:DOC_TOP_K]
    try:
        hits = document_search(text, k=DOC_TOP_K, filter=flt)
    except Exception:
        if direct:
            return direct
        raise
    semantic = [{
        "document_id": h["metadata"]["source_document_id"],
        "doc_type": h["metadata"]["doc_type"],
        "chunk_id": h["metadata"]["chunk_id"],
        "text": h["text"],
        "score": h["score"],
    } for h in hits]
    seen = {row["document_id"] for row in direct}
    return direct + [row for row in semantic if row["document_id"] not in seen][:(DOC_TOP_K - len(direct))]


def warm_up():
    """Pre-load the embedding model + vector store (~15s one-time cost). Call this at
    API startup so the first user question doesn't absorb the load time."""
    document_search("warm up", k=1)


def ask_synapse(question: str) -> dict:
    """Route -> retrieve (parallel) -> synthesize. Returns the full transparent result."""
    cached = _cache_get(question)
    if cached is not None:
        cached["latency"] = {
            "routing_s": 0.0, "retrieval_s": 0.0, "synthesis_s": 0.0,
            "total_s": 0.0, "cache_hit": True,
        }
        return cached

    t0 = time.perf_counter()
    plan = route(question)
    t_route = time.perf_counter() - t0

    graph_results = structured_results = document_results = None
    retrieval_errors = {}
    t_retrieval = 0.0

    # unresolvable plans short-circuit in the synthesizer -- skip retrieval entirely
    if plan["confidence"] != "unresolvable":
        details = plan["details"]
        # pattern/causal intent -> also sweep the adjacent dimensions (shift, procedure,
        # supplier, maintenance timing) so cross-system correlations surface even when the
        # user asked about only one path. This is broader QUERYING, not new relationships.
        wants_patterns = bool(PATTERN_INTENT_RX.search(question))
        t1 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {}
            if "graph" in plan["layers"]:
                futures["graph"] = pool.submit(graph_retrieval, details)
            if "structured" in plan["layers"]:
                futures["structured"] = pool.submit(structured_retrieval, question, details)
            if "documents" in plan["layers"]:
                futures["documents"] = pool.submit(documents_retrieval, question, details)
            if wants_patterns:
                futures["patterns"] = pool.submit(detect_patterns)
            completed = {}
            for layer, future in futures.items():
                try:
                    completed[layer] = future.result()
                except Exception as exc:
                    completed[layer] = None
                    retrieval_errors[layer] = f"{type(exc).__name__}: {str(exc)[:240]}"
            graph_results = completed.get("graph")
            structured_results = completed.get("structured")
            document_results = completed.get("documents")
            patterns = completed.get("patterns")
            if patterns:
                # attach as a labeled graph-evidence record; make sure the graph section
                # renders in the evidence block even if the router skipped that layer
                graph_results = (graph_results or [])
                graph_results.append({"cross_dimensional_correlations": patterns})
                if "graph" not in plan["layers"]:
                    plan["layers"] = plan["layers"] + ["graph"]
        t_retrieval = time.perf_counter() - t1

    if retrieval_errors:
        plan["retrieval_errors"] = retrieval_errors

    t2 = time.perf_counter()
    result = synthesize_answer(question, plan, graph_results, structured_results, document_results)
    t_synth = time.perf_counter() - t2

    result["retrieval_plan"] = plan
    result["retrieval_errors"] = retrieval_errors
    result["latency"] = {
        "routing_s": round(t_route, 2),
        "retrieval_s": round(t_retrieval, 2),
        "synthesis_s": round(t_synth, 2),
        "total_s": round(time.perf_counter() - t0, 2),
        "cache_hit": False,
    }
    # Do not turn a transient provider outage into a five-minute cached outage.
    if result.get("model_used") != "error" and not retrieval_errors:
        _cache_put(question, result)
    return result


# ---------------------------------------------------------------------------
# end-to-end test harness
# ---------------------------------------------------------------------------
TEST_QUESTIONS = [
    "How many coils failed quality testing?",
    "Which equipment produced coil C10234?",
    "Why did the Reheating Furnace fail last month?",
    "What does IS 2062 cover?",
    "Is everything okay?",
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for q in TEST_QUESTIONS:
        out = ask_synapse(q)
        plan = out["retrieval_plan"]
        lat = out["latency"]
        tier = plan["tier"] + (f"/{plan.get('tier3_source','')}" if plan["tier"] == "tier3" else "")
        rows.append((q, tier, plan["layers"], out["model_used"], out["answer"], lat))

        print("=" * 96)
        print(f"Q: {q}")
        print(f"  plan      : tier={tier} layers={plan['layers']} confidence={plan['confidence']}")
        print(f"  model     : {out['model_used']}")
        print(f"  sources   : {out['sources']}")
        print(f"  latency   : route={lat['routing_s']}s retrieve={lat['retrieval_s']}s "
              f"synthesize={lat['synthesis_s']}s TOTAL={lat['total_s']}s")
        print("  answer:")
        print("    " + out["answer"].replace("\n", "\n    "))
        print()

    print("=" * 96)
    print("END-TO-END SUMMARY -- ask_synapse()")
    print("=" * 96)
    for q, tier, layers, model, answer, lat in rows:
        one_line = " ".join(answer.split())
        one_line = one_line[:90] + ("..." if len(one_line) > 90 else "")
        print(f"  Q: {q}")
        print(f"     tier={tier:<20} layers={','.join(layers):<26} model={model}")
        print(f"     total={lat['total_s']}s (route {lat['routing_s']} / retrieve {lat['retrieval_s']} / synth {lat['synthesis_s']})")
        print(f"     A: {one_line}")
    slowest = max(rows, key=lambda r: r[5]["total_s"])
    print(f"\n  slowest question: {slowest[0]!r} at {slowest[5]['total_s']}s -- pace the demo accordingly.")
