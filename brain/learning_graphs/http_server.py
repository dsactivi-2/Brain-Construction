"""Learning Graphs HTTP Server — S5

FastAPI server for pattern recognition, consolidation, and decay/pruning.
Runs as a Docker microservice, accessed via docker network.
Scheduled tasks for consolidation (weekly) and decay (daily) via APScheduler.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup — project root is 3 levels up from this file
# (brain/learning_graphs/http_server.py -> project root)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("learning_graphs")

# ---------------------------------------------------------------------------
# Override brain config with env vars at startup
# ---------------------------------------------------------------------------


def _override_config_from_env():
    """Patch Neo4j connection settings from environment variables.

    This must run before any service is instantiated so that
    brain.shared.connections.get_neo4j() picks up the correct URI/password.
    """
    neo4j_uri = os.environ.get("NEO4J_URI")
    neo4j_password = os.environ.get("NEO4J_PASSWORD")

    if not neo4j_uri and not neo4j_password:
        return

    try:
        from brain.shared.config import load_config

        cfg = load_config()
        neo4j_cfg = cfg.get("neo4j", {})

        if neo4j_uri:
            neo4j_cfg["uri"] = neo4j_uri
            logger.info("Neo4j URI overridden from NEO4J_URI env var")

        if neo4j_password:
            neo4j_cfg["password"] = neo4j_password
            logger.info("Neo4j password overridden from NEO4J_PASSWORD env var")

        cfg["neo4j"] = neo4j_cfg
    except Exception as exc:
        logger.warning("Could not override config from env vars: %s", exc)


_override_config_from_env()

# ---------------------------------------------------------------------------
# Schedule config from databases.yaml
# ---------------------------------------------------------------------------


def _load_schedule_config() -> dict:
    """Read learning_graphs schedule settings from databases.yaml.

    Returns a dict with keys:
        consolidation_cron  — cron expression string (default "0 3 * * 0")
        decay_cron          — cron expression string (default "0 4 * * *")
    """
    defaults = {
        "consolidation_cron": "0 3 * * 0",
        "decay_cron": "0 4 * * *",
    }
    try:
        from brain.shared.config import load_config

        cfg = load_config()
        lg_cfg = cfg.get("learning_graphs", {})
        if lg_cfg:
            if lg_cfg.get("consolidation_schedule"):
                defaults["consolidation_cron"] = lg_cfg["consolidation_schedule"]
            if lg_cfg.get("decay_schedule"):
                defaults["decay_cron"] = lg_cfg["decay_schedule"]
    except Exception as exc:
        logger.warning("Could not load schedule config from databases.yaml: %s", exc)

    return defaults


# ---------------------------------------------------------------------------
# APScheduler — background scheduled tasks
# ---------------------------------------------------------------------------


def _run_consolidation():
    """Scheduled task: consolidation (weekly)."""
    logger.info("Scheduled consolidation task started")
    try:
        from brain.shared.factory import get_knowledge_graph_service

        result = get_knowledge_graph_service().consolidate()
        logger.info("Scheduled consolidation completed: %s", result)
    except Exception as exc:
        logger.error("Scheduled consolidation failed: %s", exc)


def _run_decay():
    """Scheduled task: decay/prune (daily)."""
    logger.info("Scheduled decay/prune task started")
    try:
        from brain.shared.factory import get_knowledge_graph_service

        result = get_knowledge_graph_service().decay_prune()
        logger.info("Scheduled decay/prune completed: %s", result)
    except Exception as exc:
        logger.error("Scheduled decay/prune failed: %s", exc)


def _parse_cron_field(cron_expr: str) -> dict:
    """Parse a 5-field cron expression into APScheduler CronTrigger kwargs.

    Fields: minute hour day_of_month month day_of_week
    Returns dict suitable for scheduler.add_job(..., trigger='cron', **kwargs).
    """
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression (need 5 fields): {cron_expr}")

    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4],
    }


def _start_scheduler():
    """Create and start the APScheduler BackgroundScheduler."""
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler(timezone="UTC")

    schedule_cfg = _load_schedule_config()

    # Consolidation — weekly (default: Sunday 03:00 UTC)
    try:
        cron_kwargs = _parse_cron_field(schedule_cfg["consolidation_cron"])
        scheduler.add_job(_run_consolidation, trigger="cron", **cron_kwargs, id="consolidation")
        logger.info(
            "Consolidation scheduled: %s (cron: %s)",
            cron_kwargs,
            schedule_cfg["consolidation_cron"],
        )
    except Exception as exc:
        logger.error("Failed to schedule consolidation: %s", exc)

    # Decay/Prune — daily (default: 04:00 UTC)
    try:
        cron_kwargs = _parse_cron_field(schedule_cfg["decay_cron"])
        scheduler.add_job(_run_decay, trigger="cron", **cron_kwargs, id="decay_prune")
        logger.info(
            "Decay/prune scheduled: %s (cron: %s)",
            cron_kwargs,
            schedule_cfg["decay_cron"],
        )
    except Exception as exc:
        logger.error("Failed to schedule decay/prune: %s", exc)

    scheduler.start()
    logger.info("APScheduler started with %d jobs", len(scheduler.get_jobs()))
    return scheduler


# ---------------------------------------------------------------------------
# FastAPI lifespan — start/stop scheduler alongside uvicorn
# ---------------------------------------------------------------------------

_scheduler = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    global _scheduler
    logger.info("Learning Graphs service starting up")
    _scheduler = _start_scheduler()
    yield
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Learning Graphs — S5",
    description="Pattern recognition, consolidation, and decay/pruning for the brain system.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class UpdateRequest(BaseModel):
    session_id: str
    entities: List[str]
    tools_used: List[str]


class UpdateResponse(BaseModel):
    patterns_found: int
    patterns_updated: int
    session_id: str


class ConsolidateResponse(BaseModel):
    merged: int
    deleted: int


class DecayResponse(BaseModel):
    decayed: int
    archived: int


class HealthResponse(BaseModel):
    status: str
    neo4j: str
    timestamp: str


class PatternStats(BaseModel):
    total: int
    high: int
    medium: int
    low: int
    weak: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check — test Neo4j connection."""
    neo4j_status = "unknown"
    try:
        from brain.shared.connections import get_neo4j

        driver = get_neo4j()
        driver.verify_connectivity()
        neo4j_status = "connected"
    except Exception as exc:
        neo4j_status = f"error: {exc}"

    status = "healthy" if neo4j_status == "connected" else "degraded"
    return HealthResponse(
        status=status,
        neo4j=neo4j_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/update", response_model=UpdateResponse, responses={500: {"model": ErrorResponse}})
async def update(request: UpdateRequest):
    """Update learning graph patterns from session data."""
    try:
        from brain.shared.factory import get_knowledge_graph_service

        session_data = {
            "session_id": request.session_id,
            "entities": request.entities,
            "tools_used": request.tools_used,
        }
        result = get_knowledge_graph_service().update_patterns(session_data=session_data)
        logger.info(
            "Patterns updated for session %s: found=%d, updated=%d",
            request.session_id,
            result.get("patterns_found", 0),
            result.get("patterns_updated", 0),
        )
        return UpdateResponse(**result)
    except Exception as exc:
        logger.error("Update failed: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "update_failed", "detail": str(exc)},
        )


@app.post("/consolidate", response_model=ConsolidateResponse, responses={500: {"model": ErrorResponse}})
async def consolidate():
    """Consolidate weak pattern nodes."""
    try:
        from brain.shared.factory import get_knowledge_graph_service

        result = get_knowledge_graph_service().consolidate()
        logger.info("Consolidation completed: merged=%d, deleted=%d", result.get("merged", 0), result.get("deleted", 0))
        return ConsolidateResponse(**result)
    except Exception as exc:
        logger.error("Consolidation failed: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "consolidation_failed", "detail": str(exc)},
        )


@app.post("/decay", response_model=DecayResponse, responses={500: {"model": ErrorResponse}})
async def decay():
    """Run daily score decay and archive old entries."""
    try:
        from brain.shared.factory import get_knowledge_graph_service

        result = get_knowledge_graph_service().decay_prune()
        logger.info("Decay/prune completed: decayed=%d, archived=%d", result.get("decayed", 0), result.get("archived", 0))
        return DecayResponse(**result)
    except Exception as exc:
        logger.error("Decay/prune failed: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "decay_failed", "detail": str(exc)},
        )


@app.get("/patterns", response_model=PatternStats, responses={500: {"model": ErrorResponse}})
async def patterns():
    """Return current pattern statistics from Neo4j.

    Counts patterns by score range:
        high   — score >= 0.8
        medium — 0.5 <= score < 0.8
        low    — 0.2 <= score < 0.5
        weak   — score < 0.2
    """
    try:
        from brain.shared.connections import get_neo4j

        driver = get_neo4j()

        query = """
        MATCH (p:Pattern)
        RETURN
            count(p) AS total,
            sum(CASE WHEN p.score >= 0.8 THEN 1 ELSE 0 END) AS high,
            sum(CASE WHEN p.score >= 0.5 AND p.score < 0.8 THEN 1 ELSE 0 END) AS medium,
            sum(CASE WHEN p.score >= 0.2 AND p.score < 0.5 THEN 1 ELSE 0 END) AS low,
            sum(CASE WHEN p.score < 0.2 THEN 1 ELSE 0 END) AS weak
        """

        with driver.session() as session:
            result = session.run(query).single()
            if result:
                return PatternStats(
                    total=result["total"] or 0,
                    high=result["high"] or 0,
                    medium=result["medium"] or 0,
                    low=result["low"] or 0,
                    weak=result["weak"] or 0,
                )
            return PatternStats(total=0, high=0, medium=0, low=0, weak=0)

    except Exception as exc:
        logger.error("Pattern stats query failed: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "pattern_stats_failed", "detail": str(exc)},
        )


# ---------------------------------------------------------------------------
# Main — for direct execution (outside Docker, debugging)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8103"))
    uvicorn.run(app, host="0.0.0.0", port=port)
