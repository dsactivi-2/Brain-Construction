"""Retrieval Service — Application Service (S4)

Orchestriert Queries ueber mehrere Bounded Contexts hinweg.
Klassifiziert Query-Typ und delegiert an die richtigen Services.

Kein eigener Bounded Context — reiner Koordinierungs-Service.
"""


class RetrievalService:
    """Multi-Source Router mit injizierten Services."""

    def __init__(self, identity_service, semantic_service, knowledge_service,
                 conversation_service, classifier):
        self._identity = identity_service
        self._semantic = semantic_service
        self._knowledge = knowledge_service
        self._conversation = conversation_service
        self._classifier = classifier

    def route(self, query: str, top_k: int = 5) -> dict:
        """Klassifiziert Query und sucht in den richtigen Quellen.

        Args:
            query: Suchtext.
            top_k: Maximale Ergebnisse pro Quelle.

        Returns:
            Dict: {query_type, sources_searched, results, total_found}
        """
        query_type = self._classifier.classify(query)
        all_results = []
        sources_searched = []

        if query_type == "fact":
            try:
                cm = self._identity.read()
                return {
                    "query_type": "fact",
                    "sources_searched": ["S1_core_memory"],
                    "results": [{"source": "S1_core_memory", "content": cm, "score": 1.0}],
                    "total_found": 1,
                }
            except Exception:
                pass

        # Welche Quellen je nach Typ
        if query_type == "temporal":
            sources_to_search = [
                ("S6", self._search_s6),
                ("S2", self._search_s2),
            ]
        elif query_type == "entity":
            sources_to_search = [
                ("S3", self._search_s3),
                ("S2", self._search_s2),
            ]
        else:
            sources_to_search = [
                ("S2", self._search_s2),
                ("S3", self._search_s3),
                ("S6", self._search_s6),
            ]

        # Sequentiell ausfuehren (Thread-Safety mit Embedding-Modell)
        for source_name, fn in sources_to_search:
            try:
                results = fn(query, top_k)
                all_results.extend(results)
                if results:
                    sources_searched.append(source_name)
            except Exception:
                pass

        # Nach Score sortieren
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return {
            "query_type": query_type,
            "sources_searched": sources_searched,
            "results": all_results[:top_k * 2],
            "total_found": len(all_results),
        }

    def _search_s2(self, query: str, top_k: int) -> list:
        """S2: Semantische Suche via SemanticMemoryService."""
        try:
            results = self._semantic.search(query, top_k=top_k)
            return [{"source": "S2_qdrant", **r} for r in results]
        except Exception:
            return []

    def _search_s3(self, query: str, top_k: int) -> list:
        """S3: Wissensgraph-Suche via KnowledgeGraphService."""
        try:
            results = self._knowledge.retrieve(query, top_k=top_k)
            return [{"source": "S3_hipporag", **r} for r in results]
        except Exception:
            return []

    def _search_s6(self, query: str, top_k: int) -> list:
        """S6: Konversations-Suche via ConversationService."""
        try:
            results = self._conversation.search(query, limit=top_k)
            return [{"source": "S6_recall", "score": 0.7, **r} for r in results]
        except Exception:
            return []
