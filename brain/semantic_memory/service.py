"""Semantic Memory Service — S2

Anwendungslogik fuer semantische Erinnerungen (Suche + Speicherung).
Orchestriert Repository und Embedding-Generierung.
"""

from typing import Callable, List, Optional

from brain.semantic_memory.model import PRIORITY_DEFAULTS, MemoryType, Memory, MemoryScope


# String-basierte Priority-Defaults (Compat mit capture.py)
_PRIORITY_DEFAULTS_STR = {t.value: p for t, p in PRIORITY_DEFAULTS.items()}


class SemanticMemoryService:
    """Service fuer S2 Auto-Recall/Capture."""

    def __init__(self, repository, embed_fn: Callable):
        """Initialisiert mit Repository und Embedding-Funktion.

        Args:
            repository: MemoryRepository-Instanz.
            embed_fn: Funktion text -> vector (brain.shared.embeddings.embed_text).
        """
        self._repo = repository
        self._embed_fn = embed_fn

    def search(
        self,
        query: str,
        scopes: Optional[List[str]] = None,
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[dict]:
        """Semantische Suche ueber alle gespeicherten Erinnerungen.

        Rueckgabe-Format identisch mit auto_memory/recall.py::search_memories().

        Args:
            query: Suchtext (wird zu Embedding konvertiert).
            scopes: Optional — Filtern nach Scopes (z.B. ["projekt", "user"]).
            top_k: Maximale Anzahl Ergebnisse.
            min_score: Minimaler Aehnlichkeits-Score (0.0-1.0).

        Returns:
            Liste von Dicts: [{text, scope, type, priority, score, timestamp}]
        """
        query_vector = self._embed_fn(query)
        return self._repo.search(
            query_vector=query_vector,
            scopes=scopes,
            top_k=top_k,
            min_score=min_score,
        )

    def store(
        self,
        text: str,
        scope: str = "projekt",
        type: str = "fakt",
        priority: Optional[int] = None,
    ) -> dict:
        """Speichert eine neue Erinnerung (mit Deduplizierung).

        Rueckgabe-Format identisch mit auto_memory/capture.py::extract_and_store().

        Args:
            text: Der zu speichernde Text.
            scope: Bereich (user, projekt, team, session, global).
            type: Art (entscheidung, fehler, fakt, praeferenz, todo, beobachtung).
            priority: Priority-Score 1-10. Wenn None: Auto nach Type.

        Returns:
            Dict: {id, text, scope, type, priority, stored: True/False, reason?, timestamp?}
        """
        if priority is None:
            priority = _PRIORITY_DEFAULTS_STR.get(type, 5)

        vector = self._embed_fn(text)

        # Deduplizierung: Pruefen ob sehr aehnlicher Eintrag existiert
        dup_result = self._repo.find_duplicate(query_vector=vector, threshold=0.95)
        if dup_result is not None:
            dup_id, dup_score = dup_result
            return {
                "id": dup_id,
                "text": text,
                "scope": scope,
                "type": type,
                "priority": priority,
                "stored": False,
                "reason": f"Duplikat gefunden (Score: {dup_score:.4f})",
            }

        # Neuen Eintrag erstellen via Domain Model
        try:
            scope_enum = MemoryScope(scope)
        except ValueError:
            scope_enum = MemoryScope.PROJEKT
        try:
            type_enum = MemoryType(type)
        except ValueError:
            type_enum = MemoryType.FAKT

        memory = Memory.create(
            text=text,
            scope=scope_enum,
            type=type_enum,
            priority=priority,
        )

        # Speichern via Repository
        self._repo.save(
            point_id=memory.id,
            vector=vector,
            payload={
                "text": memory.text,
                "scope": scope,
                "type": type,
                "priority": memory.priority,
                "timestamp": memory.timestamp,
            },
        )

        return {
            "id": memory.id,
            "text": memory.text,
            "scope": scope,
            "type": type,
            "priority": memory.priority,
            "stored": True,
            "timestamp": memory.timestamp,
        }
