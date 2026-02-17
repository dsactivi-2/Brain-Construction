"""Brain-Tools MCP Server — Cloud Code Team 02.26

FastMCP Server der alle Brain-Tools als MCP-Tools exponiert.
Wird von Claude Code als MCP-Server genutzt (stdio Transport).

Starten: python server.py
Oder via Claude Code settings.json: mcpServers.brain-tools
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

from fastmcp import FastMCP

# Brain-Modul-Pfad hinzufuegen
BRAIN_DIR = os.environ.get(
    "BRAIN_DIR",
    str(Path(__file__).parent.parent.parent / "brain")
)
PROJECT_DIR = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, PROJECT_DIR)

mcp = FastMCP("Brain-Tools")


# ============================================================
# S1 — Core Memory
# ============================================================

@mcp.tool()
def core_memory_read(block: Optional[str] = None) -> dict:
    """Liest Core Memory (S1). Immer zuerst aufrufen!

    Enthaelt 5 Bloecke: USER, PROJEKT, ENTSCHEIDUNGEN (Shared/Redis),
    FEHLER-LOG, AKTUELLE-ARBEIT (Lokal/Agent-Only).

    Args:
        block: Optional — Name des Blocks. Wenn leer: alle Blocks.
    """
    from brain.core_memory.reader import core_memory_read as _read
    return _read(block)


@mcp.tool()
def core_memory_update(block: str, content: str) -> dict:
    """Updated einen Core Memory Block (S1).

    Shared-Blocks (USER, PROJEKT, ENTSCHEIDUNGEN) werden auch in Redis gespeichert.
    Max 4000 Zeichen pro Block.

    Args:
        block: Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
        content: Neuer Inhalt.
    """
    from brain.core_memory.writer import core_memory_update as _update
    return _update(block, content)


# ============================================================
# S2 — Auto-Recall / Capture
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
    from brain.auto_memory.recall import search_memories
    return search_memories(query, scopes=scopes, top_k=top_k, min_score=min_score)


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
    from brain.auto_memory.capture import extract_and_store
    return extract_and_store(text, scope=scope, type=type, priority=priority)


# ============================================================
# S3 — HippoRAG
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
    from brain.hipporag_service.retriever import hipporag_retrieve as _retrieve
    return _retrieve(query, top_k=top_k)


@mcp.tool()
def hipporag_ingest(text: str) -> dict:
    """Pflegt neues Wissen in den Wissensgraph ein (S3/Neo4j+Qdrant).

    Extrahiert Entitaeten und Beziehungen, erstellt Graph-Knoten und Vektoren.
    Nutze dies nach wichtigen Erkenntnissen oder neuen Informationen.

    Args:
        text: Der zu indizierende Text.
    """
    from brain.hipporag_service.indexer import hipporag_ingest as _ingest
    return _ingest(text)


# ============================================================
# S4 — Agentic RAG (Multi-Source Router)
# ============================================================

@mcp.tool()
def rag_route(query: str) -> dict:
    """Automatischer Multi-Source Router (S4).

    Entscheidet selbststaendig welche Datenbank(en) zu durchsuchen sind.
    Sucht parallel in S2 (Qdrant), S3 (Neo4j), S6 (PostgreSQL).
    Nutze dies wenn unklar ist wo die Information liegt.

    Args:
        query: Suchtext.
    """
    from brain.agentic_rag.router import rag_route as _route
    return _route(query)


# ============================================================
# S5 — Learning Graphs
# ============================================================

@mcp.tool()
def learning_graph_update(session_data: dict) -> dict:
    """Aktualisiert Learning Graphs (S5/Neo4j).

    Erkennt Patterns in Session-Daten und staerkt Verbindungen im Wissensgraph.
    Wird normalerweise automatisch am Session-Ende aufgerufen.

    Args:
        session_data: Dict mit session_id, entities, tools_used.
    """
    from brain.learning_graphs.patterns import learning_graph_update as _update
    return _update(session_data)


# ============================================================
# S6 — Recall Memory
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
    from brain.recall_memory.search import conversation_search as _search
    return _search(query, limit=limit)


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
    from brain.recall_memory.search import conversation_search_date as _search_date
    return _search_date(start, end, agent=agent, limit=limit)


# ============================================================
# Server starten
# ============================================================

if __name__ == "__main__":
    mcp.run()
