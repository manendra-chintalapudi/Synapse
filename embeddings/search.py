"""
Similarity search over the Synapse Chroma vector store.

search(query, k, filter) -> list of {text, metadata, score}
  - score is the Chroma cosine distance (LOWER = more similar; 0 == identical).
  - filter is an optional metadata equality dict, e.g. {"doc_type": "sop"}.
Embeddings only -- no LLM calls.
"""
from vector_store import get_vectorstore

_vs = None


def _store():
    global _vs
    if _vs is None:
        _vs = get_vectorstore(announce=False)
    return _vs


def _to_where(flt):
    """Translate a plain equality dict into a Chroma 'where' clause.
    Single key -> {k: v}; multiple keys -> {'$and': [{k: v}, ...]}."""
    if not flt:
        return None
    if len(flt) == 1:
        return dict(flt)
    return {"$and": [{k: v} for k, v in flt.items()]}


def search(query: str, k: int = 5, filter: dict = None):
    """Return the top-k chunks for `query`, optionally filtered by metadata."""
    vs = _store()
    results = vs.similarity_search_with_score(query, k=k, filter=_to_where(filter))
    return [
        {"text": doc.page_content, "metadata": doc.metadata, "score": float(score)}
        for doc, score in results
    ]


if __name__ == "__main__":
    queries = [
        "hot rolling mill startup procedure",
        "why did the coiler fail",
        "IS 2062 structural steel grade",
    ]
    for q in queries:
        print("=" * 78)
        print(f"QUERY: {q!r}   (top-3; score = cosine distance, lower is closer)")
        print("=" * 78)
        for r in search(q, k=3):
            m = r["metadata"]
            snippet = " ".join(r["text"].split())[:100]
            print(f"  {m['chunk_id']:<18} score={r['score']:.4f}  [{m['doc_type']}]  {snippet}")
        print()
