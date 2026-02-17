"""Auto-Recall — S2 (Qdrant Semantische Suche)

Sucht in der mem0_memories Collection nach aehnlichen Erinnerungen.
Wird von hooks/auto-recall.sh aufgerufen.
"""

from typing import List, Optional
from datetime import datetime


COLLECTION = "mem0_memories"


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
    from brain.embeddings import embed_text
    from brain.db import get_qdrant
    from qdrant_client.models import Filter, FieldCondition, MatchAny

    client = get_qdrant()
    query_vector = embed_text(query)

    # Filter bauen
    search_filter = None
    if scopes:
        search_filter = Filter(
            must=[FieldCondition(key="scope", match=MatchAny(any=scopes))]
        )

    response = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        query_filter=search_filter,
        limit=top_k,
        score_threshold=min_score,
    )

    memories = []
    for hit in response.points:
        payload = hit.payload or {}
        memories.append({
            "text": payload.get("text", ""),
            "scope": payload.get("scope", ""),
            "type": payload.get("type", ""),
            "priority": payload.get("priority", 5),
            "score": round(hit.score, 4),
            "timestamp": payload.get("timestamp", ""),
        })

    return memories
