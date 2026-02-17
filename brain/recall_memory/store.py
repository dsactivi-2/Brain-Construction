"""Recall Memory Store — S6 (PostgreSQL + SQLite Fallback)

Speichert Konversations-Nachrichten. PostgreSQL primaer, SQLite als Fallback.
"""

import json
from datetime import datetime, timezone


def save_conversation(
    session_id: str,
    role: str,
    content: str,
    tool_calls: dict = None,
    metadata: dict = None,
) -> dict:
    """Speichert eine Nachricht in der Recall Memory.

    Args:
        session_id: Session-ID (z.B. UUID).
        role: Rolle (user, assistant, system, tool).
        content: Nachrichteninhalt.
        tool_calls: Optional — Tool-Aufrufe als Dict.
        metadata: Optional — Zusaetzliche Metadaten.

    Returns:
        Dict: {id, stored_in, session_id}
    """
    tool_calls_json = json.dumps(tool_calls) if tool_calls else None
    metadata_json = json.dumps(metadata) if metadata else None
    timestamp = datetime.now(timezone.utc).isoformat()

    # Versuche PostgreSQL zuerst
    try:
        from brain.db import get_postgres
        conn = get_postgres()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversations (session_id, timestamp, role, content, tool_calls, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (session_id, timestamp, role, content, tool_calls_json, metadata_json),
        )
        row_id = cur.fetchone()[0]
        return {"id": row_id, "stored_in": "postgresql", "session_id": session_id}
    except Exception:
        pass

    # Fallback: SQLite
    try:
        from brain.db import get_sqlite
        conn = get_sqlite()
        cur = conn.execute(
            """
            INSERT INTO conversations (session_id, timestamp, role, content, tool_calls, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, timestamp, role, content, tool_calls_json, metadata_json),
        )
        conn.commit()
        return {"id": cur.lastrowid, "stored_in": "sqlite", "session_id": session_id}
    except Exception as e:
        return {"id": None, "stored_in": "error", "error": str(e)}
