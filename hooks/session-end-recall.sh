#!/bin/bash
# Recall Memory: Konversation bei Session-Ende speichern (S6)
INPUT=$(cat -)

python3 << PYEOF
import json, sqlite3, os, sys
from datetime import datetime

DB_PATH = os.path.expanduser("~/claude-agent-team/brain/recall_memory/conversations.db")

hook_data = json.loads(r"""$INPUT""")
CONV_DATA = hook_data.get("conversation", "")
SESSION_ID = hook_data.get("session_id", "unknown")
AGENT_NAME = hook_data.get("agent_name", "unknown")

if not CONV_DATA:
    print("[RECALL] Keine Konversationsdaten — uebersprungen")
    sys.exit(0)

# Sicherstellen dass Verzeichnis + Tabelle existieren
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT (datetime('now')),
        role TEXT NOT NULL,
        content TEXT,
        tool_calls TEXT,
        metadata TEXT
    )
""")

now = datetime.now().isoformat()
metadata = json.dumps({"agent_name": AGENT_NAME})

# Konversation als einzelne Nachrichten speichern (Message-Level)
messages = json.loads(CONV_DATA) if isinstance(CONV_DATA, str) else CONV_DATA
if isinstance(messages, list):
    for msg in messages:
        conn.execute("""
            INSERT INTO conversations (session_id, timestamp, role, content, tool_calls, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (SESSION_ID, msg.get("timestamp", now), msg.get("role", "unknown"),
              msg.get("content", ""), json.dumps(msg.get("tool_calls")), metadata))
else:
    # Fallback: Gesamte Konversation als einzelnen Eintrag
    conn.execute("""
        INSERT INTO conversations (session_id, timestamp, role, content, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (SESSION_ID, now, "session", str(CONV_DATA), metadata))

conn.commit()
conn.close()
print(f"[RECALL] Konversation gespeichert: {SESSION_ID}")
PYEOF
