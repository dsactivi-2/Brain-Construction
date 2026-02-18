"""RAG API — REST wrapper for the brain system's multi-source retrieval router (S4).

Exposes the brain's search capabilities over HTTP on port 8100.
Used by the multi-agent system to query Qdrant (S2), Neo4j (S3),
PostgreSQL (S6), and the unified retrieval router (S4).
"""

import os
import sys
import traceback
from typing import List, Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup — make brain package importable
# ---------------------------------------------------------------------------
PROJECT_DIR = os.environ.get(
    "PROJECT_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ---------------------------------------------------------------------------
# Override brain config with environment variables (before any brain import)
# ---------------------------------------------------------------------------
_env_overrides_applied = False


def _apply_env_overrides():
    """Patch the in-memory config dict returned by brain.shared.config.load_config
    so that connection factories pick up Docker/compose env vars automatically.

    Called once at startup, idempotent.
    """
    global _env_overrides_applied
    if _env_overrides_applied:
        return
    _env_overrides_applied = True

    from brain.shared.config import load_config
    try:
        cfg = load_config()
    except FileNotFoundError:
        # If databases.yaml is missing we still want the server to start;
        # the individual service factories will fail gracefully.
        return

    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")
    if neo4j_uri:
        cfg.setdefault("neo4j", {})["uri"] = neo4j_uri
    if neo4j_password:
        cfg.setdefault("neo4j", {})["password"] = neo4j_password

    qdrant_url = os.environ.get("QDRANT_URL")
    if qdrant_url:
        cfg.setdefault("qdrant", {})["url"] = qdrant_url

    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        cfg.setdefault("redis", {})["url"] = redis_url

    recall_db_url = os.environ.get("RECALL_DB_URL")
    if recall_db_url:
        cfg.setdefault("recall_memory", {})["url"] = recall_db_url


_apply_env_overrides()

# ---------------------------------------------------------------------------
# Lazy service accessors (import factory only after path + config are ready)
# ---------------------------------------------------------------------------
from brain.shared.factory import (  # noqa: E402
    get_retrieval_service,
    get_semantic_memory_service,
    get_knowledge_graph_service,
    get_conversation_service,
    get_identity_service,
)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RAG API",
    description="REST wrapper for the brain system's multi-source retrieval router",
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class MemorySearchRequest(BaseModel):
    query: str
    scopes: Optional[List[str]] = None
    top_k: int = 5
    min_score: float = 0.5


class MemoryStoreRequest(BaseModel):
    text: str
    scope: str = "projekt"
    type: str = "fakt"
    priority: int = 5


class GraphRetrieveRequest(BaseModel):
    query: str
    top_k: int = 5


class GraphIngestRequest(BaseModel):
    text: str


class ConversationSearchRequest(BaseModel):
    query: str
    limit: int = 10


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _error(message: str, status: int = 500):
    """Return a structured JSON error response."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status,
        content={"error": message, "detail": traceback.format_exc()},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Health check — returns service status and reachable backends."""
    status = {"status": "ok", "service": "rag-api", "port": 8100}
    backends = {}

    # Check Qdrant
    try:
        from brain.shared.connections import get_qdrant
        get_qdrant().get_collections()
        backends["qdrant"] = "connected"
    except Exception:
        backends["qdrant"] = "unavailable"

    # Check Neo4j
    try:
        from brain.shared.connections import get_neo4j
        get_neo4j().verify_connectivity()
        backends["neo4j"] = "connected"
    except Exception:
        backends["neo4j"] = "unavailable"

    # Check Redis
    try:
        from brain.shared.connections import get_redis
        get_redis().ping()
        backends["redis"] = "connected"
    except Exception:
        backends["redis"] = "unavailable"

    # Check PostgreSQL
    try:
        from brain.shared.connections import get_postgres
        get_postgres().cursor().execute("SELECT 1")
        backends["postgresql"] = "connected"
    except Exception:
        backends["postgresql"] = "unavailable"

    status["backends"] = backends
    return status


@app.post("/search")
def search(req: SearchRequest):
    """Unified multi-source retrieval via S4 router.

    Classifies the query and searches across S1 (Core Memory),
    S2 (Qdrant), S3 (Neo4j), and S6 (PostgreSQL) as appropriate.
    """
    try:
        service = get_retrieval_service()
        return service.route(query=req.query, top_k=req.top_k)
    except Exception as e:
        return _error(f"Search failed: {e}")


@app.post("/memory/search")
def memory_search(req: MemorySearchRequest):
    """Semantic memory search (S2 — Qdrant vector search)."""
    try:
        service = get_semantic_memory_service()
        results = service.search(
            query=req.query,
            scopes=req.scopes,
            top_k=req.top_k,
            min_score=req.min_score,
        )
        return {"results": results, "total": len(results)}
    except Exception as e:
        return _error(f"Memory search failed: {e}")


@app.post("/memory/store")
def memory_store(req: MemoryStoreRequest):
    """Store a new semantic memory (S2 — Qdrant with deduplication)."""
    try:
        service = get_semantic_memory_service()
        return service.store(
            text=req.text,
            scope=req.scope,
            type=req.type,
            priority=req.priority,
        )
    except Exception as e:
        return _error(f"Memory store failed: {e}")


@app.post("/graph/retrieve")
def graph_retrieve(req: GraphRetrieveRequest):
    """Knowledge graph retrieval (S3 — Neo4j + Qdrant PPR search)."""
    try:
        service = get_knowledge_graph_service()
        results = service.retrieve(query=req.query, top_k=req.top_k)
        return {"results": results, "total": len(results)}
    except Exception as e:
        return _error(f"Graph retrieve failed: {e}")


@app.post("/graph/ingest")
def graph_ingest(req: GraphIngestRequest):
    """Ingest text into the knowledge graph (S3 — Neo4j entities + Qdrant embeddings)."""
    try:
        service = get_knowledge_graph_service()
        return service.ingest(text=req.text)
    except Exception as e:
        return _error(f"Graph ingest failed: {e}")


@app.post("/conversation/search")
def conversation_search(req: ConversationSearchRequest):
    """Full-text conversation search (S6 — PostgreSQL recall memory)."""
    try:
        service = get_conversation_service()
        results = service.search(query=req.query, limit=req.limit)
        return {"results": results, "total": len(results)}
    except Exception as e:
        return _error(f"Conversation search failed: {e}")


@app.get("/core-memory")
def core_memory(block: Optional[str] = Query(default=None)):
    """Read core memory blocks (S1 — Redis + JSON).

    Without a block parameter returns all blocks.
    With ?block=USER returns only that block.
    """
    try:
        service = get_identity_service()
        return service.read(block=block)
    except Exception as e:
        return _error(f"Core memory read failed: {e}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
