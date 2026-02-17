"""Conversation Context — Service (S6 Recall Memory)

Applikationslogik fuer Konversations-Speicherung und -Suche.
Gibt Ergebnisse im exakt gleichen Format wie die bisherigen
recall_memory/store.py und recall_memory/search.py zurueck.
"""

from __future__ import annotations

from typing import List, Optional

from brain.conversation.model import Message
from brain.conversation.repository import ConversationRepository


class ConversationService:
    """Service fuer Konversations-Operationen.

    Args:
        repository: ConversationRepository Instanz.
    """

    def __init__(self, repository: ConversationRepository):
        self._repo = repository

    def save(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: dict = None,
        metadata: dict = None,
    ) -> dict:
        """Speichert eine Nachricht in der Recall Memory.

        Gibt das exakt gleiche Format wie recall_memory/store.py zurueck:
        - Erfolg PG: {"id": row_id, "stored_in": "postgresql", "session_id": ...}
        - Erfolg SQLite: {"id": row_id, "stored_in": "sqlite", "session_id": ...}
        - Fehler: {"id": None, "stored_in": "error", "error": message}

        Args:
            session_id: Session-ID (z.B. UUID).
            role: Rolle (user, assistant, system, tool).
            content: Nachrichteninhalt.
            tool_calls: Optionale Tool-Aufrufe als Dict.
            metadata: Optionale Metadaten.

        Returns:
            Dict mit Ergebnis.
        """
        try:
            message = Message.create(
                session_id=session_id,
                role=role,
                content=content,
                tool_calls=tool_calls,
                metadata=metadata,
            )
        except (ValueError, KeyError) as e:
            return {"id": None, "stored_in": "error", "error": str(e)}

        saved = self._repo.save(message)

        if saved.id is not None:
            # Bestimme stored_in anhand der Repository-Logik
            # PostgreSQL wird zuerst versucht, dann SQLite
            stored_in = self._detect_storage()
            return {
                "id": saved.id,
                "stored_in": stored_in,
                "session_id": session_id,
            }

        return {
            "id": None,
            "stored_in": "error",
            "error": "Konnte Nachricht nicht speichern",
        }

    def search(self, query: str, limit: int = 10) -> List[dict]:
        """Full-Text-Suche in Konversationen.

        Gibt das exakt gleiche Format wie recall_memory/search.py zurueck:
        - Liste von Dicts: [{id, session_id, timestamp, role, content}]

        Args:
            query: Suchtext.
            limit: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Ergebnis-Dicts.
        """
        return self._repo.search_text(query=query, limit=limit)

    def search_date(
        self,
        start: str,
        end: str,
        agent: Optional[str] = None,
        limit: int = 20,
    ) -> List[dict]:
        """Datums-basierte Suche in Konversationen.

        Gibt das exakt gleiche Format wie recall_memory/search.py zurueck:
        - Liste von Dicts: [{id, session_id, timestamp, role, content}]

        Args:
            start: Start-Datum (ISO format).
            end: End-Datum (ISO format).
            agent: Optional -- Agent-Name Filter.
            limit: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Ergebnis-Dicts.
        """
        return self._repo.search_date(start=start, end=end, agent=agent, limit=limit)

    def _detect_storage(self) -> str:
        """Erkennt welcher Storage aktiv ist (fuer stored_in Feld)."""
        if self._repo._pg:
            try:
                self._repo._pg.cursor().execute("SELECT 1")
                return "postgresql"
            except Exception:
                pass
        if self._repo._sqlite:
            return "sqlite"
        return "error"
