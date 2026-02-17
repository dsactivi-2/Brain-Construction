"""HippoRAG Indexer — S3 (COMPAT WRAPPER)

Delegiert an brain.knowledge_graph.service.KnowledgeGraphService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.hipporag_service.indexer import hipporag_ingest
"""


def hipporag_ingest(text: str) -> dict:
    """Pflegt neues Wissen in Neo4j + Qdrant ein.

    Args:
        text: Der zu indizierende Text.

    Returns:
        Dict: {entities_created, relations_created, embedding_stored, entities}
    """
    from brain.shared.factory import get_knowledge_graph_service

    return get_knowledge_graph_service().ingest(text=text)
