"""Auto-Recall — S2 (COMPAT WRAPPER)

Delegiert an brain.semantic_memory.service.SemanticMemoryService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.auto_memory.recall import search_memories
"""

from typing import List, Optional


def search_memories(
    query: str,
    scopes: Optional[List[str]] = None,
    top_k: int = 5,
    min_score: float = 0.5,
) -> List[dict]:
    """Semantische Suche in Qdrant ueber alle gespeicherten Erinnerungen.

    Args:
        query: Suchtext (wird zu Embedding konvertiert).
        scopes: Optional — Filtern nach Scopes (z.B. ["projekt", "user"]).
        top_k: Maximale Anzahl Ergebnisse.
        min_score: Minimaler Aehnlichkeits-Score (0.0-1.0).

    Returns:
        Liste von Dicts: [{text, scope, type, priority, score, timestamp}]
    """
    from brain.shared.factory import get_semantic_memory_service

    return get_semantic_memory_service().search(
        query=query, scopes=scopes, top_k=top_k, min_score=min_score,
    )
