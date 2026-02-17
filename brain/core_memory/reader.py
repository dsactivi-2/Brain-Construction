"""Core Memory Reader — S1

Liest ~/.claude/core-memory.json und synchronisiert Shared-Blocks mit Redis.
"""

import json
import os
from pathlib import Path

CORE_MEMORY_PATH = Path.home() / ".claude" / "core-memory.json"
SHARED_BLOCKS = {"USER", "PROJEKT", "ENTSCHEIDUNGEN"}


def _load_json() -> dict:
    """Liest core-memory.json von Disk."""
    if not CORE_MEMORY_PATH.exists():
        return {"version": 1, "blocks": {}}
    with open(CORE_MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def core_memory_read(block: str = None) -> dict:
    """Liest Core Memory (komplett oder einzelnen Block).

    Args:
        block: Optional — Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
               Wenn None, werden alle Blocks zurueckgegeben.

    Returns:
        Dict mit Block-Inhalten. Bei einzelnem Block: {"block": name, "content": text, "storage": type}
        Bei allen: {"blocks": {name: {"content": ..., "storage": ...}, ...}}
    """
    data = _load_json()
    blocks = data.get("blocks", {})

    if block:
        block_upper = block.upper().replace("-", "-")
        if block_upper in blocks:
            b = blocks[block_upper]
            content = b.get("content", "")

            # Shared-Blocks: Versuche aus Redis zu lesen (aktueller)
            if block_upper in SHARED_BLOCKS:
                try:
                    from brain.db import get_redis
                    r = get_redis()
                    redis_val = r.get(f"core_memory:{block_upper}")
                    if redis_val:
                        content = redis_val
                except Exception:
                    pass  # Fallback auf JSON

            return {
                "block": block_upper,
                "content": content,
                "storage": b.get("storage", "local"),
            }
        return {"block": block_upper, "content": "", "storage": "unknown", "error": "Block nicht gefunden"}

    # Alle Blocks zurueckgeben
    result = {}
    for name, b in blocks.items():
        content = b.get("content", "")
        if name in SHARED_BLOCKS:
            try:
                from brain.db import get_redis
                r = get_redis()
                redis_val = r.get(f"core_memory:{name}")
                if redis_val:
                    content = redis_val
            except Exception:
                pass
        result[name] = {
            "content": content,
            "storage": b.get("storage", "local"),
            "description": b.get("description", ""),
        }

    return {"blocks": result}
