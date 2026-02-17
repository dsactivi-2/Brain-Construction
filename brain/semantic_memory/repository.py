"""Semantic Memory Repository — S2

Datenzugriff auf die mem0_memories Qdrant Collection.
Kapselt alle Qdrant-Operationen fuer semantische Erinnerungen.
"""

from typing import List, Optional

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchAny,
    SearchParams,
    PointStruct,
)


COLLECTION = "mem0_memories"


class MemoryRepository:
    """Repository fuer semantische Erinnerungen in Qdrant."""

    def __init__(self, qdrant_client):
        """Initialisiert mit Qdrant-Client.

        Args:
            qdrant_client: Verbundener QdrantClient.
        """
        self._client = qdrant_client

    def search(
        self,
        query_vector: List[float],
        scopes: Optional[List[str]] = None,
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[dict]:
        """Semantische Suche in der mem0_memories Collection.

        Args:
            query_vector: Embedding-Vektor der Suchanfrage.
            scopes: Optional — Filtern nach Scopes (z.B. ["projekt", "user"]).
            top_k: Maximale Anzahl Ergebnisse.
            min_score: Minimaler Aehnlichkeits-Score (0.0-1.0).

        Returns:
            Liste von Dicts: [{text, scope, type, priority, score, timestamp}]
        """
        # Filter bauen
        search_filter = None
        if scopes:
            search_filter = Filter(
                must=[FieldCondition(key="scope", match=MatchAny(any=scopes))]
            )

        response = self._client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            query_filter=search_filter,
            limit=top_k,
            score_threshold=min_score,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False,
            ),
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

    def find_duplicate(
        self,
        query_vector: List[float],
        threshold: float = 0.95,
    ) -> Optional[str]:
        """Prueft ob ein sehr aehnlicher Eintrag existiert (Deduplizierung).

        Args:
            query_vector: Embedding-Vektor des neuen Textes.
            threshold: Minimaler Score fuer Duplikat-Erkennung.

        Returns:
            Point-ID des Duplikats oder None.
        """
        response = self._client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            limit=1,
            score_threshold=threshold,
        )

        if response.points:
            return str(response.points[0].id), response.points[0].score
        return None

    def save(
        self,
        point_id: str,
        vector: List[float],
        payload: dict,
    ) -> None:
        """Speichert einen neuen Eintrag in Qdrant (Upsert).

        Args:
            point_id: UUID des neuen Eintrags.
            vector: Embedding-Vektor.
            payload: Metadaten (text, scope, type, priority, timestamp).
        """
        self._client.upsert(
            collection_name=COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
