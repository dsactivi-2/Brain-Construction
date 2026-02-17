"""Composition Root — Shared Kernel

Verdrahtet alle Services mit ihren Dependencies.
Wird einmalig beim Start aufgerufen (MCP-Server Prewarm oder Hook-Init).

Jede Factory-Funktion gibt einen Singleton zurueck (@lru_cache).
"""

from functools import lru_cache


@lru_cache(maxsize=1)
def get_identity_service():
    """Erstellt CoreMemoryService mit Repository (Redis + JSON)."""
    from brain.shared.connections import get_redis
    from brain.shared.config import get_brain_dir
    from brain.identity.repository import CoreMemoryRepository
    from brain.identity.service import CoreMemoryService
    from pathlib import Path

    try:
        redis_client = get_redis()
    except Exception:
        redis_client = None

    # Core Memory JSON-Pfad
    json_path = Path(get_brain_dir()).parent / "config" / "core-memory.json"
    repo = CoreMemoryRepository(json_path=str(json_path), redis_client=redis_client)
    return CoreMemoryService(repo)


@lru_cache(maxsize=1)
def get_semantic_memory_service():
    """Erstellt SemanticMemoryService mit Qdrant Repository."""
    from brain.shared.connections import get_qdrant
    from brain.shared.embeddings import embed_text
    from brain.semantic_memory.repository import MemoryRepository
    from brain.semantic_memory.service import SemanticMemoryService

    repo = MemoryRepository(qdrant_client=get_qdrant())
    return SemanticMemoryService(repo, embed_fn=embed_text)


@lru_cache(maxsize=1)
def get_knowledge_graph_service():
    """Erstellt KnowledgeGraphService mit Neo4j + Qdrant Repositories."""
    from brain.shared.connections import get_neo4j, get_qdrant
    from brain.shared.embeddings import embed_text
    from brain.knowledge_graph.repository import GraphRepository, GraphEmbeddingRepository
    from brain.knowledge_graph.service import KnowledgeGraphService

    graph_repo = GraphRepository(neo4j_driver=get_neo4j())
    emb_repo = GraphEmbeddingRepository(qdrant_client=get_qdrant())
    return KnowledgeGraphService(graph_repo, emb_repo, embed_fn=embed_text)


@lru_cache(maxsize=1)
def get_conversation_service():
    """Erstellt ConversationService mit PostgreSQL + SQLite Fallback."""
    from brain.shared.connections import get_postgres, get_sqlite
    from brain.conversation.repository import ConversationRepository
    from brain.conversation.service import ConversationService

    try:
        pg = get_postgres()
    except Exception:
        pg = None
    try:
        sqlite = get_sqlite()
    except Exception:
        sqlite = None

    repo = ConversationRepository(postgres_conn=pg, sqlite_conn=sqlite)
    return ConversationService(repo)


@lru_cache(maxsize=1)
def get_retrieval_service():
    """Erstellt RetrievalService mit allen injizierten Services."""
    from brain.retrieval.classifier import QueryClassifier
    from brain.retrieval.service import RetrievalService

    return RetrievalService(
        identity_service=get_identity_service(),
        semantic_service=get_semantic_memory_service(),
        knowledge_service=get_knowledge_graph_service(),
        conversation_service=get_conversation_service(),
        classifier=QueryClassifier(),
    )
