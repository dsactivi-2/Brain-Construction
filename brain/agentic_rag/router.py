"""Agentic RAG Router — S4 (COMPAT WRAPPER)

Delegiert an brain.retrieval.service.RetrievalService.
Alte Import-Pfade bleiben funktionsfaehig:
  from brain.agentic_rag.router import rag_route
"""


def rag_route(query: str, top_k: int = 5) -> dict:
    """Multi-Source Router — entscheidet automatisch und sucht parallel.

    Args:
        query: Suchtext.
        top_k: Maximale Ergebnisse pro Quelle.

    Returns:
        Dict: {query_type, sources_searched, results, total_found}
    """
    from brain.shared.factory import get_retrieval_service

    return get_retrieval_service().route(query=query, top_k=top_k)
