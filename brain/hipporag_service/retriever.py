"""HippoRAG Retriever — S3 (COMPAT WRAPPER)

Delegiert an brain.knowledge_graph.service.KnowledgeGraphService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.hipporag_service.retriever import hipporag_retrieve
"""

from typing import List


def hipporag_retrieve(query: str, top_k: int = 5) -> List[dict]:
    """Wissensgraph-Suche mit PPR-Algorithmus.

    Args:
        query: Suchtext.
        top_k: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{entity, type, relations, score, context, source}]
    """
    from brain.shared.factory import get_knowledge_graph_service

    return get_knowledge_graph_service().retrieve(query=query, top_k=top_k)
