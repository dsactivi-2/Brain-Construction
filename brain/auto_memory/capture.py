"""Auto-Capture — S2 (COMPAT WRAPPER)

Delegiert an brain.semantic_memory.service.SemanticMemoryService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.auto_memory.capture import extract_and_store
"""

from typing import Optional


# Re-export fuer Rueckwaertskompatibilitaet
PRIORITY_DEFAULTS = {
    "entscheidung": 9,
    "fehler": 8,
    "fakt": 7,
    "praeferenz": 6,
    "todo": 5,
    "beobachtung": 3,
}


def extract_and_store(
    text: str,
    scope: str = "projekt",
    type: str = "fakt",
    priority: Optional[int] = None,
) -> dict:
    """Speichert eine neue Erinnerung in Qdrant (mit Deduplizierung).

    Args:
        text: Der zu speichernde Text.
        scope: Bereich (user, projekt, team, global).
        type: Art (entscheidung, fehler, fakt, praeferenz, todo, beobachtung).
        priority: Priority-Score 1-10. Wenn None: Auto nach Type.

    Returns:
        Dict: {id, text, scope, type, priority, stored: True/False, reason}
    """
    from brain.shared.factory import get_semantic_memory_service

    return get_semantic_memory_service().store(
        text=text, scope=scope, type=type, priority=priority,
    )
