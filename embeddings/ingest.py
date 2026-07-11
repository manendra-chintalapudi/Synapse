"""
Ingest the pre-chunked documents into the Chroma vector store.

Loads all chunk JSON files from data/unstructured/chunks/, builds one LangChain Document per
chunk, and adds them in a single batch keyed by chunk_id (so re-running upserts rather than
duplicates). Embeddings only -- no LLM calls.
"""
import glob
import json

from langchain_core.documents import Document

from vector_store import ROOT, COLLECTION_NAME, get_client, get_vectorstore

CHUNKS_DIR = ROOT / "data" / "unstructured" / "chunks"


def load_chunk_documents():
    """Return (documents, ids) built from every chunk record on disk."""
    documents, ids = [], []
    for path in sorted(glob.glob(str(CHUNKS_DIR / "*.json"))):
        with open(path, encoding="utf-8") as f:
            chunks = json.load(f)
        for ch in chunks:
            md = ch["metadata"]
            documents.append(Document(
                page_content=ch["text"],
                metadata={
                    "source_document_id": ch["source_document_id"],
                    "doc_type": md["doc_type"],
                    "related_entity_id": md["related_entity_id"],
                    "source_file_path": md["source_file_path"],
                    "chunk_index": ch["chunk_index"],
                    "chunk_id": ch["chunk_id"],
                },
            ))
            ids.append(ch["chunk_id"])
    return documents, ids


def main():
    client = get_client()
    vs = get_vectorstore(client)

    documents, ids = load_chunk_documents()
    assert len(ids) == len(set(ids)), "duplicate chunk_id detected -- ids must be unique"
    print(f"[ingest] Loaded {len(documents)} chunk documents from {CHUNKS_DIR}")

    # single batch add; explicit ids => idempotent upsert on re-run
    vs.add_documents(documents=documents, ids=ids)

    # persist (PersistentClient auto-persists on write; call .persist() only if available)
    if hasattr(vs, "persist"):
        vs.persist()

    count = client.get_collection(COLLECTION_NAME).count()
    print(f"[ingest] Ingested {len(documents)} documents. "
          f"Collection '{COLLECTION_NAME}' now holds {count} vectors.")
    return count


if __name__ == "__main__":
    main()
