"""
Synapse / Maven demo API.

Thin FastAPI wrapper around ask_synapse() so the browser chat UI can drive the full
pipeline (router -> graph[Neo4j] / structured[DuckDB] / documents[Chroma] retrieval ->
synthesizer) live.

Run (from inside synapse/):
    uvicorn api.main:app --host 0.0.0.0 --port 8000      # Railway: --port $PORT
or simply:
    python api/main.py

Environment (see .env.example): NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD, OPENROUTER_API_KEY,
ALLOWED_ORIGINS (CORS), and optional DUCKDB_DIR / CHROMA_DIR data paths.
"""
import os
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

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pipeline import ask_synapse, warm_up
from api.auth import Identity, require_user
from api.compliance_store import get_standard_detail, get_summary as get_compliance_summary
from api.knowledge_transfer import extract_knowledge_cards, next_interview_turn
from api.rca_store import get_failure_detail, get_failures, get_summary

FRONTEND = SYNAPSE_ROOT / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Railway must become ready before loading the relatively large embedding stack.
    # Keep eager warm-up opt-in; the first document query initializes it on demand.
    if os.environ.get("WARM_UP_ON_STARTUP", "false").lower() not in {"1", "true", "yes"}:
        yield
        return
    # pre-load the embedding model + vector store so the first real request is fast
    try:
        warm_up()
        print("[startup] warm_up complete — embedding model + vector store ready")
    except Exception as exc:                       # never block startup on warm-up
        print(f"[startup] warm_up failed (first query will be slower): {exc}")
    yield


app = FastAPI(title="Synapse / Maven Demo API", version="1.0", lifespan=lifespan)

# CORS: allow the Vercel frontend origin(s). ALLOWED_ORIGINS is a comma-separated list, or
# "*" (default) to allow any origin — tighten to the real Vercel domain(s) in production.
# (file:// origin shows up as 'null'; "*" covers it for local demo use.)
_origins_env = os.environ.get("ALLOWED_ORIGINS", "*").strip()
ALLOW_ORIGINS = ["*"] if _origins_env in ("", "*") else [o.strip() for o in _origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class InterviewEntry(BaseModel):
    question: str
    answer: str


class KnowledgeTransferRequest(BaseModel):
    profile: dict
    plan: list[str]
    transcript: list[InterviewEntry] = Field(default_factory=list)


class KnowledgeExtractionRequest(BaseModel):
    profile: dict
    transcript: list[InterviewEntry]


@app.post("/api/ask")
def ask(req: AskRequest, identity: Identity = Depends(require_user)):
    """Run one question through the full Synapse pipeline. Never crashes the server."""
    question = (req.question or "").strip()
    if not question:
        return JSONResponse(status_code=400, content={"error": "question is empty"})
    try:
        return ask_synapse(question)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"{type(exc).__name__}: {exc}"})


@app.post("/api/knowledge-transfer/interview")
def knowledge_transfer_interview(req: KnowledgeTransferRequest, identity: Identity = Depends(require_user)):
    """Generate one short, spoken interview turn with Tencent HY3 on OpenRouter."""
    try:
        message = next_interview_turn(req.profile, req.plan, [entry.model_dump() for entry in req.transcript])
        return {"message": message, "complete": "[INTERVIEW_COMPLETE]" in message, "model": "tencent/hy3:free"}
    except Exception as exc:
        return JSONResponse(status_code=502, content={"error": f"{type(exc).__name__}: {exc}"})


@app.post("/api/knowledge-transfer/extract")
def knowledge_transfer_extract(req: KnowledgeExtractionRequest, identity: Identity = Depends(require_user)):
    """Extract unverified knowledge cards from the completed transcript."""
    if not req.transcript:
        return JSONResponse(status_code=400, content={"error": "the interview transcript is empty"})
    try:
        cards = extract_knowledge_cards(req.profile, [entry.model_dump() for entry in req.transcript])
        return {"cards": cards, "model": "tencent/hy3:free"}
    except Exception as exc:
        return JSONResponse(status_code=502, content={"error": f"{type(exc).__name__}: {exc}"})


# ---- RCA & Failures: direct read-only Neo4j browsing (never calls the synthesizer) ----
@app.get("/api/rca/summary")
def rca_summary(identity: Identity = Depends(require_user)):
    return get_summary()


@app.get("/api/rca/failures")
def rca_failures(
    equipment_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    severity: str | None = None,
    has_rca: bool | None = None,
    sort: str = Query(default="recent", pattern="^(recent|severe|recurring)$"),
    identity: Identity = Depends(require_user),
):
    return get_failures(
        equipment_type=equipment_type,
        date_from=date_from,
        date_to=date_to,
        severity=severity,
        has_rca=has_rca,
        sort=sort,
    )


@app.get("/api/rca/failures/{failure_id}")
def rca_failure_detail(failure_id: str, identity: Identity = Depends(require_user)):
    detail = get_failure_detail(failure_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Failure {failure_id} not found")
    return detail


# ---- Compliance: direct read-only Neo4j patterns (never calls the synthesizer) ----
@app.get("/api/compliance/summary")
def compliance_summary(identity: Identity = Depends(require_user)):
    return get_compliance_summary()


@app.get("/api/compliance/standards")
def compliance_standards(identity: Identity = Depends(require_user)):
    summary = get_compliance_summary()
    return {"count": len(summary["standards"]), "standards": summary["standards"]}


@app.get("/api/compliance/standards/{family_id}")
def compliance_standard_detail(family_id: str, identity: Identity = Depends(require_user)):
    detail = get_standard_detail(family_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Compliance standard {family_id} not found")
    return detail


# ---- health: is every dependency reachable? ----
def _neo4j_ok() -> bool:
    try:
        from graph_store import get_driver
        get_driver().verify_connectivity()
        return True
    except Exception:
        return False


def _dfs_ok() -> bool:
    try:
        from structured_store import query_federated       # direct DuckDB federation
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
    neo4j, dfs, chroma = _neo4j_ok(), _dfs_ok(), _chroma_ok()
    return {
        "status": "ok" if all((neo4j, dfs, chroma)) else "degraded",
        "neo4j": neo4j,
        "dfs": dfs,          # DuckDB federated structured store (was "trino")
        "chroma": chroma,
        "openrouter_configured": bool(os.environ.get("OPENROUTER_API_KEY", "").strip()),
    }


@app.get("/healthz")
def readiness():
    """Lightweight process readiness endpoint for Railway; no dependency probes."""
    return {"status": "ok"}


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


@app.get("/config.js")
def frontend_config():
    # runtime frontend config (window.SYNAPSE_API_URL); served locally, static on Vercel
    return FileResponse(FRONTEND / "config.js", media_type="text/javascript")


app.mount("/assets", StaticFiles(directory=str(FRONTEND / "assets")), name="assets")
UI_DIST = FRONTEND / "ui-dist"
if UI_DIST.exists():
    app.mount("/ui-dist", StaticFiles(directory=str(UI_DIST)), name="ui-dist")


if __name__ == "__main__":
    import uvicorn
    print("Starting Synapse/Maven API on http://localhost:8000  (POST /api/ask, GET /api/health)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
