"""Doc-Scanner Microservice — REST API on port 8101

Scans web documentation, extracts content, and ingests it into the
brain system (S2 Semantic Memory + S3 Knowledge Graph).

Endpoints:
    GET  /health     — Health check
    POST /scan       — Scan URL, chunk, store in S2 + S3
    POST /scan/text  — Ingest raw text, chunk, store in S2 + S3
    GET  /status     — Scan queue status
"""

import os
import sys
import time
import uuid
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Path setup — make brain imports available
# ---------------------------------------------------------------------------
PROJECT_DIR = os.environ.get("PYTHONPATH", os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("doc-scanner")

# ---------------------------------------------------------------------------
# Environment-driven config overrides for brain system
# ---------------------------------------------------------------------------
# The brain's shared/config.py reads from databases.yaml.  When running inside
# Docker the database hostnames differ (e.g. "qdrant" instead of "localhost").
# We patch os.environ so brain.shared.config / connections pick up the right
# values via their own env-var reading logic (CONFIG_DIR, BRAIN_DIR).
if os.environ.get("CONFIG_DIR") is None:
    os.environ["CONFIG_DIR"] = os.path.join(PROJECT_DIR, "config")
if os.environ.get("BRAIN_DIR") is None:
    os.environ["BRAIN_DIR"] = os.path.join(PROJECT_DIR, "brain")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Doc-Scanner",
    description="Scans web documentation and ingests into brain S2 + S3",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Internal communication URL (RAG API or other services)
# ---------------------------------------------------------------------------
RAG_API_URL = os.environ.get("RAG_API_URL", "http://localhost:8100")

# ---------------------------------------------------------------------------
# Scan tracking (in-memory)
# ---------------------------------------------------------------------------

class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


_scan_jobs: dict = {}  # scan_id -> {status, url/source, started, finished, result, error}


def _create_scan_job(source: str) -> str:
    """Register a new scan job and return its ID."""
    scan_id = str(uuid.uuid4())[:8]
    _scan_jobs[scan_id] = {
        "status": ScanStatus.PENDING,
        "source": source,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "result": None,
        "error": None,
    }
    return scan_id


def _finish_scan_job(scan_id: str, result: dict):
    """Mark scan job as completed."""
    if scan_id in _scan_jobs:
        _scan_jobs[scan_id]["status"] = ScanStatus.DONE
        _scan_jobs[scan_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
        _scan_jobs[scan_id]["result"] = result


def _fail_scan_job(scan_id: str, error: str):
    """Mark scan job as failed."""
    if scan_id in _scan_jobs:
        _scan_jobs[scan_id]["status"] = ScanStatus.ERROR
        _scan_jobs[scan_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
        _scan_jobs[scan_id]["error"] = error


# ---------------------------------------------------------------------------
# Brain service helpers (lazy-loaded singletons via factory)
# ---------------------------------------------------------------------------
_semantic_service = None
_knowledge_service = None


def _get_semantic_service():
    """Lazy-load SemanticMemoryService via brain factory."""
    global _semantic_service
    if _semantic_service is None:
        from brain.shared.factory import get_semantic_memory_service
        _semantic_service = get_semantic_memory_service()
    return _semantic_service


def _get_knowledge_service():
    """Lazy-load KnowledgeGraphService via brain factory."""
    global _knowledge_service
    if _knowledge_service is None:
        from brain.shared.factory import get_knowledge_graph_service
        _knowledge_service = get_knowledge_graph_service()
    return _knowledge_service


# ---------------------------------------------------------------------------
# Text extraction and chunking
# ---------------------------------------------------------------------------

def extract_text_from_html(html: str) -> str:
    """Strip HTML tags and extract meaningful text using BeautifulSoup.

    Removes script, style, nav, footer, and header elements to focus on
    the main content of the page.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "noscript", "iframe", "svg", "form"]):
        tag.decompose()

    # Extract text with newline separation
    text = soup.get_text(separator="\n", strip=True)

    # Collapse excessive whitespace / blank lines
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def chunk_text(text: str, max_words: int = 500) -> list[str]:
    """Split text into chunks of approximately *max_words* words.

    Strategy:
    1. Split by double-newline (paragraphs).
    2. Accumulate paragraphs until the word budget is reached.
    3. Yield the accumulated chunk and start the next one.
    4. If a single paragraph exceeds max_words, split it at word boundaries.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_words = 0

    for para in paragraphs:
        para_words = len(para.split())

        # If this single paragraph already exceeds the budget, split it
        if para_words > max_words:
            # Flush current chunk first
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_words = 0

            words = para.split()
            for i in range(0, len(words), max_words):
                sub = " ".join(words[i : i + max_words])
                chunks.append(sub)
            continue

        if current_words + para_words > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            current_words = 0

        current_chunk.append(para)
        current_words += para_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


# ---------------------------------------------------------------------------
# Core ingestion logic (shared between /scan and /scan/text)
# ---------------------------------------------------------------------------

def ingest_chunks(chunks: list[str], source: str, scope: str) -> dict:
    """Store chunks in S2 (Semantic Memory) and S3 (Knowledge Graph).

    Returns:
        Dict with chunks_stored, entities_found, and details lists.
    """
    chunks_stored = 0
    total_entities: list[str] = []
    store_details: list[dict] = []
    ingest_details: list[dict] = []

    sem_svc = _get_semantic_service()
    kg_svc = _get_knowledge_service()

    for idx, chunk in enumerate(chunks):
        # --- S2: Semantic Memory ---
        try:
            store_result = sem_svc.store(
                text=chunk,
                scope=scope,
                type="fakt",
                priority=5,
            )
            if store_result.get("stored"):
                chunks_stored += 1
            store_details.append({
                "chunk_index": idx,
                "stored": store_result.get("stored", False),
                "id": store_result.get("id"),
                "reason": store_result.get("reason"),
            })
        except Exception as exc:
            logger.warning("S2 store failed for chunk %d: %s", idx, exc)
            store_details.append({
                "chunk_index": idx,
                "stored": False,
                "error": str(exc),
            })

        # --- S3: Knowledge Graph ---
        try:
            ingest_result = kg_svc.ingest(chunk)
            entities = ingest_result.get("entities", [])
            total_entities.extend(entities)
            ingest_details.append({
                "chunk_index": idx,
                "entities_created": ingest_result.get("entities_created", 0),
                "relations_created": ingest_result.get("relations_created", 0),
                "entities": entities,
            })
        except Exception as exc:
            logger.warning("S3 ingest failed for chunk %d: %s", idx, exc)
            ingest_details.append({
                "chunk_index": idx,
                "error": str(exc),
            })

    # Deduplicate entity list
    unique_entities = list(set(total_entities))

    return {
        "chunks_stored": chunks_stored,
        "entities_found": len(unique_entities),
        "entities": unique_entities,
        "store_details": store_details,
        "ingest_details": ingest_details,
    }


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    url: str
    max_pages: int = 10
    scope: str = "projekt"


class ScanTextRequest(BaseModel):
    text: str
    source: str = "manual"
    scope: str = "projekt"


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Return structured JSON for unhandled exceptions."""
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check endpoint."""
    brain_status = "unknown"
    try:
        _get_semantic_service()
        _get_knowledge_service()
        brain_status = "connected"
    except Exception as exc:
        brain_status = f"error: {exc}"

    return {
        "status": "ok",
        "service": "doc-scanner",
        "version": "1.0.0",
        "brain": brain_status,
        "rag_api_url": RAG_API_URL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/scan")
async def scan_url(req: ScanRequest):
    """Fetch a URL, extract text, chunk it, and ingest into brain S2 + S3."""
    scan_id = _create_scan_job(req.url)
    _scan_jobs[scan_id]["status"] = ScanStatus.RUNNING

    try:
        # Fetch URL
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "DocScanner/1.0 (brain-system)"},
        ) as client:
            response = await client.get(req.url)
            response.raise_for_status()

        html = response.text

        # Extract text
        text = extract_text_from_html(html)
        if not text.strip():
            _fail_scan_job(scan_id, "No text content extracted from URL")
            raise HTTPException(
                status_code=422,
                detail={
                    "error": True,
                    "message": "No text content could be extracted from the URL",
                    "url": req.url,
                    "scan_id": scan_id,
                },
            )

        # Chunk
        chunks = chunk_text(text, max_words=500)
        logger.info("URL %s: extracted %d chars, %d chunks", req.url, len(text), len(chunks))

        # Limit to max_pages worth of chunks (rough heuristic: ~3 chunks per page)
        max_chunks = req.max_pages * 3
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]
            logger.info("Truncated to %d chunks (max_pages=%d)", max_chunks, req.max_pages)

        # Ingest
        result = ingest_chunks(chunks, source=req.url, scope=req.scope)

        response_data = {
            "url": req.url,
            "pages_scanned": min(req.max_pages, max(1, len(chunks) // 3)),
            "chunks_stored": result["chunks_stored"],
            "entities_found": result["entities_found"],
            "total_chunks": len(chunks),
            "entities": result["entities"][:50],  # Limit entity list in response
            "scan_id": scan_id,
        }

        _finish_scan_job(scan_id, response_data)
        return response_data

    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:
        error_msg = f"HTTP {exc.response.status_code} fetching {req.url}"
        _fail_scan_job(scan_id, error_msg)
        raise HTTPException(
            status_code=502,
            detail={
                "error": True,
                "message": error_msg,
                "url": req.url,
                "scan_id": scan_id,
            },
        )
    except httpx.RequestError as exc:
        error_msg = f"Request error fetching {req.url}: {exc}"
        _fail_scan_job(scan_id, error_msg)
        raise HTTPException(
            status_code=502,
            detail={
                "error": True,
                "message": error_msg,
                "url": req.url,
                "scan_id": scan_id,
            },
        )
    except Exception as exc:
        error_msg = f"Scan failed: {exc}"
        _fail_scan_job(scan_id, error_msg)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": error_msg,
                "url": req.url,
                "scan_id": scan_id,
            },
        )


@app.post("/scan/text")
async def scan_text(req: ScanTextRequest):
    """Ingest raw text: chunk and store in brain S2 + S3."""
    scan_id = _create_scan_job(req.source)
    _scan_jobs[scan_id]["status"] = ScanStatus.RUNNING

    try:
        if not req.text.strip():
            _fail_scan_job(scan_id, "Empty text provided")
            raise HTTPException(
                status_code=422,
                detail={
                    "error": True,
                    "message": "Text must not be empty",
                    "source": req.source,
                    "scan_id": scan_id,
                },
            )

        # Chunk
        chunks = chunk_text(req.text, max_words=500)
        logger.info("Text source '%s': %d chars, %d chunks", req.source, len(req.text), len(chunks))

        # Ingest
        result = ingest_chunks(chunks, source=req.source, scope=req.scope)

        response_data = {
            "source": req.source,
            "chunks_stored": result["chunks_stored"],
            "entities_found": result["entities_found"],
            "total_chunks": len(chunks),
            "entities": result["entities"][:50],
            "scan_id": scan_id,
        }

        _finish_scan_job(scan_id, response_data)
        return response_data

    except HTTPException:
        raise
    except Exception as exc:
        error_msg = f"Text scan failed: {exc}"
        _fail_scan_job(scan_id, error_msg)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "message": error_msg,
                "source": req.source,
                "scan_id": scan_id,
            },
        )


@app.get("/status")
async def scan_status():
    """Show scan queue status — all tracked scan jobs."""
    total = len(_scan_jobs)
    running = sum(1 for j in _scan_jobs.values() if j["status"] == ScanStatus.RUNNING)
    done = sum(1 for j in _scan_jobs.values() if j["status"] == ScanStatus.DONE)
    failed = sum(1 for j in _scan_jobs.values() if j["status"] == ScanStatus.ERROR)

    # Most recent 20 jobs
    recent = dict(list(_scan_jobs.items())[-20:])

    return {
        "total_scans": total,
        "running": running,
        "done": done,
        "failed": failed,
        "recent_jobs": recent,
    }


# ---------------------------------------------------------------------------
# Entrypoint (for direct execution)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8101, reload=True)
