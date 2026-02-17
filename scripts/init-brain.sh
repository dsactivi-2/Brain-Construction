#!/bin/bash
# ============================================================
# Brain-System Initialisierung — Cloud Code Team 02.26
# Einmal ausfuehren nach frischer Installation
# ============================================================

set -e
echo "=== Brain-System Initialisierung ==="
echo ""

# Projekt-Pfad automatisch erkennen (Verzeichnis in dem dieses Skript liegt)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BRAIN_DIR="$PROJECT_DIR/brain"
CONFIG_DIR="$PROJECT_DIR/config"

# .env laden fuer Passwoerter
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
  echo "[INFO] .env geladen aus: $PROJECT_DIR/.env"
else
  echo "[WARNUNG] Keine .env gefunden — Platzhalter-Passwoerter werden genutzt"
fi

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
python3 << PYEOF
import sqlite3, os

db_path = "$BRAIN_DIR/recall_memory/conversations.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
conn.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
print("  Recall Memory DB erstellt: $BRAIN_DIR/recall_memory/conversations.db")
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
  }' 2>/dev/null && echo "  Qdrant Collection 'hipporag_embeddings' erstellt" || echo "  WARNUNG: Qdrant nicht erreichbar"

curl -s -X PUT "$QDRANT_URL/collections/mem0_memories" \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }' 2>/dev/null && echo "  Qdrant Collection 'mem0_memories' erstellt" || echo "  WARNUNG: Qdrant nicht erreichbar"

# --- 5. Neo4j Constraints erstellen ---
echo "[5/7] Neo4j Constraints erstellen..."
NEO4J_URL="http://localhost:7474"
NEO4J_AUTH="neo4j:${NEO4J_PASSWORD:-DEIN_NEO4J_PASSWORT}"
curl -s -X POST "$NEO4J_URL/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  -u "$NEO4J_AUTH" \
  -d '{
    "statements": [
      {"statement": "CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE"},
      {"statement": "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE"},
      {"statement": "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)"}
    ]
  }' 2>/dev/null && echo "  Neo4j Constraints erstellt" || echo "  WARNUNG: Neo4j nicht erreichbar"

# --- 6. Redis Health-Check ---
echo "[6/7] Redis pruefen..."
docker exec redis redis-cli -a "${REDIS_PASSWORD:-DEIN_REDIS_PASSWORT}" ping 2>/dev/null | grep -q PONG \
  && echo "  Redis: OK" || echo "  WARNUNG: Redis nicht erreichbar"

# --- 7. PostgreSQL Recall Memory (Produktion) ---
echo "[7/7] PostgreSQL Recall Memory..."
docker exec recall-db psql -U recall_user -d recall_memory -c "
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
" 2>/dev/null && echo "  PostgreSQL Tabelle erstellt" || echo "  WARNUNG: PostgreSQL nicht erreichbar"

# --- Zusammenfassung ---
echo ""
echo "=== Initialisierung abgeschlossen ==="
echo ""
echo "Projekt-Pfad: $PROJECT_DIR"
echo "Brain-Pfad:   $BRAIN_DIR"
echo ""
echo "Naechste Schritte:"
echo "  1. Health-Check: bash $PROJECT_DIR/scripts/health-check.sh"
echo "  2. Core Memory befuellen: Nutzer-Infos in ~/.claude/core-memory.json eintragen"
