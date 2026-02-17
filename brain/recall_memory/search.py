"""Recall Memory Search — S6 (PostgreSQL + SQLite Fallback)

Full-Text-Suche und Datums-basierte Suche in Konversationen.
"""

from typing import List, Optional


def conversation_search(query: str, limit: int = 10) -> List[dict]:
    """Full-Text-Suche in Konversationen.

    Args:
        query: Suchtext.
        limit: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{id, session_id, timestamp, role, content}]
    """
    # Versuche PostgreSQL zuerst (mit ILIKE)
    try:
        from brain.db import get_postgres
        conn = get_postgres()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, session_id, timestamp, role, content
            FROM conversations
            WHERE content ILIKE %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (f"%{query}%", limit),
        )
        columns = ["id", "session_id", "timestamp", "role", "content"]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception:
        pass

    # Fallback: SQLite
    try:
        from brain.db import get_sqlite
        conn = get_sqlite()
        cur = conn.execute(
            """
            SELECT id, session_id, timestamp, role, content
            FROM conversations
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (f"%{query}%", limit),
        )
        columns = ["id", "session_id", "timestamp", "role", "content"]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception:
        return []


def conversation_search_date(
    start: str,
    end: str,
    agent: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """Datums-basierte Suche in Konversationen.

    Args:
        start: Start-Datum (ISO format, z.B. "2026-02-01").
        end: End-Datum (ISO format, z.B. "2026-02-17").
        agent: Optional — Filtern nach Agent-Name (in metadata).
        limit: Maximale Anzahl Ergebnisse.

    Returns:
        Liste von Dicts: [{id, session_id, timestamp, role, content}]
    """
    # Versuche PostgreSQL zuerst
    try:
        from brain.db import get_postgres
        conn = get_postgres()
        cur = conn.cursor()

        if agent:
            cur.execute(
                """
                SELECT id, session_id, timestamp, role, content
                FROM conversations
                WHERE timestamp >= %s AND timestamp <= %s
                  AND metadata->>'agent' = %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (start, end, agent, limit),
            )
        else:
            cur.execute(
                """
                SELECT id, session_id, timestamp, role, content
                FROM conversations
                WHERE timestamp >= %s AND timestamp <= %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (start, end, limit),
            )

        columns = ["id", "session_id", "timestamp", "role", "content"]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception:
        pass

    # Fallback: SQLite
    try:
        from brain.db import get_sqlite
        conn = get_sqlite()
        cur = conn.execute(
            """
            SELECT id, session_id, timestamp, role, content
            FROM conversations
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (start, end, limit),
        )
        columns = ["id", "session_id", "timestamp", "role", "content"]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    except Exception:
        return []
