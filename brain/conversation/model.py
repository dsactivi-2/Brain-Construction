"""Conversation Context — Domain Model (S6 Recall Memory)

Definiert die Nachrichtenstruktur fuer Konversations-Speicherung.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ConversationRole(Enum):
    """Rollen in einer Konversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class Message:
    """Eine einzelne Konversations-Nachricht.

    Attributes:
        id: Datenbank-ID (None vor dem Speichern).
        session_id: Session-Identifier (z.B. UUID).
        timestamp: ISO-Zeitstempel (UTC).
        role: Rolle des Absenders.
        content: Nachrichteninhalt.
        tool_calls: Optionale Tool-Aufrufe als Dict.
        metadata: Optionale zusaetzliche Metadaten.
    """
    id: Optional[int]
    session_id: str
    timestamp: str
    role: ConversationRole
    content: str
    tool_calls: Optional[dict] = None
    metadata: Optional[dict] = None

    @classmethod
    def create(
        cls,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> Message:
        """Factory-Methode fuer neue Nachrichten.

        Erzeugt automatisch einen UTC-Zeitstempel und setzt id=None.

        Args:
            session_id: Session-ID.
            role: Rolle als String (user, assistant, system, tool).
            content: Nachrichteninhalt.
            tool_calls: Optionale Tool-Aufrufe.
            metadata: Optionale Metadaten.

        Returns:
            Neue Message-Instanz.
        """
        return cls(
            id=None,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=ConversationRole(role),
            content=content,
            tool_calls=tool_calls,
            metadata=metadata,
        )

    def to_dict(self) -> dict:
        """Konvertiert die Nachricht in ein Dict.

        Returns:
            Dict mit allen Feldern (role als String-Wert).
        """
        result = {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "role": self.role.value,
            "content": self.content,
        }
        if self.tool_calls is not None:
            result["tool_calls"] = self.tool_calls
        if self.metadata is not None:
            result["metadata"] = self.metadata
        return result
