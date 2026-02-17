"""Identity Context — Repository (S1 Core Memory)

Persistenz-Schicht fuer Core Memory.
Liest/Schreibt JSON-Datei und synchronisiert Shared-Blocks mit Redis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from brain.identity.model import (
    Block,
    BlockName,
    CoreMemoryState,
    SHARED_BLOCKS,
    StorageType,
)


class CoreMemoryRepository:
    """Repository fuer Core Memory Persistenz.

    Liest den Zustand aus einer JSON-Datei und ueberlagert
    Shared-Blocks mit aktuelleren Werten aus Redis.

    Args:
        json_path: Pfad zur core-memory.json Datei.
        redis_client: Optionaler Redis-Client fuer Shared-Blocks.
    """

    def __init__(self, json_path: str, redis_client=None):
        self._json_path = Path(json_path)
        self._redis = redis_client

    def load(self) -> CoreMemoryState:
        """Laedt den gesamten Core Memory Zustand.

        Liest die JSON-Datei und ueberlagert Shared-Blocks mit Redis-Werten
        (falls Redis verfuegbar und Werte vorhanden).

        Returns:
            CoreMemoryState mit allen Blocks.
        """
        data = self._load_json()
        version = data.get("version", 1)
        raw_blocks = data.get("blocks", {})

        blocks = {}
        for name_str, block_data in raw_blocks.items():
            try:
                block_name = BlockName(name_str)
            except ValueError:
                continue  # Unbekannte Blocks ignorieren

            storage = StorageType(block_data.get("storage", "local"))
            content = block_data.get("content", "")

            # Shared-Blocks: Versuche aktuelleren Wert aus Redis
            if block_name in SHARED_BLOCKS:
                redis_content = self.read_redis_block(name_str)
                if redis_content is not None:
                    content = redis_content

            blocks[block_name] = Block(
                name=block_name,
                content=content,
                storage=storage,
                description=block_data.get("description", ""),
                max_chars=block_data.get("max_chars", 4000),
            )

        return CoreMemoryState(version=version, blocks=blocks)

    def save_block(self, block_name: str, content: str) -> None:
        """Speichert einen Block in der JSON-Datei (und Redis falls shared).

        Args:
            block_name: Name des Blocks (z.B. "USER").
            content: Neuer Inhalt.

        Raises:
            KeyError: Wenn der Block in der JSON-Datei nicht existiert.
        """
        block_upper = block_name.upper()

        # JSON lesen
        data = self._load_json()
        blocks = data.get("blocks", {})

        if block_upper not in blocks:
            raise KeyError(f"Block existiert nicht: {block_upper}")

        # Block-Content updaten
        blocks[block_upper]["content"] = content

        # JSON schreiben
        self._json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Shared-Blocks: Auch in Redis schreiben
        try:
            block_enum = BlockName(block_upper)
        except ValueError:
            block_enum = None

        if block_enum and block_enum in SHARED_BLOCKS and self._redis:
            try:
                self._redis.set(f"core_memory:{block_upper}", content)
            except Exception:
                pass  # Lokales Update war erfolgreich, Redis optional

    def read_redis_block(self, block_name: str) -> Optional[str]:
        """Liest einen Block-Wert aus Redis.

        Args:
            block_name: Name des Blocks (z.B. "USER").

        Returns:
            Block-Inhalt als String oder None falls nicht verfuegbar.
        """
        if not self._redis:
            return None
        try:
            return self._redis.get(f"core_memory:{block_name.upper()}")
        except Exception:
            return None

    def _load_json(self) -> dict:
        """Liest die JSON-Datei von Disk."""
        if not self._json_path.exists():
            return {"version": 1, "blocks": {}}
        with open(self._json_path, "r", encoding="utf-8") as f:
            return json.load(f)
