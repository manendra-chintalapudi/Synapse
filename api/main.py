"""
Synapse / Maven demo API.

Thin FastAPI wrapper around ask_synapse() so the browser chat UI can drive the full
pipeline (router -> graph/Trino/Chroma retrieval -> synthesizer) live.

Run (from the repo root that contains the `synapse/` folder):
    uvicorn synapse.api.main:app --reload --port 8000
or (from inside synapse/):
    uvicorn api.main:app --reload --port 8000
or simply:
    python synapse/api/main.py
"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# make the pipeline + retrieval/embedding modules importable regardless of launch cwd
SYNAPSE_ROOT = Path(__file__).resolve().parent.parent          # -> synapse/
for _p in (SYNAPSE_ROOT, SYNAPSE_ROOT / "retrieval", SYNAPSE_ROOT / "embeddings",
           SYNAPSE_ROOT / "router", SYNAPSE_ROOT / "synthesizer"):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import ask_synapse, warm_up

FRONTEND = SYNAPSE_ROOT / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # pre-load the embedding model + vector store so the first real request is fast
    try:
        warm_up()
        print("[startup] warm_up complete — embedding model + vector store ready")
    except Exception as exc:                       # never block startup on warm-up
        print(f"[startup] warm_up failed (first query will be slower): {exc}")
    yield


app = FastAPI(title="Synapse / Maven Demo API", version="1.0", lifespan=lifespan)

# permissive CORS for local demo (file:// origin shows up as 'null')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.post("/api/ask")
def ask(req: AskRequest):
    """Run one question through the full Synapse pipeline. Never crashes the server."""
    question = (req.question or "").strip()
    if not question:
        return JSONResponse(status_code=400, content={"error": "question is empty"})
    try:
        return ask_synapse(question)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"{type(exc).__name__}: {exc}"})


# ---- health: is every dependency reachable? ----
def _neo4j_ok() -> bool:
    try:
        from graph_store import get_driver
        get_driver().verify_connectivity()
        return True
    except Exception:
        return False


def _trino_ok() -> bool:
    try:
        from structured_store import query_federated
        return query_federated("SELECT 1 AS ok")[0]["ok"] == 1
    except Exception:
        return False


def _chroma_ok() -> bool:
    try:
        from vector_store import get_client, COLLECTION_NAME
        return get_client().get_collection(COLLECTION_NAME).count() > 0
    except Exception:
        return False


@app.get("/api/health")
def health():
    neo4j, trino, chroma = _neo4j_ok(), _trino_ok(), _chroma_ok()
    return {
        "status": "ok" if all((neo4j, trino, chroma)) else "degraded",
        "neo4j": neo4j,
        "trino": trino,
        "chroma": chroma,
    }


# ---- serve the front-end from the same origin as the API ----
# (so one public tunnel exposes both the chat UI and /api/ask — no CORS, shareable)
@app.get("/")
def index():
    return FileResponse(FRONTEND / "chat.html")


@app.get("/chat.html")
def chat_page():
    return FileResponse(FRONTEND / "chat.html")


@app.get("/landing.html")
def landing_page():
    return FileResponse(FRONTEND / "landing.html")


app.mount("/assets", StaticFiles(directory=str(FRONTEND / "assets")), name="assets")


if __name__ == "__main__":
    import uvicorn
    print("Starting Synapse/Maven API on http://localhost:8000  (POST /api/ask, GET /api/health)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
