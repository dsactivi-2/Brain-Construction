#!/bin/bash
# ============================================================
# Health-Check — Cloud Code Team 02.26
# Prueft alle Services und Datenbanken
# ============================================================

echo "=== Health-Check: Cloud Code Team 02.26 ==="
echo ""
ERRORS=0

# --- 1. Core Memory ---
echo -n "Core Memory: "
if [ -f "$HOME/.claude/core-memory.json" ]; then
  python3 -c "import json; json.load(open('$HOME/.claude/core-memory.json'))" 2>/dev/null \
    && echo "OK" || { echo "FEHLER (ungueltige JSON)"; ERRORS=$((ERRORS+1)); }
else
  echo "FEHLER (Datei fehlt: ~/.claude/core-memory.json)"
  ERRORS=$((ERRORS+1))
fi

# --- 2. Neo4j ---
echo -n "Neo4j: "
curl -s http://localhost:7474 > /dev/null 2>&1 \
  && echo "OK" || { echo "FEHLER (nicht erreichbar auf Port 7474)"; ERRORS=$((ERRORS+1)); }

# --- 3. Qdrant ---
echo -n "Qdrant: "
curl -s http://localhost:6333/collections > /dev/null 2>&1 \
  && echo "OK" || { echo "FEHLER (nicht erreichbar auf Port 6333)"; ERRORS=$((ERRORS+1)); }

# --- 4. Redis ---
echo -n "Redis: "
redis-cli -a "${REDIS_PASSWORD:-DEIN_REDIS_PASSWORT}" ping 2>/dev/null | grep -q PONG \
  && echo "OK" || { echo "FEHLER (nicht erreichbar auf Port 6379)"; ERRORS=$((ERRORS+1)); }

# --- 5. PostgreSQL ---
echo -n "PostgreSQL: "
PGPASSWORD="${RECALL_DB_PASSWORD:-SICHERES_PASSWORT}" psql -h localhost -U recall_user -d recall_memory -c "SELECT 1" > /dev/null 2>&1 \
  && echo "OK" || { echo "WARNUNG (nicht erreichbar — SQLite Fallback aktiv?)"; }

# --- 6. SQLite Recall Memory (Fallback) ---
echo -n "SQLite Recall: "
DB_FILE="$HOME/claude-agent-team/brain/recall_memory/conversations.db"
if [ -f "$DB_FILE" ]; then
  sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM conversations" > /dev/null 2>&1 \
    && echo "OK ($(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM conversations") Eintraege)" \
    || { echo "FEHLER (Tabelle fehlt)"; ERRORS=$((ERRORS+1)); }
else
  echo "Nicht initialisiert (bash scripts/init-brain.sh ausfuehren)"
fi

# --- 7. HippoRAG Service ---
echo -n "HippoRAG: "
curl -s http://localhost:8102/health > /dev/null 2>&1 \
  && echo "OK" || echo "NICHT AKTIV (Degraded: S3 deaktiviert)"

# --- 8. Learning-Graphs ---
echo -n "Learning-Graphs: "
docker exec learning_graphs python3 -c "print('OK')" 2>/dev/null \
  && echo "OK" || echo "NICHT AKTIV (Degraded: S5 deaktiviert)"

# --- 9. Hook-Skripte ---
echo -n "Hook-Skripte: "
HOOKS_DIR="$HOME/claude-agent-team/hooks"
HOOK_COUNT=$(ls "$HOOKS_DIR"/*.sh 2>/dev/null | wc -l)
if [ "$HOOK_COUNT" -ge 10 ]; then
  echo "OK ($HOOK_COUNT Skripte)"
else
  echo "WARNUNG (nur $HOOK_COUNT von 12 Skripten gefunden)"
fi

# --- 10. settings.json ---
echo -n "Settings: "
SETTINGS="$HOME/claude-agent-team/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
  python3 -c "import json; d=json.load(open('$SETTINGS')); print(f'OK ({len(d.get(\"hooks\", {}))} Hook-Typen)')" 2>/dev/null \
    || { echo "FEHLER (ungueltige JSON)"; ERRORS=$((ERRORS+1)); }
else
  echo "FEHLER (Datei fehlt)"
  ERRORS=$((ERRORS+1))
fi

# --- 11. Degraded Mode ---
echo ""
echo "=== Degraded Mode Status ==="
DEGRADED=false
curl -s http://localhost:7474 > /dev/null 2>&1 || { echo "WARNUNG: Neo4j down → S3/S5 deaktiviert"; DEGRADED=true; }
curl -s http://localhost:6333 > /dev/null 2>&1 || { echo "WARNUNG: Qdrant down → S2 nur Redis-Cache"; DEGRADED=true; }
redis-cli -a "${REDIS_PASSWORD:-DEIN_REDIS_PASSWORT}" ping 2>/dev/null | grep -q PONG || { echo "WARNUNG: Redis down → Kein Cache/Event-Bus"; DEGRADED=true; }

if [ "$DEGRADED" = true ]; then
  echo "SYSTEM LAEUFT IM DEGRADED MODE — einige Schichten deaktiviert"
else
  echo "Alle Systeme operational"
fi

# --- Zusammenfassung ---
echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo "=== $ERRORS FEHLER gefunden — bitte beheben ==="
  exit 1
else
  echo "=== Health-Check bestanden ==="
  exit 0
fi
