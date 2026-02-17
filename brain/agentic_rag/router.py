"""Agentic RAG Router — S4 (Multi-Source)

Entscheidet automatisch welche Schicht(en) fuer eine Query genutzt werden.
Sucht parallel in S2 (Qdrant), S3 (Neo4j+Qdrant), S6 (PostgreSQL).
Merged und ranked die Ergebnisse.
"""

import re
from typing import List


# Query-Typ Heuristiken
_DATE_PATTERNS = [
    r'\b(gestern|heute|letzte woche|letzten monat|diesen monat)\b',
    r'\b\d{4}-\d{2}-\d{2}\b',
    r'\b(januar|februar|maerz|april|mai|juni|juli|august|september|oktober|november|dezember)\b',
]

_ENTITY_PATTERNS = [
    r'\b(wer|welche|zusammenhang|beziehung|verknuepf|verbind)\b',
]

_FACT_PATTERNS = [
    r'\b(wie heisst|was ist|name|version|stack|passwort)\b',
]


def _classify_query(query: str) -> str:
    """Klassifiziert die Query in einen Typ."""
    q_lower = query.lower()

    # Faktenfrage -> S1 (Core Memory)
    for pattern in _FACT_PATTERNS:
        if re.search(pattern, q_lower):
            return "fact"

    # Datums-basiert -> S6 (Recall Memory)
    for pattern in _DATE_PATTERNS:
        if re.search(pattern, q_lower):
            return "temporal"

    # Entity/Beziehungen -> S3 (HippoRAG)
    for pattern in _ENTITY_PATTERNS:
        if re.search(pattern, q_lower):
            return "entity"

    # Default -> Multi-Source
    return "multi"


def _search_s2(query: str, top_k: int) -> List[dict]:
    """S2: Semantische Suche in Qdrant."""
    try:
        from brain.auto_memory.recall import search_memories
        results = search_memories(query, top_k=top_k)
        return [{"source": "S2_qdrant", **r} for r in results]
    except Exception:
        return []


def _search_s3(query: str, top_k: int) -> List[dict]:
    """S3: Wissensgraph-Suche."""
    try:
        from brain.hipporag_service.retriever import hipporag_retrieve
        results = hipporag_retrieve(query, top_k=top_k)
        return [{"source": "S3_hipporag", **r} for r in results]
    except Exception:
        return []


def _search_s6(query: str, top_k: int) -> List[dict]:
    """S6: Konversations-Suche."""
    try:
        from brain.recall_memory.search import conversation_search
        results = conversation_search(query, limit=top_k)
        return [{"source": "S6_recall", "score": 0.7, **r} for r in results]
    except Exception:
        return []


def rag_route(query: str, top_k: int = 5) -> dict:
    """Multi-Source Router — entscheidet automatisch und sucht parallel.

    Args:
        query: Suchtext.
        top_k: Maximale Ergebnisse pro Quelle.

    Returns:
        Dict: {query_type, sources_searched, results, total_found}
    """
    query_type = _classify_query(query)
    all_results = []
    sources_searched = []

    if query_type == "fact":
        # Nur S1 (Core Memory) — wird direkt vom Agenten aufgerufen
        try:
            from brain.core_memory.reader import core_memory_read
            cm = core_memory_read()
            return {
                "query_type": "fact",
                "sources_searched": ["S1_core_memory"],
                "results": [{"source": "S1_core_memory", "content": cm, "score": 1.0}],
                "total_found": 1,
            }
        except Exception:
            pass

    elif query_type == "temporal":
        # Primaer S6, sekundaer S2
        sources_to_search = [
            ("S6", lambda: _search_s6(query, top_k)),
            ("S2", lambda: _search_s2(query, top_k)),
        ]
    elif query_type == "entity":
        # Primaer S3, sekundaer S2
        sources_to_search = [
            ("S3", lambda: _search_s3(query, top_k)),
            ("S2", lambda: _search_s2(query, top_k)),
        ]
    else:
        # Multi: Alle 3 parallel
        sources_to_search = [
            ("S2", lambda: _search_s2(query, top_k)),
            ("S3", lambda: _search_s3(query, top_k)),
            ("S6", lambda: _search_s6(query, top_k)),
        ]

    # Sequentiell ausfuehren (Thread-Safety mit Embedding-Modell)
    for source_name, fn in sources_to_search:
        try:
            results = fn()
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
        "results": all_results[:top_k * 2],  # Doppelt so viele wie top_k
        "total_found": len(all_results),
    }
