"""Semantic Memory Domain Model — S2

Entitaeten und Wertobjekte fuer die semantische Erinnerungsverwaltung.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Optional
import uuid


class MemoryScope(Enum):
    """Gueltigkeitsbereich einer Erinnerung."""
    USER = "user"
    PROJEKT = "projekt"
    TEAM = "team"
    SESSION = "session"
    GLOBAL = "global"


class MemoryType(Enum):
    """Art der Erinnerung — bestimmt Default-Priority."""
    ENTSCHEIDUNG = "entscheidung"
    FEHLER = "fehler"
    FAKT = "fakt"
    PRAEFERENZ = "praeferenz"
    TODO = "todo"
    BEOBACHTUNG = "beobachtung"


# Default Priority-Scores nach Type
PRIORITY_DEFAULTS = {
    MemoryType.ENTSCHEIDUNG: 9,
    MemoryType.FEHLER: 8,
    MemoryType.FAKT: 7,
    MemoryType.PRAEFERENZ: 6,
    MemoryType.TODO: 5,
    MemoryType.BEOBACHTUNG: 3,
}


@dataclass
class Memory:
    """Eine semantische Erinnerung im Qdrant-Speicher."""
    id: str
    text: str
    scope: MemoryScope
    type: MemoryType
    priority: int
    timestamp: str

    @classmethod
    def create(
        cls,
        text: str,
        scope: MemoryScope,
        type: MemoryType,
        priority: Optional[int] = None,
    ) -> "Memory":
        """Factory-Methode: Erstellt neue Memory mit UUID und Timestamp.

        Args:
            text: Der zu speichernde Text.
            scope: Gueltigkeitsbereich.
            type: Art der Erinnerung.
            priority: Priority-Score 1-10. Wenn None: Auto nach Type.

        Returns:
            Neue Memory-Instanz.
        """
        if priority is None:
            priority = PRIORITY_DEFAULTS.get(type, 5)

        return cls(
            id=str(uuid.uuid4()),
            text=text,
            scope=scope,
            type=type,
            priority=priority,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(frozen=True)
class MemorySearchResult:
    """Ein Suchergebnis aus der semantischen Suche."""
    memory: Memory
    score: float

    def to_dict(self) -> dict:
        """Konvertiert zu Dict im Compat-Format (wie recall.py).

        Returns:
            Dict: {text, scope, type, priority, score, timestamp}
        """
        return {
            "text": self.memory.text,
            "scope": self.memory.scope.value if isinstance(self.memory.scope, MemoryScope) else self.memory.scope,
            "type": self.memory.type.value if isinstance(self.memory.type, MemoryType) else self.memory.type,
            "priority": self.memory.priority,
            "score": self.score,
            "timestamp": self.memory.timestamp,
        }
