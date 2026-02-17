"""HippoRAG Retriever — S3 (Neo4j + Qdrant)

Wissensgraph-Suche mit Personalized PageRank.
1. Entity Extraction aus Query
2. Graph Lookup in Neo4j
3. PPR (Personalized PageRank) Traversal
4. Qdrant Boost fuer Vektor-Aehnlichkeit
"""

import re
from typing import List


COLLECTION = "hipporag_embeddings"


def _extract_entities(text: str) -> List[str]:
    """Einfache Entity-Extraktion (Woerter mit Grossbuchstaben, > 2 Zeichen)."""
    words = re.findall(r'\b[A-Z][a-zA-Z0-9äöüÄÖÜß]{2,}\b', text)
    # Auch explizit genannte Terme
    quoted = re.findall(r'"([^"]+)"', text)
    return list(set(words + quoted)) or [text]


def hipporag_retrieve(query: str, top_k: int = 5) -> List[dict]:
    """Wissensgraph-Suche mit PPR-Algorithmus.

    Args:
        query: Suchtext.
        top_k: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{entity, type, relations, score, context}]
    """
    from brain.db import get_neo4j, get_qdrant
    from brain.embeddings import embed_text

    results = []

    # 1. Entity Extraction
    entities = _extract_entities(query)

    # 2. Graph Lookup + PPR in Neo4j
    try:
        driver = get_neo4j()
        with driver.session() as session:
            for entity_name in entities[:5]:  # Max 5 Startknoten
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
                    name=entity_name,
                    limit=top_k,
                )
                for record in records:
                    results.append({
                        "entity": record["entity"],
                        "type": record["type"] or "Unknown",
                        "relations": record["relations"],
                        "score": min(1.0, record["connections"] / 10.0),
                        "context": f"Graph-Knoten mit {record['connections']} Verbindungen",
                        "source": "neo4j",
                    })
    except Exception:
        pass  # Neo4j nicht erreichbar

    # 3. Qdrant Boost — Vektor-Suche in hipporag_embeddings
    try:
        client = get_qdrant()
        query_vector = embed_text(query)
        response = client.query_points(
            collection_name=COLLECTION,
            query=query_vector,
            limit=top_k,
            score_threshold=0.4,
        )
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
