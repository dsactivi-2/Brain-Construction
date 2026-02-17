"""Knowledge Graph Repositories — S3 + S5

Datenzugriff auf Neo4j (Graph) und Qdrant (Embeddings).
Zwei Repository-Klassen: GraphRepository und GraphEmbeddingRepository.
"""

from typing import List, Optional, Dict
from datetime import datetime, timezone, timedelta

from qdrant_client.models import PointStruct


EMBEDDING_COLLECTION = "hipporag_embeddings"


class GraphRepository:
    """Repository fuer den Wissensgraph in Neo4j."""

    def __init__(self, neo4j_driver):
        """Initialisiert mit Neo4j Driver.

        Args:
            neo4j_driver: Verbundener Neo4j Driver.
        """
        self._driver = neo4j_driver

    def find_entities(self, name: str, limit: int = 5) -> List[dict]:
        """Sucht Entitaeten im Graph (Case-insensitive CONTAINS).

        Identisch mit retriever.py Graph Lookup Cypher.

        Args:
            name: Suchbegriff (Teilstring-Match).
            limit: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts: [{entity, type, relations, connections}]
        """
        with self._driver.session() as session:
            records = session.run(
                """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($name)
                OPTIONAL MATCH (e)-[r]-(related:Entity)
                RETURN e.name AS entity, e.type AS type,
                       collect(DISTINCT {
                           name: related.name,
                           type: related.type,
                           relation: type(r)
                       })[..10] AS relations,
                       size((e)--()) AS connections
                ORDER BY connections DESC
                LIMIT $limit
                """,
                name=name,
                limit=limit,
            )
            results = []
            for record in records:
                results.append({
                    "entity": record["entity"],
                    "type": record["type"] or "Unknown",
                    "relations": record["relations"],
                    "connections": record["connections"],
                })
            return results

    def merge_entity(self, name: str, entity_type: str = "Entity") -> None:
        """Erstellt oder aktualisiert eine Entitaet (MERGE).

        Args:
            name: Name der Entitaet.
            entity_type: Typ der Entitaet (default: "Entity").
        """
        with self._driver.session() as session:
            session.run(
                "MERGE (e:Entity {name: $name}) SET e.type = $type, e.updated = datetime()",
                name=name,
                type=entity_type,
            )

    def merge_relation(
        self,
        source: str,
        target: str,
        rel_type: str = "RELATED_TO",
        context: str = "",
    ) -> None:
        """Erstellt oder aktualisiert eine Beziehung (MERGE).

        Args:
            source: Name der Quell-Entitaet.
            target: Name der Ziel-Entitaet.
            rel_type: Beziehungstyp (default: "RELATED_TO").
            context: Kontext-Text der Beziehung.
        """
        with self._driver.session() as session:
            session.run(
                """
                MATCH (a:Entity {name: $source})
                MATCH (b:Entity {name: $target})
                MERGE (a)-[r:RELATED_TO]->(b)
                SET r.context = $context, r.updated = datetime()
                """,
                source=source,
                target=target,
                context=context,
            )

    def upsert_pattern(self, entity_a: str, entity_b: str) -> dict:
        """Erstellt oder staerkt ein Pattern (Co-Occurrence).

        Identisch mit patterns.py MERGE-Logik.

        Args:
            entity_a: Erste Entitaet.
            entity_b: Zweite Entitaet.

        Returns:
            Dict: {count, is_new}
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        pattern_id = f"{min(entity_a, entity_b)}_{max(entity_a, entity_b)}"

        with self._driver.session() as session:
            result = session.run(
                """
                MERGE (p:Pattern {
                    id: $pattern_id
                })
                ON CREATE SET
                    p.entity_a = $entity_a,
                    p.entity_b = $entity_b,
                    p.count = 1,
                    p.first_seen = $timestamp,
                    p.last_seen = $timestamp,
                    p.score = 1.0
                ON MATCH SET
                    p.count = p.count + 1,
                    p.last_seen = $timestamp,
                    p.score = p.score + 0.1
                RETURN p.count AS count
                """,
                pattern_id=pattern_id,
                entity_a=entity_a,
                entity_b=entity_b,
                timestamp=timestamp,
            )
            record = result.single()
            if record:
                return {"count": record["count"], "is_new": record["count"] == 1}
            return {"count": 0, "is_new": False}

    def delete_weak_patterns(self, min_score: float = 0.1) -> int:
        """Loescht Patterns mit Score unter dem Schwellwert.

        Args:
            min_score: Minimaler Score (Patterns darunter werden geloescht).

        Returns:
            Anzahl geloeschter Patterns.
        """
        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.score < $min_score
                DELETE p
                RETURN count(p) AS deleted
                """,
                min_score=min_score,
            )
            record = result.single()
            return record["deleted"] if record else 0

    def decay_old_patterns(self, days_threshold: int = 90, factor: float = 0.5) -> int:
        """Reduziert Scores von alten Patterns.

        Args:
            days_threshold: Tage seit letztem Zugriff.
            factor: Multiplikator fuer den Score (z.B. 0.5 = halbieren).

        Returns:
            Anzahl betroffener Patterns.
        """
        threshold = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).isoformat()

        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.last_seen < $threshold AND p.score > 0.1
                SET p.score = p.score * $factor
                RETURN count(p) AS decayed
                """,
                threshold=threshold,
                factor=factor,
            )
            record = result.single()
            return record["decayed"] if record else 0

    def delete_archived_patterns(self, days_threshold: int = 180) -> int:
        """Loescht archivierte Patterns (sehr alt).

        Args:
            days_threshold: Tage seit letztem Zugriff fuer Archiv-Loeschung.

        Returns:
            Anzahl geloeschter Patterns.
        """
        threshold = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).isoformat()

        with self._driver.session() as session:
            result = session.run(
                """
                MATCH (p:Pattern)
                WHERE p.last_seen < $threshold
                DELETE p
                RETURN count(p) AS archived
                """,
                threshold=threshold,
            )
            record = result.single()
            return record["archived"] if record else 0


class GraphEmbeddingRepository:
    """Repository fuer Graph-Embeddings in Qdrant."""

    def __init__(self, qdrant_client):
        """Initialisiert mit Qdrant-Client.

        Args:
            qdrant_client: Verbundener QdrantClient.
        """
        self._client = qdrant_client

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        min_score: float = 0.4,
    ) -> List[dict]:
        """Vektor-Suche in der hipporag_embeddings Collection.

        Verwendet client.query_points() (qdrant-client 1.16.2).

        Args:
            query_vector: Embedding-Vektor der Suchanfrage.
            top_k: Maximale Anzahl Ergebnisse.
            min_score: Minimaler Aehnlichkeits-Score.

        Returns:
            Liste von Dicts: [{entity, type, relations, score, context, source}]
        """
        response = self._client.query_points(
            collection_name=EMBEDDING_COLLECTION,
            query=query_vector,
            limit=top_k,
            score_threshold=min_score,
        )

        results = []
        for hit in response.points:
            payload = hit.payload or {}
            results.append({
                "entity": payload.get("entity", payload.get("text", "")),
                "type": payload.get("type", "embedding"),
                "relations": [],
                "score": round(hit.score, 4),
                "context": payload.get("context", ""),
                "source": "qdrant",
            })

        return results

    def store(
        self,
        point_id: str,
        vector: List[float],
        payload: dict,
    ) -> None:
        """Speichert ein Embedding in Qdrant (Upsert).

        Args:
            point_id: UUID des Eintrags.
            vector: Embedding-Vektor.
            payload: Metadaten (text, entity, type, context, timestamp).
        """
        self._client.upsert(
            collection_name=EMBEDDING_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
