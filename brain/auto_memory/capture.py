"""Auto-Capture — S2 (Qdrant Speicherung)

Speichert neue Erinnerungen in der mem0_memories Collection.
Wird von hooks/auto-capture.sh aufgerufen.
Deduplizierung: Pruebt ob aehnlicher Eintrag existiert (Score > 0.95).
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


COLLECTION = "mem0_memories"

# Priority-Defaults nach Type
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
    from brain.embeddings import embed_text
    from brain.db import get_qdrant
    from qdrant_client.models import PointStruct

    if priority is None:
        priority = PRIORITY_DEFAULTS.get(type, 5)

    client = get_qdrant()
    vector = embed_text(text)

    # Deduplizierung: Pruefen ob sehr aehnlicher Eintrag existiert
    response = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=1,
        score_threshold=0.95,
    )

    if response.points:
        return {
            "id": str(response.points[0].id),
            "text": text,
            "scope": scope,
            "type": type,
            "priority": priority,
            "stored": False,
            "reason": f"Duplikat gefunden (Score: {response.points[0].score:.4f})",
        }

    # Neuen Eintrag speichern
    point_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": text,
                    "scope": scope,
                    "type": type,
                    "priority": priority,
                    "timestamp": timestamp,
                },
            )
        ],
    )

    return {
        "id": point_id,
        "text": text,
        "scope": scope,
        "type": type,
        "priority": priority,
        "stored": True,
        "timestamp": timestamp,
    }
