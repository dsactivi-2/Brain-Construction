"""HippoRAG Indexer — S3 (Neo4j + Qdrant)

Pflegt Wissen in den Wissensgraph ein.
Extrahiert Entitaeten + Beziehungen und erstellt Graph-Knoten + Vektoren.
"""

import re
import uuid
from datetime import datetime, timezone
from typing import List, Tuple


COLLECTION = "hipporag_embeddings"


def _extract_entities_and_relations(text: str) -> Tuple[List[dict], List[dict]]:
    """Einfache NER + Relation Extraction.

    Returns:
        (entities, relations) — Listen von Dicts.
    """
    # Einfache Heuristik: Gross geschriebene Woerter = Entitaeten
    entity_names = list(set(re.findall(r'\b[A-Z][a-zA-Z0-9äöüÄÖÜß]{2,}\b', text)))

    entities = [{"name": name, "type": "Entity"} for name in entity_names]

    # Einfache Relation-Erkennung: Entitaeten die im selben Satz vorkommen
    relations = []
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        found = [e for e in entity_names if e in sentence]
        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                relations.append({
                    "source": found[i],
                    "target": found[j],
                    "type": "RELATED_TO",
                    "context": sentence.strip()[:200],
                })

    return entities, relations


def hipporag_ingest(text: str) -> dict:
    """Pflegt neues Wissen in Neo4j + Qdrant ein.

    Args:
        text: Der zu indizierende Text.

    Returns:
        Dict: {entities_created, relations_created, embedding_stored}
    """
    from brain.db import get_neo4j, get_qdrant
    from brain.embeddings import embed_text
    from qdrant_client.models import PointStruct

    entities, relations = _extract_entities_and_relations(text)
    entities_created = 0
    relations_created = 0
    embedding_stored = False

    # 1. Neo4j: Entitaeten + Beziehungen erstellen
    try:
        driver = get_neo4j()
        with driver.session() as session:
            for entity in entities:
                session.run(
                    "MERGE (e:Entity {name: $name}) SET e.type = $type, e.updated = datetime()",
                    name=entity["name"],
                    type=entity["type"],
                )
                entities_created += 1

            for rel in relations:
                session.run(
                    """
                    MATCH (a:Entity {name: $source})
                    MATCH (b:Entity {name: $target})
                    MERGE (a)-[r:RELATED_TO]->(b)
                    SET r.context = $context, r.updated = datetime()
                    """,
                    source=rel["source"],
                    target=rel["target"],
                    context=rel["context"],
                )
                relations_created += 1
    except Exception:
        pass  # Neo4j nicht erreichbar

    # 2. Qdrant: Embedding speichern
    try:
        client = get_qdrant()
        vector = embed_text(text)
        timestamp = datetime.now(timezone.utc).isoformat()

        client.upsert(
            collection_name=COLLECTION,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": text[:1000],
                        "entity": ", ".join(e["name"] for e in entities[:5]),
                        "type": "document",
                        "context": text[:500],
                        "timestamp": timestamp,
                    },
                )
            ],
        )
        embedding_stored = True
    except Exception:
        pass

    return {
        "entities_created": entities_created,
        "relations_created": relations_created,
        "embedding_stored": embedding_stored,
        "entities": [e["name"] for e in entities],
    }
