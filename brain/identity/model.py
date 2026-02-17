"""Identity Context — Domain Model (S1 Core Memory)

Definiert die Block-Struktur und den Zustand des Core Memory.
Jeder Agent hat 5 Bloecke: 3 shared (Redis) + 2 private (lokal JSON).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Set


class StorageType(Enum):
    """Speichertyp eines Blocks."""
    REDIS = "redis"
    LOCAL = "local"


class BlockName(Enum):
    """Erlaubte Block-Namen im Core Memory."""
    USER = "USER"
    PROJEKT = "PROJEKT"
    ENTSCHEIDUNGEN = "ENTSCHEIDUNGEN"
    FEHLER_LOG = "FEHLER-LOG"
    AKTUELLE_ARBEIT = "AKTUELLE-ARBEIT"


# Blocks die ueber Redis mit allen Agenten geteilt werden
SHARED_BLOCKS: Set[BlockName] = {
    BlockName.USER,
    BlockName.PROJEKT,
    BlockName.ENTSCHEIDUNGEN,
}

# Maximale Zeichenanzahl pro Block
MAX_CHARS_PER_BLOCK = 4000


@dataclass
class Block:
    """Ein einzelner Core-Memory-Block.

    Attributes:
        name: Block-Bezeichnung (z.B. USER, PROJEKT).
        content: Aktueller Textinhalt.
        storage: Speichertyp (redis = shared, local = agent-only).
        description: Beschreibung des Block-Zwecks.
        max_chars: Maximale Zeichenanzahl (Default 4000).
    """
    name: BlockName
    content: str
    storage: StorageType
    description: str
    max_chars: int = MAX_CHARS_PER_BLOCK

    @property
    def is_shared(self) -> bool:
        """True wenn der Block ueber Redis geteilt wird."""
        return self.name in SHARED_BLOCKS

    def update_content(self, new_content: str) -> None:
        """Aktualisiert den Block-Inhalt mit Laengen-Validierung.

        Args:
            new_content: Neuer Inhalt fuer den Block.

        Raises:
            ValueError: Wenn der Inhalt die maximale Zeichenanzahl ueberschreitet.
        """
        if len(new_content) > self.max_chars:
            raise ValueError(
                f"Content zu lang: {len(new_content)} > {self.max_chars} Zeichen"
            )
        self.content = new_content


@dataclass
class CoreMemoryState:
    """Gesamtzustand des Core Memory.

    Attributes:
        version: Schema-Version (aktuell 1).
        blocks: Dict von BlockName -> Block.
    """
    version: int
    blocks: Dict[BlockName, Block] = field(default_factory=dict)

    def get_block(self, name_str: str) -> Block | None:
        """Gibt einen Block nach String-Name zurueck.

        Args:
            name_str: Block-Name als String (z.B. "USER", "FEHLER-LOG").

        Returns:
            Block oder None wenn nicht gefunden.
        """
        name_upper = name_str.upper()
        for block_name, block in self.blocks.items():
            if block_name.value == name_upper:
                return block
        return None

    def all_blocks(self) -> Dict[str, Block]:
        """Gibt alle Blocks als Dict mit String-Keys zurueck.

        Returns:
            Dict von Block-Name (str) -> Block.
        """
        return {block_name.value: block for block_name, block in self.blocks.items()}
