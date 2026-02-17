#!/bin/bash
# ============================================================
# Brain-System Initialisierung — Cloud Code Team 02.26
# Einmal ausfuehren nach frischer Installation
# ============================================================

set -e
echo "=== Brain-System Initialisierung ==="
echo ""

BRAIN_DIR="$HOME/claude-agent-team/brain"
CONFIG_DIR="$HOME/claude-agent-team/config"

# --- 1. Verzeichnisse erstellen ---
echo "[1/7] Verzeichnisse erstellen..."
mkdir -p "$BRAIN_DIR"/{auto_memory,recall_memory,hipporag_service,agentic_rag,learning_graphs,logs}
mkdir -p "$HOME/.claude"
echo "  OK"

# --- 2. Core Memory Template kopieren ---
echo "[2/7] Core Memory initialisieren..."
if [ ! -f "$HOME/.claude/core-memory.json" ]; then
  cp "$CONFIG_DIR/core-memory.json" "$HOME/.claude/core-memory.json"
  echo "  Core Memory erstellt: ~/.claude/core-memory.json"
else
  echo "  Core Memory existiert bereits — uebersprungen"
fi

# --- 3. Recall Memory (SQLite lokal fuer Entwicklung) ---
echo "[3/7] Recall Memory (SQLite) initialisieren..."
python3 << 'PYEOF'
import sqlite3, os

db_path = os.path.expanduser("~/claude-agent-team/brain/recall_memory/conversations.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
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
conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversations(timestamp)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_role ON conversations(role)")
conn.commit()
conn.close()
print("  Recall Memory DB erstellt: ~/claude-agent-team/brain/recall_memory/conversations.db")
PYEOF

# --- 4. Qdrant Collection erstellen ---
echo "[4/7] Qdrant Collection erstellen..."
QDRANT_URL="http://localhost:6333"
curl -s -X PUT "$QDRANT_URL/collections/hipporag_embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }' 2>/dev/null && echo "  Qdrant Collection erstellt" || echo "  WARNUNG: Qdrant nicht erreichbar (starte Docker zuerst)"

curl -s -X PUT "$QDRANT_URL/collections/mem0_memories" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }' 2>/dev/null && echo "  Mem0 Collection erstellt" || echo "  WARNUNG: Qdrant nicht erreichbar"

# --- 5. Neo4j Constraints erstellen ---
echo "[5/7] Neo4j Constraints erstellen..."
NEO4J_URL="http://localhost:7474"
NEO4J_AUTH="neo4j:DEIN_NEO4J_PASSWORT"
curl -s -X POST "$NEO4J_URL/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  -u "$NEO4J_AUTH" \
  -d '{
    "statements": [
      {"statement": "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE"},
      {"statement": "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE"},
      {"statement": "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)"}
    ]
  }' 2>/dev/null && echo "  Neo4j Constraints erstellt" || echo "  WARNUNG: Neo4j nicht erreichbar (starte Docker zuerst)"

# --- 6. Redis Health-Check ---
echo "[6/7] Redis pruefen..."
redis-cli -a "DEIN_REDIS_PASSWORT" ping 2>/dev/null | grep -q PONG && echo "  Redis: OK" || echo "  WARNUNG: Redis nicht erreichbar"

# --- 7. PostgreSQL Recall Memory (Produktion) ---
echo "[7/7] PostgreSQL Recall Memory (optional)..."
if command -v psql &> /dev/null; then
  PGPASSWORD="SICHERES_PASSWORT" psql -h localhost -U recall_user -d recall_memory -c "
    CREATE TABLE IF NOT EXISTS conversations (
      id            SERIAL PRIMARY KEY,
      session_id    VARCHAR(64) NOT NULL,
      timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      role          VARCHAR(16) NOT NULL,
      content       TEXT,
      tool_calls    JSONB,
      metadata      JSONB
    );
    CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
    CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
    CREATE INDEX IF NOT EXISTS idx_conversations_role ON conversations(role);
  " 2>/dev/null && echo "  PostgreSQL Tabelle erstellt" || echo "  WARNUNG: PostgreSQL nicht erreichbar (SQLite wird als Fallback genutzt)"
else
  echo "  psql nicht installiert — SQLite wird als Fallback genutzt"
fi

# --- Zusammenfassung ---
echo ""
echo "=== Initialisierung abgeschlossen ==="
echo ""
echo "Naechste Schritte:"
echo "  1. Passwoerter in config/databases.yaml und .env setzen"
echo "  2. Core Memory befuellen: claude 'Lies ~/.claude/core-memory.json und fuege Nutzer-Infos hinzu'"
echo "  3. Docker starten: docker compose up -d"
echo "  4. Health-Check: bash scripts/health-check.sh"
