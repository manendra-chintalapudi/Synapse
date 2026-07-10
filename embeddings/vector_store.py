"""
Vector store setup for the Synapse RAG layer.

Embeddings + storage only -- NO LLM calls anywhere.

- Persistent Chroma client at synapse/data/chroma_db/
- Embedding model: sentence-transformers/all-MiniLM-L6-v2 (384-dim), chosen for speed on a
  small (135-chunk), domain-narrow (steel-plant) corpus where a larger model wouldn't
  meaningfully improve retrieval.
- A langchain_chroma.Chroma vectorstore wraps the persistent client, collection
  "synapse_documents", using cosine distance.
"""
import os
from pathlib import Path

# quiet, offline-friendly telemetry settings (set before importing the libs)
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

ROOT = Path(__file__).resolve().parent.parent           # -> synapse/
CHROMA_PATH = str(ROOT / "data" / "chroma_db")
COLLECTION_NAME = "synapse_documents"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384

_embeddings = None


def get_embeddings():
    """Cached HuggingFace MiniLM embedding function (local model, no API calls)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    return _embeddings


def get_client():
    """Persistent Chroma client rooted at data/chroma_db/."""
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH, settings=Settings(anonymized_telemetry=False))


def _collection_names(client):
    return [getattr(c, "name", c) for c in client.list_collections()]


def get_vectorstore(client=None, announce=True):
    """Create/load the LangChain Chroma vectorstore over the persistent client.

    LangChain's wrapper uses get-or-create semantics, so if a raw-chromadb collection
    named 'synapse_documents' already exists at this path from an earlier ingestion pass,
    it is REUSED (same underlying collection) rather than rebuilt. This is stated at call time.
    """
    client = client or get_client()
    existed = COLLECTION_NAME in _collection_names(client)
    count = client.get_collection(COLLECTION_NAME).count() if existed else 0

    if announce:
        if existed and count > 0:
            print(f"[vector_store] REUSING existing raw-chromadb collection "
                  f"'{COLLECTION_NAME}' at {CHROMA_PATH} ({count} vectors) via the LangChain wrapper "
                  f"(get-or-create; not rebuilt).")
        elif existed:
            print(f"[vector_store] Found existing but EMPTY collection '{COLLECTION_NAME}' at "
                  f"{CHROMA_PATH} -- will populate it.")
        else:
            print(f"[vector_store] No existing collection at {CHROMA_PATH} -- building "
                  f"'{COLLECTION_NAME}' FRESH via the LangChain wrapper.")

    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        collection_metadata={"hnsw:space": "cosine"},
    )


if __name__ == "__main__":
    c = get_client()
    vs = get_vectorstore(c)
    print(f"model={MODEL_NAME} dim={EMBED_DIM} collection={COLLECTION_NAME} path={CHROMA_PATH}")
