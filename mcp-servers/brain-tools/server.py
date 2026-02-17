"""Brain-Tools MCP Server — Cloud Code Team 02.26 (DDD v3)

FastMCP Server der alle Brain-Tools als MCP-Tools exponiert.
Wird von Claude Code als MCP-Server genutzt (stdio Transport).

DDD v3 Architektur:
- Alle Tools delegieren an Services via Composition Root (factory.py)
- Bounded Contexts: Identity, SemanticMemory, KnowledgeGraph, Conversation
- Application Service: Retrieval (Multi-Source Router)

Optimierungen:
- Pre-Warm: DB-Verbindungen + Embedding-Modell beim Start laden
- Error Handling: Strukturierte Fehler-Antworten statt raw Exceptions
- Caching: Core Memory mit 30s TTL
- Health-Check: Diagnose-Tool fuer alle DBs
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, List

from fastmcp import FastMCP

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
log = logging.getLogger("brain-tools")

# Brain-Modul-Pfad hinzufuegen
BRAIN_DIR = os.environ.get(
    "BRAIN_DIR",
    str(Path(__file__).parent.parent.parent / "brain")
)
PROJECT_DIR = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, PROJECT_DIR)

# Suppress noisy HuggingFace warnings
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

mcp = FastMCP("Brain-Tools")


# ============================================================
# Pre-Warm: Verbindungen + Modell beim Import vorbereiten
# ============================================================

def _prewarm():
    """Laedt DB-Verbindungen und Embedding-Modell im Hintergrund."""
    try:
        from brain.shared.config import load_config
        load_config()
        log.info("Config geladen (shared.config)")
    except Exception as e:
        log.warning(f"Config nicht geladen: {e}")

    try:
        from brain.shared.embeddings import _get_model
        _get_model()
        log.info("Embedding-Modell geladen (all-MiniLM-L6-v2)")
    except Exception as e:
        log.warning(f"Embedding-Modell nicht geladen: {e}")


# ============================================================
# Error Handling Wrapper
# ============================================================

def _safe_call(fn, **kwargs):
    """Wrapper der strukturierte Fehler zurueckgibt statt Exceptions."""
    try:
        return fn(**kwargs)
    except ConnectionError as e:
        return {"error": "connection_error", "message": str(e), "hint": "Ist Docker/DB gestartet?"}
    except ImportError as e:
        return {"error": "import_error", "message": str(e), "hint": "pip install -r requirements.txt"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


# ============================================================
# Caching: Core Memory (30s TTL)
# ============================================================

_core_memory_cache = {}
_core_memory_cache_time = 0
_CACHE_TTL = 30  # Sekunden


def _cached_core_memory_read(block=None):
    """Core Memory mit 30s Cache (haeufigster Read-Call)."""
    global _core_memory_cache, _core_memory_cache_time
    now = time.time()
    cache_key = block or "__all__"

    if now - _core_memory_cache_time < _CACHE_TTL and cache_key in _core_memory_cache:
        result = _core_memory_cache[cache_key]
        result["_cached"] = True
        return result

    from brain.shared.factory import get_identity_service
    result = get_identity_service().read(block)
    _core_memory_cache[cache_key] = result
    _core_memory_cache_time = now
    result["_cached"] = False
    return result


# ============================================================
# S1 — Core Memory (Identity Context)
# ============================================================

@mcp.tool()
def core_memory_read(block: Optional[str] = None) -> dict:
    """Liest Core Memory (S1). Immer zuerst aufrufen!

    Enthaelt 5 Bloecke: USER, PROJEKT, ENTSCHEIDUNGEN (Shared/Redis),
    FEHLER-LOG, AKTUELLE-ARBEIT (Lokal/Agent-Only).

    Args:
        block: Optional — Name des Blocks. Wenn leer: alle Blocks.
    """
    return _safe_call(_cached_core_memory_read, block=block)


@mcp.tool()
def core_memory_update(block: str, content: str) -> dict:
    """Updated einen Core Memory Block (S1).

    Shared-Blocks (USER, PROJEKT, ENTSCHEIDUNGEN) werden auch in Redis gespeichert.
    Max 4000 Zeichen pro Block.

    Args:
        block: Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
        content: Neuer Inhalt.
    """
    # Cache invalidieren bei Update
    global _core_memory_cache, _core_memory_cache_time
    _core_memory_cache = {}
    _core_memory_cache_time = 0

    from brain.shared.factory import get_identity_service
    return _safe_call(get_identity_service().update, block=block, content=content)


# ============================================================
# S2 — Auto-Recall / Capture (Semantic Memory Context)
# ============================================================

@mcp.tool()
def memory_search(
    query: str,
    scopes: Optional[List[str]] = None,
    top_k: int = 5,
    min_score: float = 0.5,
) -> list:
    """Semantische Suche in Erinnerungen (S2/Qdrant).

    Findet aehnliche Erinnerungen basierend auf Bedeutung, nicht nur Worten.
    Nutze dies fuer "Suche nach X" oder "Was wissen wir ueber Y?".

    Args:
        query: Suchtext (wird zu Vektor konvertiert).
        scopes: Optional — Filtern nach Bereichen (z.B. ["projekt", "user"]).
        top_k: Max Ergebnisse (default: 5).
        min_score: Min Aehnlichkeit 0.0-1.0 (default: 0.5).
    """
    from brain.shared.factory import get_semantic_memory_service
    return _safe_call(get_semantic_memory_service().search,
                      query=query, scopes=scopes, top_k=top_k, min_score=min_score)


@mcp.tool()
def memory_store(
    text: str,
    scope: str = "projekt",
    type: str = "fakt",
    priority: int = 5,
) -> dict:
    """Speichert eine neue Erinnerung (S2/Qdrant).

    Nutze dies fuer wichtige Fakten, Entscheidungen, Fehler.
    Automatische Deduplizierung (Score > 0.95 = Duplikat).

    Priority-Guide:
    - 9-10: Kritisch (Architektur-Entscheidungen, Security)
    - 7-8: Wichtig (Feature-Entscheidungen, Bugs)
    - 5-6: Normal (Implementierungs-Details)
    - 3-4: Niedrig (Temp-Notizen)
    - 1-2: Vergaenglich (Session-Beobachtungen)

    Args:
        text: Der zu speichernde Text.
        scope: Bereich (user, projekt, team, global).
        type: Art (entscheidung, fehler, fakt, praeferenz, todo, beobachtung).
        priority: Priority-Score 1-10.
    """
    from brain.shared.factory import get_semantic_memory_service
    return _safe_call(get_semantic_memory_service().store,
                      text=text, scope=scope, type=type, priority=priority)


# ============================================================
# S3 — HippoRAG (Knowledge Graph Context)
# ============================================================

@mcp.tool()
def hipporag_retrieve(query: str, top_k: int = 5) -> list:
    """Wissensgraph-Suche mit PPR (S3/Neo4j+Qdrant).

    Findet verknuepfte Konzepte, Personen, Projekte.
    Nutze dies fuer "Welche Projekte haengen mit X zusammen?" oder
    "Was wissen wir ueber die Beziehung zwischen A und B?".

    Args:
        query: Suchtext (Entitaeten werden automatisch extrahiert).
        top_k: Max Ergebnisse (default: 5).
    """
    from brain.shared.factory import get_knowledge_graph_service
    return _safe_call(get_knowledge_graph_service().retrieve, query=query, top_k=top_k)


@mcp.tool()
def hipporag_ingest(text: str) -> dict:
    """Pflegt neues Wissen in den Wissensgraph ein (S3/Neo4j+Qdrant).

    Extrahiert Entitaeten und Beziehungen, erstellt Graph-Knoten und Vektoren.
    Nutze dies nach wichtigen Erkenntnissen oder neuen Informationen.

    Args:
        text: Der zu indizierende Text.
    """
    from brain.shared.factory import get_knowledge_graph_service
    return _safe_call(get_knowledge_graph_service().ingest, text=text)


# ============================================================
# S4 — Agentic RAG (Retrieval Application Service)
# ============================================================

@mcp.tool()
def rag_route(query: str) -> dict:
    """Automatischer Multi-Source Router (S4).

    Entscheidet selbststaendig welche Datenbank(en) zu durchsuchen sind.
    Sucht in S2 (Qdrant), S3 (Neo4j), S6 (PostgreSQL).
    Nutze dies wenn unklar ist wo die Information liegt.

    Args:
        query: Suchtext.
    """
    from brain.shared.factory import get_retrieval_service
    return _safe_call(get_retrieval_service().route, query=query)


# ============================================================
# S5 — Learning Graphs (Knowledge Graph Context)
# ============================================================

@mcp.tool()
def learning_graph_update(session_data: dict) -> dict:
    """Aktualisiert Learning Graphs (S5/Neo4j).

    Erkennt Patterns in Session-Daten und staerkt Verbindungen im Wissensgraph.
    Wird normalerweise automatisch am Session-Ende aufgerufen.

    Args:
        session_data: Dict mit session_id, entities, tools_used.
    """
    from brain.shared.factory import get_knowledge_graph_service
    return _safe_call(get_knowledge_graph_service().update_patterns, session_data=session_data)


# ============================================================
# S6 — Recall Memory (Conversation Context)
# ============================================================

@mcp.tool()
def conversation_search(query: str, limit: int = 10) -> list:
    """Full-Text-Suche in Konversations-Historie (S6/PostgreSQL).

    Durchsucht alle gespeicherten Konversationen nach Stichworten.
    Nutze dies fuer "Was haben wir ueber X besprochen?".

    Args:
        query: Suchtext.
        limit: Max Ergebnisse (default: 10).
    """
    from brain.shared.factory import get_conversation_service
    return _safe_call(get_conversation_service().search, query=query, limit=limit)


@mcp.tool()
def conversation_search_date(
    start: str,
    end: str,
    agent: Optional[str] = None,
    limit: int = 20,
) -> list:
    """Datums-basierte Suche in Konversationen (S6/PostgreSQL).

    Findet Konversationen in einem Zeitraum.
    Nutze dies fuer "Was haben wir letzte Woche gemacht?".

    Args:
        start: Start-Datum (ISO format, z.B. "2026-02-01").
        end: End-Datum (ISO format, z.B. "2026-02-17").
        agent: Optional — Filtern nach Agent-Name.
        limit: Max Ergebnisse (default: 20).
    """
    from brain.shared.factory import get_conversation_service
    return _safe_call(get_conversation_service().search_date,
                      start=start, end=end, agent=agent, limit=limit)


# ============================================================
# Health-Check Tool
# ============================================================

@mcp.tool()
def brain_health() -> dict:
    """Prueft alle Brain-System Verbindungen (Diagnose-Tool).

    Testet: Qdrant, Neo4j, Redis, PostgreSQL, SQLite, Embeddings, Core Memory.
    Nutze dies bei Problemen oder zum System-Check.
    """
    status = {}

    # Qdrant
    try:
        from brain.shared.connections import get_qdrant
        client = get_qdrant()
        cols = client.get_collections()
        status["qdrant"] = {"ok": True, "collections": len(cols.collections)}
    except Exception as e:
        status["qdrant"] = {"ok": False, "error": str(e)}

    # Neo4j
    try:
        from brain.shared.connections import get_neo4j
        driver = get_neo4j()
        driver.verify_connectivity()
        status["neo4j"] = {"ok": True}
    except Exception as e:
        status["neo4j"] = {"ok": False, "error": str(e)}

    # Redis
    try:
        from brain.shared.connections import get_redis
        r = get_redis()
        r.ping()
        status["redis"] = {"ok": True}
    except Exception as e:
        status["redis"] = {"ok": False, "error": str(e)}

    # PostgreSQL
    try:
        from brain.shared.connections import get_postgres
        conn = get_postgres()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM conversations")
        count = cur.fetchone()[0]
        status["postgresql"] = {"ok": True, "conversations": count}
    except Exception as e:
        status["postgresql"] = {"ok": False, "error": str(e)}

    # SQLite
    try:
        from brain.shared.connections import get_sqlite
        conn = get_sqlite()
        cur = conn.execute("SELECT count(*) FROM conversations")
        count = cur.fetchone()[0]
        status["sqlite"] = {"ok": True, "conversations": count}
    except Exception as e:
        status["sqlite"] = {"ok": False, "error": str(e)}

    # Core Memory (via Identity Service)
    try:
        from brain.shared.factory import get_identity_service
        cm = get_identity_service().read()
        blocks = len(cm.get("blocks", {}))
        status["core_memory"] = {"ok": True, "blocks": blocks}
    except Exception as e:
        status["core_memory"] = {"ok": False, "error": str(e)}

    # DDD Architecture Status
    status["architecture"] = "DDD v3"
    status["bounded_contexts"] = ["Identity", "SemanticMemory", "KnowledgeGraph", "Conversation"]

    # Summary
    service_count = sum(1 for k, v in status.items() if isinstance(v, dict) and "ok" in v)
    ok_count = sum(1 for k, v in status.items() if isinstance(v, dict) and v.get("ok"))
    status["_summary"] = f"{ok_count}/{service_count} services healthy"

    return status


# ============================================================
# Server starten
# ============================================================

if __name__ == "__main__":
    _prewarm()
    mcp.run()
