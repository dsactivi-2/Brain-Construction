"""Knowledge Graph Service — S3 + S5

Anwendungslogik fuer den Wissensgraph (HippoRAG Retrieve/Ingest + Learning Graphs).
Orchestriert GraphRepository, GraphEmbeddingRepository und Embedding-Generierung.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Callable, List, Optional

from brain.knowledge_graph.extraction import (
    extract_entities,
    extract_entity_names,
    extract_relations,
)

_logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service fuer S3 HippoRAG + S5 Learning Graphs."""

    def __init__(self, graph_repo, embedding_repo, embed_fn: Callable):
        """Initialisiert mit Repositories und Embedding-Funktion.

        Args:
            graph_repo: GraphRepository-Instanz (Neo4j).
            embedding_repo: GraphEmbeddingRepository-Instanz (Qdrant).
            embed_fn: Funktion text -> vector (brain.shared.embeddings.embed_text).
        """
        self._graph_repo = graph_repo
        self._embedding_repo = embedding_repo
        self._embed_fn = embed_fn

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        """Wissensgraph-Suche mit Personalized PageRank.

        Versucht GDS PPR, faellt auf Connection-Count zurueck wenn GDS nicht verfuegbar.
        Rueckgabe-Format identisch mit hipporag_service/retriever.py::hipporag_retrieve().

        Args:
            query: Suchtext.
            top_k: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts: [{entity, type, relations, score, context, source}]
        """
        results = []

        # 1. Entity Extraction
        entities = extract_entity_names(query)

        # 2. Graph Lookup — PPR zuerst, Fallback auf Connection-Count
        try:
            results.extend(self._retrieve_ppr(entities, top_k))
        except Exception as e:
            _logger.debug("PPR nicht verfuegbar, Fallback auf Connection-Count: %s", e)
            try:
                results.extend(self._retrieve_connection_count(entities, top_k))
            except Exception:
                pass  # Neo4j nicht erreichbar

        # 3. Qdrant Boost — Vektor-Suche in hipporag_embeddings
        try:
            query_vector = self._embed_fn(query)
            qdrant_results = self._embedding_repo.search(
                query_vector=query_vector,
                top_k=top_k,
                min_score=0.4,
            )
            results.extend(qdrant_results)
        except Exception:
            pass  # Qdrant nicht erreichbar

        # 4. Ergebnisse mergen und nach Score sortieren
        # Deduplizierung nach Entity-Name
        seen = set()
        unique_results = []
        for r in sorted(results, key=lambda x: x["score"], reverse=True):
            key = r["entity"].lower() if r["entity"] else str(len(seen))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results[:top_k]

    def _retrieve_ppr(self, entities: list, top_k: int) -> list:
        """PPR-basiertes Retrieval. Wirft Exception bei Fehler (Caller faellt zurueck).

        Args:
            entities: Extrahierte Entity-Namen.
            top_k: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts im Standard-Format.

        Raises:
            RuntimeError: Wenn Projection oder Seed-Nodes nicht verfuegbar.
        """
        if not self._graph_repo.ensure_graph_projection():
            raise RuntimeError("Graph-Projection leer oder nicht verfuegbar")

        seed_ids = self._graph_repo.resolve_entity_nodes(entities[:5])
        if not seed_ids:
            raise RuntimeError("Keine Seed-Nodes gefunden")

        ppr_results = self._graph_repo.personalized_pagerank(
            seed_node_ids=seed_ids, top_k=top_k,
        )

        if not ppr_results:
            return []

        # PPR-Scores auf 0.0-1.0 normalisieren
        max_score = max(r["ppr_score"] for r in ppr_results)
        results = []
        for r in ppr_results:
            score = round(r["ppr_score"] / max_score, 4) if max_score > 0 else 0.0
            results.append({
                "entity": r["entity"],
                "type": r["type"],
                "relations": r["relations"],
                "score": score,
                "context": f"PPR-Score: {r['ppr_score']:.6f} (normalisiert: {score})",
                "source": "neo4j",
            })

        return results

    def _retrieve_connection_count(self, entities: list, top_k: int) -> list:
        """Connection-Count Fallback (Original-Verhalten).

        Args:
            entities: Extrahierte Entity-Namen.
            top_k: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts im Standard-Format.
        """
        results = []
        for entity_name in entities[:5]:
            records = self._graph_repo.find_entities(
                name=entity_name, limit=top_k,
            )
            for record in records:
                results.append({
                    "entity": record["entity"],
                    "type": record["type"],
                    "relations": record["relations"],
                    "score": min(1.0, record["connections"] / 10.0),
                    "context": f"Graph-Knoten mit {record['connections']} Verbindungen",
                    "source": "neo4j",
                })
        return results

    def ingest(self, text: str) -> dict:
        """Pflegt neues Wissen in Neo4j + Qdrant ein.

        Rueckgabe-Format identisch mit hipporag_service/indexer.py::hipporag_ingest().

        Args:
            text: Der zu indizierende Text.

        Returns:
            Dict: {entities_created, relations_created, embedding_stored, entities}
        """
        entities = extract_entities(text)
        relations = extract_relations(text, entities)
        entities_created = 0
        relations_created = 0
        embedding_stored = False

        # 1. Neo4j: Entitaeten + Beziehungen erstellen
        try:
            for entity in entities:
                self._graph_repo.merge_entity(
                    name=entity.name, entity_type=entity.type,
                )
                entities_created += 1

            for rel in relations:
                self._graph_repo.merge_relation(
                    source=rel.source,
                    target=rel.target,
                    rel_type=rel.type,
                    context=rel.context,
                )
                relations_created += 1
        except Exception:
            pass  # Neo4j nicht erreichbar

        # 2. Qdrant: Embedding speichern
        try:
            vector = self._embed_fn(text)
            timestamp = datetime.now(timezone.utc).isoformat()

            self._embedding_repo.store(
                point_id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": text[:1000],
                    "entity": ", ".join(e.name for e in entities[:5]),
                    "type": "document",
                    "context": text[:500],
                    "timestamp": timestamp,
                },
            )
            embedding_stored = True
        except Exception:
            pass  # Qdrant nicht erreichbar

        return {
            "entities_created": entities_created,
            "relations_created": relations_created,
            "embedding_stored": embedding_stored,
            "entities": [e.name for e in entities],
        }

    def update_patterns(self, session_data: dict) -> dict:
        """Aktualisiert Learning Graphs basierend auf Session-Daten.

        Rueckgabe-Format identisch mit learning_graphs/patterns.py::learning_graph_update().

        Args:
            session_data: Dict mit session_id, entities, tools_used, etc.

        Returns:
            Dict: {patterns_found, patterns_updated, session_id}
        """
        patterns_found = 0
        patterns_updated = 0

        try:
            entities = session_data.get("entities", [])

            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    result = self._graph_repo.upsert_pattern(
                        entity_a=entities[i],
                        entity_b=entities[j],
                    )
                    if result.get("is_new"):
                        patterns_found += 1
                    else:
                        patterns_updated += 1
        except Exception:
            pass

        return {
            "patterns_found": patterns_found,
            "patterns_updated": patterns_updated,
            "session_id": session_data.get("session_id", ""),
        }

    def consolidate(self) -> dict:
        """Konsolidiert schwache Pattern-Knoten.

        Rueckgabe-Format identisch mit learning_graphs/patterns.py::consolidate().

        Returns:
            Dict: {merged, deleted}
        """
        merged = 0
        deleted = 0

        try:
            # Schwache Patterns loeschen (Score < 0.1)
            deleted = self._graph_repo.delete_weak_patterns(min_score=0.1)

            # Mittlere Patterns: Score halbieren wenn alt (> 90 Tage)
            merged = self._graph_repo.decay_old_patterns(
                days_threshold=90, factor=0.5,
            )
        except Exception:
            pass

        return {"merged": merged, "deleted": deleted}

    def decay_prune(self) -> dict:
        """Taelicher Score-Decay + Archivierung alter Eintraege.

        Rueckgabe-Format identisch mit learning_graphs/patterns.py::decay_prune().

        - Patterns > 90 Tage ohne Abruf: Score -10%
        - Patterns > 180 Tage: Archivieren/Loeschen

        Returns:
            Dict: {decayed, archived}
        """
        decayed = 0
        archived = 0

        try:
            # 90-Tage Decay (Score * 0.9)
            decayed = self._graph_repo.decay_old_patterns(
                days_threshold=90, factor=0.9,
            )

            # 180-Tage Archiv (loeschen)
            archived = self._graph_repo.delete_archived_patterns(
                days_threshold=180,
            )
        except Exception:
            pass

        return {"decayed": decayed, "archived": archived}
