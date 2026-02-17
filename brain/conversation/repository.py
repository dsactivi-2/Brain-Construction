"""Conversation Context — Repository (S6 Recall Memory)

Persistenz-Schicht fuer Konversations-Nachrichten.
PostgreSQL primaer, SQLite als Fallback.
"""

from __future__ import annotations

import json
from typing import List, Optional

from brain.conversation.model import Message, ConversationRole


# SQL fuer Tabellen-Erstellung
_PG_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    metadata TEXT
)
"""

_SQLITE_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    metadata TEXT
)
"""


class ConversationRepository:
    """Repository fuer Konversations-Persistenz.

    Versucht PostgreSQL zuerst, faellt auf SQLite zurueck.

    Args:
        postgres_conn: Optionale psycopg2-Verbindung.
        sqlite_conn: Optionale sqlite3-Verbindung.
    """

    def __init__(self, postgres_conn=None, sqlite_conn=None):
        self._pg = postgres_conn
        self._sqlite = sqlite_conn
        self._pg_table_ensured = False
        self._sqlite_table_ensured = False

    def _ensure_pg_table(self) -> None:
        """Stellt sicher dass die conversations-Tabelle in PostgreSQL existiert."""
        if self._pg_table_ensured or not self._pg:
            return
        try:
            cur = self._pg.cursor()
            cur.execute(_PG_CREATE_TABLE)
            self._pg_table_ensured = True
        except Exception:
            pass

    def _ensure_sqlite_table(self) -> None:
        """Stellt sicher dass die conversations-Tabelle in SQLite existiert."""
        if self._sqlite_table_ensured or not self._sqlite:
            return
        try:
            self._sqlite.execute(_SQLITE_CREATE_TABLE)
            self._sqlite.commit()
            self._sqlite_table_ensured = True
        except Exception:
            pass

    def save(self, message: Message) -> Message:
        """Speichert eine Nachricht. PostgreSQL zuerst, Fallback SQLite.

        Args:
            message: Die zu speichernde Message.

        Returns:
            Message mit gesetzter ID und stored_in Info.
        """
        tool_calls_json = json.dumps(message.tool_calls) if message.tool_calls else None
        metadata_json = json.dumps(message.metadata) if message.metadata else None

        # Versuche PostgreSQL zuerst
        if self._pg:
            try:
                self._ensure_pg_table()
                cur = self._pg.cursor()
                cur.execute(
                    """
                    INSERT INTO conversations (session_id, timestamp, role, content, tool_calls, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        message.session_id,
                        message.timestamp,
                        message.role.value,
                        message.content,
                        tool_calls_json,
                        metadata_json,
                    ),
                )
                row_id = cur.fetchone()[0]
                message.id = row_id
                return message
            except Exception:
                pass

        # Fallback: SQLite
        if self._sqlite:
            try:
                self._ensure_sqlite_table()
                cur = self._sqlite.execute(
                    """
                    INSERT INTO conversations (session_id, timestamp, role, content, tool_calls, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        message.session_id,
                        message.timestamp,
                        message.role.value,
                        message.content,
                        tool_calls_json,
                        metadata_json,
                    ),
                )
                self._sqlite.commit()
                message.id = cur.lastrowid
                return message
            except Exception:
                pass

        return message

    def search_text(self, query: str, limit: int = 10) -> List[dict]:
        """Full-Text-Suche in Konversationen.

        Verwendet ILIKE auf PostgreSQL, LIKE auf SQLite.

        Args:
            query: Suchtext.
            limit: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts: [{id, session_id, timestamp, role, content}]
        """
        columns = ["id", "session_id", "timestamp", "role", "content"]

        # Versuche PostgreSQL zuerst (mit ILIKE)
        if self._pg:
            try:
                self._ensure_pg_table()
                cur = self._pg.cursor()
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
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception:
                pass

        # Fallback: SQLite
        if self._sqlite:
            try:
                self._ensure_sqlite_table()
                cur = self._sqlite.execute(
                    """
                    SELECT id, session_id, timestamp, role, content
                    FROM conversations
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", limit),
                )
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception:
                pass

        return []

    def search_date(
        self,
        start: str,
        end: str,
        agent: Optional[str] = None,
        limit: int = 20,
    ) -> List[dict]:
        """Datums-basierte Suche in Konversationen.

        Args:
            start: Start-Datum (ISO format, z.B. "2026-02-01").
            end: End-Datum (ISO format, z.B. "2026-02-17").
            agent: Optional -- Filtern nach Agent-Name (in metadata).
            limit: Maximale Anzahl Ergebnisse.

        Returns:
            Liste von Dicts: [{id, session_id, timestamp, role, content}]
        """
        columns = ["id", "session_id", "timestamp", "role", "content"]

        # Versuche PostgreSQL zuerst
        if self._pg:
            try:
                self._ensure_pg_table()
                cur = self._pg.cursor()

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

                return [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception:
                pass

        # Fallback: SQLite
        if self._sqlite:
            try:
                self._ensure_sqlite_table()
                cur = self._sqlite.execute(
                    """
                    SELECT id, session_id, timestamp, role, content
                    FROM conversations
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (start, end, limit),
                )
                return [dict(zip(columns, row)) for row in cur.fetchall()]
            except Exception:
                pass

        return []
