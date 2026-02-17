"""Recall Memory Search — S6 (COMPAT WRAPPER)

Delegiert an brain.conversation.service via Factory.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.recall_memory.search import conversation_search, conversation_search_date
"""

from typing import List, Optional


def conversation_search(query: str, limit: int = 10) -> List[dict]:
    """Full-Text-Suche in Konversationen.

    Args:
        query: Suchtext.
        limit: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{id, session_id, timestamp, role, content}]
    """
    from brain.shared.factory import get_conversation_service
    return get_conversation_service().search(query=query, limit=limit)


def conversation_search_date(
    start: str,
    end: str,
    agent: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """Datums-basierte Suche in Konversationen.

    Args:
        start: Start-Datum (ISO format, z.B. "2026-02-01").
        end: End-Datum (ISO format, z.B. "2026-02-17").
        agent: Optional — Filtern nach Agent-Name (in metadata).
        limit: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{id, session_id, timestamp, role, content}]
    """
    from brain.shared.factory import get_conversation_service
    return get_conversation_service().search_date(
        start=start, end=end, agent=agent, limit=limit,
    )
