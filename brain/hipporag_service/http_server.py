"""HippoRAG HTTP Microservice — S3

FastAPI server exposing the KnowledgeGraphService (HippoRAG) over HTTP.
Port: 8102

Endpoints:
    GET  /health   — Health check (Neo4j + Qdrant connectivity)
    POST /retrieve — Knowledge graph search with PPR algorithm
    POST /ingest   — Ingest text into Neo4j + Qdrant
    GET  /stats    — Graph statistics (entity/relation/pattern counts)
"""

import os
import sys
import logging
import traceback
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Path setup: project root is 3 levels up from this file
#   brain/hipporag_service/http_server.py -> project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Override brain config with environment variables at import time
# ---------------------------------------------------------------------------
_neo4j_uri = os.environ.get("NEO4J_URI")
_neo4j_password = os.environ.get("NEO4J_PASSWORD")
_qdrant_url = os.environ.get("QDRANT_URL")


def _override_config():
    """Patch the cached config dict with env-var overrides (if set)."""
    try:
        from brain.shared.config import load_config
        cfg = load_config()

        if _neo4j_uri and "neo4j" in cfg:
            cfg["neo4j"]["uri"] = _neo4j_uri
        if _neo4j_password and "neo4j" in cfg:
            cfg["neo4j"]["password"] = _neo4j_password
        if _qdrant_url and "qdrant" in cfg:
            cfg["qdrant"]["url"] = _qdrant_url
    except Exception:
        pass  # Config not yet available — will use defaults


_override_config()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("hipporag_service")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="HippoRAG Microservice",
    description="Knowledge Graph retrieval and ingestion (S3) via HTTP",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=100, description="Max results to return")


class RetrieveResultItem(BaseModel):
    entity: str
    type: str
    relations: list
    score: float
    context: Optional[str] = ""
    source: Optional[str] = ""


class RetrieveResponse(BaseModel):
    results: List[RetrieveResultItem]
    count: int


class IngestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to ingest into the knowledge graph")


class IngestResponse(BaseModel):
    entities_created: int
    relations_created: int
    embedding_stored: bool
    entities: Optional[List[str]] = None


class StatsResponse(BaseModel):
    entities: int
    relations: int
    patterns: int


class HealthResponse(BaseModel):
    status: str
    neo4j: str
    qdrant: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Structured error handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check — tests Neo4j and Qdrant connectivity."""
    neo4j_status = "disconnected"
    qdrant_status = "disconnected"

    # Neo4j
    try:
        from brain.shared.connections import get_neo4j
        driver = get_neo4j()
        driver.verify_connectivity()
        neo4j_status = "connected"
    except Exception as e:
        neo4j_status = f"error: {e}"

    # Qdrant
    try:
        from brain.shared.connections import get_qdrant
        client = get_qdrant()
        client.get_collections()
        qdrant_status = "connected"
    except Exception as e:
        qdrant_status = f"error: {e}"

    overall = "healthy" if neo4j_status == "connected" and qdrant_status == "connected" else "degraded"

    return HealthResponse(status=overall, neo4j=neo4j_status, qdrant=qdrant_status)


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest):
    """Knowledge graph search with PPR algorithm.

    Calls get_knowledge_graph_service().retrieve(query, top_k).
    Returns a list of results with entity, type, relations, and score.
    """
    try:
        from brain.shared.factory import get_knowledge_graph_service
        svc = get_knowledge_graph_service()
        results = svc.retrieve(query=req.query, top_k=req.top_k)
        return RetrieveResponse(results=results, count=len(results))
    except ConnectionError as e:
        logger.error("Connection error during retrieve: %s", e)
        raise HTTPException(
            status_code=503,
            detail={"error": "service_unavailable", "detail": str(e)},
        )
    except Exception as e:
        logger.error("Error during retrieve: %s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": "retrieve_failed", "detail": str(e)},
        )


@app.post("/ingest", response_model=IngestResponse)
async def ingest(req: IngestRequest):
    """Ingest text into the knowledge graph (Neo4j entities/relations + Qdrant embeddings).

    Calls get_knowledge_graph_service().ingest(text).
    Returns counts of entities created, relations created, and whether the embedding was stored.
    """
    try:
        from brain.shared.factory import get_knowledge_graph_service
        svc = get_knowledge_graph_service()
        result = svc.ingest(text=req.text)
        return IngestResponse(**result)
    except ConnectionError as e:
        logger.error("Connection error during ingest: %s", e)
        raise HTTPException(
            status_code=503,
            detail={"error": "service_unavailable", "detail": str(e)},
        )
    except Exception as e:
        logger.error("Error during ingest: %s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": "ingest_failed", "detail": str(e)},
        )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Graph statistics — counts of entities, relations, and patterns from Neo4j."""
    try:
        from brain.shared.connections import get_neo4j
        driver = get_neo4j()

        entities_count = 0
        relations_count = 0
        patterns_count = 0

        with driver.session() as session:
            # Count entities
            result = session.run("MATCH (e:Entity) RETURN count(e) AS cnt")
            record = result.single()
            if record:
                entities_count = record["cnt"]

            # Count relations
            result = session.run("MATCH (:Entity)-[r]->(:Entity) RETURN count(r) AS cnt")
            record = result.single()
            if record:
                relations_count = record["cnt"]

            # Count patterns
            result = session.run("MATCH (p:Pattern) RETURN count(p) AS cnt")
            record = result.single()
            if record:
                patterns_count = record["cnt"]

        return StatsResponse(
            entities=entities_count,
            relations=relations_count,
            patterns=patterns_count,
        )
    except ConnectionError as e:
        logger.error("Connection error during stats: %s", e)
        raise HTTPException(
            status_code=503,
            detail={"error": "service_unavailable", "detail": str(e)},
        )
    except Exception as e:
        logger.error("Error during stats: %s", traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={"error": "stats_failed", "detail": str(e)},
        )


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8102)
