"""Core Memory Writer — S1

Schreibt Updates in ~/.claude/core-memory.json und synchronisiert Shared-Blocks mit Redis.
"""

import json
from pathlib import Path

CORE_MEMORY_PATH = Path.home() / ".claude" / "core-memory.json"
SHARED_BLOCKS = {"USER", "PROJEKT", "ENTSCHEIDUNGEN"}
MAX_CHARS_PER_BLOCK = 4000


def core_memory_update(block: str, content: str) -> dict:
    """Updated einen Core Memory Block.

    Args:
        block: Name des Blocks (USER, PROJEKT, ENTSCHEIDUNGEN, FEHLER-LOG, AKTUELLE-ARBEIT).
        content: Neuer Inhalt (max 4000 Zeichen).

    Returns:
        Dict mit Ergebnis: {"block": name, "updated": True/False, "chars": len}
    """
    block_upper = block.upper()

    # Validierung
    if len(content) > MAX_CHARS_PER_BLOCK:
        return {
            "block": block_upper,
            "updated": False,
            "error": f"Content zu lang: {len(content)} > {MAX_CHARS_PER_BLOCK} Zeichen",
        }

    # JSON lesen
    if CORE_MEMORY_PATH.exists():
        with open(CORE_MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"version": 1, "max_total_chars": 20000, "blocks": {}}

    # Block updaten
    if block_upper not in data.get("blocks", {}):
        return {"block": block_upper, "updated": False, "error": "Block existiert nicht"}

    data["blocks"][block_upper]["content"] = content

    # JSON schreiben
    CORE_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CORE_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Shared-Blocks: Auch in Redis schreiben
    if block_upper in SHARED_BLOCKS:
        try:
            from brain.db import get_redis
            r = get_redis()
            r.set(f"core_memory:{block_upper}", content)
        except Exception:
            pass  # Lokales Update war erfolgreich, Redis optional

    return {
        "block": block_upper,
        "updated": True,
        "chars": len(content),
        "storage": "redis" if block_upper in SHARED_BLOCKS else "local",
    }
