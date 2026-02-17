"""Identity Context — Service (S1 Core Memory)

Applikationslogik fuer Core Memory Lese- und Schreiboperationen.
Gibt Ergebnisse im exakt gleichen Format wie die bisherigen
core_memory/reader.py und core_memory/writer.py zurueck.
"""

from __future__ import annotations

from brain.identity.model import SHARED_BLOCKS, MAX_CHARS_PER_BLOCK
from brain.identity.repository import CoreMemoryRepository


class CoreMemoryService:
    """Service fuer Core Memory Operationen.

    Args:
        repository: CoreMemoryRepository Instanz.
    """

    def __init__(self, repository: CoreMemoryRepository):
        self._repo = repository

    def read(self, block: str = None) -> dict:
        """Liest Core Memory (komplett oder einzelnen Block).

        Gibt das exakt gleiche Format wie core_memory/reader.py zurueck:
        - Einzelner Block: {"block": name, "content": text, "storage": type}
        - Alle Blocks: {"blocks": {name: {"content": ..., "storage": ..., "description": ...}}}

        Args:
            block: Optional -- Name des Blocks. Wenn None, alle Blocks.

        Returns:
            Dict mit Block-Inhalten.
        """
        state = self._repo.load()

        if block:
            block_upper = block.upper()
            block_obj = state.get_block(block_upper)

            if block_obj:
                return {
                    "block": block_upper,
                    "content": block_obj.content,
                    "storage": block_obj.storage.value,
                }
            return {
                "block": block_upper,
                "content": "",
                "storage": "unknown",
                "error": "Block nicht gefunden",
            }

        # Alle Blocks zurueckgeben
        result = {}
        for name_str, block_obj in state.all_blocks().items():
            result[name_str] = {
                "content": block_obj.content,
                "storage": block_obj.storage.value,
                "description": block_obj.description,
            }

        return {"blocks": result}

    def update(self, block: str, content: str) -> dict:
        """Updated einen Core Memory Block.

        Gibt das exakt gleiche Format wie core_memory/writer.py zurueck:
        - Erfolg: {"block": name, "updated": True, "chars": len, "storage": type}
        - Fehler: {"block": name, "updated": False, "error": message}

        Args:
            block: Name des Blocks.
            content: Neuer Inhalt (max 4000 Zeichen).

        Returns:
            Dict mit Ergebnis.
        """
        block_upper = block.upper()

        # Laengen-Validierung
        if len(content) > MAX_CHARS_PER_BLOCK:
            return {
                "block": block_upper,
                "updated": False,
                "error": f"Content zu lang: {len(content)} > {MAX_CHARS_PER_BLOCK} Zeichen",
            }

        # Pruefen ob Block existiert
        state = self._repo.load()
        block_obj = state.get_block(block_upper)

        if not block_obj:
            return {
                "block": block_upper,
                "updated": False,
                "error": "Block existiert nicht",
            }

        # Speichern via Repository
        try:
            self._repo.save_block(block_upper, content)
        except KeyError:
            return {
                "block": block_upper,
                "updated": False,
                "error": "Block existiert nicht",
            }

        # Storage-Typ bestimmen
        is_shared = block_obj.name in SHARED_BLOCKS
        storage = "redis" if is_shared else "local"

        return {
            "block": block_upper,
            "updated": True,
            "chars": len(content),
            "storage": storage,
        }
