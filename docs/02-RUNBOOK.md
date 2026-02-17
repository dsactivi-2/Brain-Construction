# RUNBOOK — Cloud Code Team 02.26

Bau- und Deploy-Anleitung fuer die Agenten die dieses System erstellen und betreiben.

---

## Uebersicht: Bau-Reihenfolge

```
Schritt 1: Infrastruktur (Datenbanken + Server)
    │
    ▼
Schritt 2: Gehirn-System (HippoRAG 2 + Agentic RAG + Learning Graphs)
    │
    ▼
Schritt 3: MCP-Server (RAG-API + Doc-Scanner + Connectoren)
    │
    ▼
Schritt 4: Hook-System (17 Hooks konfigurieren)
    │
    ▼
Schritt 5: Agenten-Profile (10 Agenten + Grundprofil)
    │
    ▼
Schritt 6: Kommunikation (Slack/WhatsApp/Linear Webhooks)
    │
    ▼
Schritt 7: Fragenkatalog-System
    │
    ▼
Schritt 8: Web-Scanner + KB-Import
    │
    ▼
Schritt 9: Sync-System
    │
    ▼
Schritt 10: Cloud-Deployment (Docker + CI/CD)
    │
    ▼
Schritt 11: Tests + Health-Check
    │
    ▼
Schritt 12: Dokumentation generieren
```

---

## Schritt 1: Infrastruktur

### 1.1 Neo4j (Graph-Datenbank)

**Zweck:** Wissensgraph fuer HippoRAG 2 + Agentic Learning Graphs

**Befehle:**
```bash
# Docker Container starten
docker run -d \
  --name neo4j \
  --restart always \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/SICHERES_PASSWORT \
  -e NEO4J_PLUGINS='["apoc", "graph-data-science"]' \
  -v neo4j-data:/data \
  -v neo4j-logs:/logs \
  neo4j:5-community

# Verbindung testen
curl http://localhost:7474
```

**Pruefung:** Browser oeffnen → http://localhost:7474 → Login mit neo4j/PASSWORT
**Fehlerbehandlung:** Port belegt → `docker ps` pruefen, alten Container stoppen
**Rollback:** `docker stop neo4j && docker rm neo4j`

### 1.2 Qdrant (Vektor-Datenbank)

**Zweck:** Embeddings fuer semantische Suche

**Befehle:**
```bash
# Docker Container starten
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant-data:/qdrant/storage \
  qdrant/qdrant:latest

# Verbindung testen
curl http://localhost:6333/dashboard
```

**Pruefung:** http://localhost:6333/dashboard erreichbar
**Fehlerbehandlung:** Port belegt → anderen Port mappen: `-p 6335:6333`
**Rollback:** `docker stop qdrant && docker rm qdrant`

### 1.3 Redis (Cache + Queue)

**Zweck:** Smart Cache, Task-Queue, Fragenkatalog

**Befehle:**
```bash
# Docker Container starten
docker run -d \
  --name redis \
  --restart always \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes --requirepass SICHERES_PASSWORT

# Verbindung testen
docker exec -it redis redis-cli -a SICHERES_PASSWORT ping
# Antwort: PONG
```

**Pruefung:** `PONG` als Antwort
**Fehlerbehandlung:** `docker logs redis` pruefen
**Rollback:** `docker stop redis && docker rm redis`

### 1.4 Abhaengigkeiten zwischen Datenbanken

```
Neo4j       → Unabhaengig, kann zuerst starten
Qdrant      → Unabhaengig, kann parallel starten
Redis       → Unabhaengig, kann parallel starten

Alle 3 muessen laufen BEVOR Schritt 2 beginnt.
```

---

## Schritt 2: Gehirn-System

### 2.1 HippoRAG 2 Setup

**Zweck:** Wissensgraph + PageRank + Langzeitgedaechtnis

**Befehle:**
```bash
# Projekt-Verzeichnis erstellen
mkdir -p ~/claude-agent-team/brain
cd ~/claude-agent-team/brain

# Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Abhaengigkeiten installieren
pip install neo4j qdrant-client redis sentence-transformers \
  openai tiktoken networkx numpy pydantic fastapi uvicorn

# HippoRAG 2 Konfiguration erstellen
cat > config.yaml << 'EOF'
hipporag:
  neo4j:
    uri: bolt://localhost:7687
    user: neo4j
    password: SICHERES_PASSWORT
  qdrant:
    url: http://localhost:6333
    collection: hipporag_embeddings
  redis:
    url: redis://:SICHERES_PASSWORT@localhost:6379/0
  embedding_model: all-MiniLM-L6-v2
  pagerank:
    damping_factor: 0.85
    max_iterations: 100
EOF
```

**Pruefung:**
```bash
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'SICHERES_PASSWORT'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('Neo4j OK:', result.single()[0])
driver.close()
"
```

**Fehlerbehandlung:** Connection refused → Docker Container laeuft nicht → `docker start neo4j`
**Rollback:** `rm -rf ~/claude-agent-team/brain/venv`

### 2.2 Agentic RAG Setup

**Zweck:** Intelligente Suchsteuerung + Selbst-Korrektur

**Befehle:**
```bash
cd ~/claude-agent-team/brain

# Agentic RAG Modul erstellen
mkdir -p agentic_rag
cat > agentic_rag/__init__.py << 'EOF'
# Agentic RAG — Suchsteuerung + Bewertung
# Entscheidet: WANN suchen, WO suchen, WIE bewerten
# Korrigiert sich selbst bei schlechten Ergebnissen
EOF
```

**Abhaengigkeit:** HippoRAG 2 muss konfiguriert sein (Schritt 2.1)

### 2.3 Agentic Learning Graphs Setup

**Zweck:** Selbst-erweiterndes Wissensnetz

**Befehle:**
```bash
cd ~/claude-agent-team/brain

# Learning Graphs Modul erstellen
mkdir -p learning_graphs
cat > learning_graphs/__init__.py << 'EOF'
# Agentic Learning Graphs — Selbst-Erweiterung
# Agent baut eigenes Wissensnetz das mit jeder Interaktion waechst
# Neue Entitaeten + Beziehungen werden automatisch hinzugefuegt
EOF
```

**Abhaengigkeit:** Neo4j (Schritt 1.1) + HippoRAG 2 (Schritt 2.1)

---

## Schritt 3: MCP-Server

### 3.1 RAG-API MCP-Server

**Zweck:** Alle Agenten greifen auf das Gehirn-System zu

**Befehle:**
```bash
cd ~/claude-agent-team
mkdir -p mcp-servers/rag-api

cat > mcp-servers/rag-api/server.py << 'EOF'
# MCP Server fuer HippoRAG 2 + Agentic RAG
# Tools:
#   - memory_store: Wissen speichern
#   - memory_search: Wissen suchen (semantisch + Graph)
#   - memory_connect: Beziehung zwischen Entitaeten erstellen
#   - cache_get: Cached Ergebnis abrufen
#   - cache_set: Ergebnis cachen
EOF

# Server starten
# uvicorn mcp-servers.rag-api.server:app --host 0.0.0.0 --port 8100
```

**Pruefung:** `curl http://localhost:8100/health`
**Fehlerbehandlung:** Port belegt → anderen Port waehlen
**Rollback:** Prozess beenden: `kill $(lsof -t -i:8100)`

### 3.2 Doc-Scanner MCP-Server

**Zweck:** Web-Dokumentationen scannen + importieren

**Befehle:**
```bash
mkdir -p mcp-servers/doc-scanner

pip install beautifulsoup4 playwright aiohttp difflib

# Playwright Browser installieren (fuer JS-Seiten)
playwright install chromium

cat > mcp-servers/doc-scanner/server.py << 'EOF'
# MCP Server fuer Doc-Scanner
# Tools:
#   - scan_url: Eine URL scannen und importieren
#   - scan_list: Alle ueberwachten URLs anzeigen
#   - scan_add: Neue URL zur Ueberwachung hinzufuegen
#   - scan_diff: Aenderungen seit letztem Scan
#   - scan_schedule: Scan-Zyklus konfigurieren
EOF
```

**Abhaengigkeit:** RAG-API (Schritt 3.1) muss laufen

### 3.3 GitHub + Notion Connectoren

**Befehle:**
```bash
# GitHub MCP installieren
npm install -g @modelcontextprotocol/server-github

# Notion MCP installieren
npm install -g @modelcontextprotocol/server-notion

# In Claude Code registrieren
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

**Pruefung:** `claude mcp list` → GitHub und Notion sichtbar
**Fehlerbehandlung:** API-Keys pruefen (GITHUB_TOKEN, NOTION_TOKEN)

---

## Schritt 4: Hook-System

### 4.1 Hook-Skripte erstellen

**Befehle:**
```bash
mkdir -p ~/.claude/hooks

# Alle 17 Hook-Skripte erstellen
# (Detaillierte Inhalte werden in Phase "Bauen" erstellt)

# Skripte ausfuehrbar machen
chmod +x ~/.claude/hooks/*.sh
```

### 4.2 settings.json konfigurieren

```bash
# settings.json mit allen 17 Hooks schreiben
cat > ~/.claude/settings.json << 'SETTINGSEOF'
{
  "hooks": {
    "SessionStart": [
      {"matcher": "startup", "type": "command", "command": "bash ~/.claude/hooks/session-start-startup.sh", "timeout": 15000},
      {"matcher": "compact", "type": "command", "command": "bash ~/.claude/hooks/session-start-compact.sh", "timeout": 10000},
      {"matcher": "resume", "type": "command", "command": "bash ~/.claude/hooks/session-start-resume.sh", "timeout": 15000}
    ],
    "UserPromptSubmit": [
      {"type": "command", "command": "bash ~/.claude/hooks/user-prompt-submit.sh", "timeout": 5000}
    ],
    "PreToolUse": [
      {"matcher": "Write|Edit", "type": "agent", "prompt": "Pruefe ob dieser Code-Aenderung sicher ist. Keine Secrets, keine Injection, keine gefaehrlichen Patterns.", "timeout": 30000},
      {"matcher": "Bash", "type": "agent", "prompt": "Pruefe ob dieser Bash-Befehl sicher ist. Blockiere: rm -rf /, DROP TABLE, --force auf main/master, Secrets in Befehlen.", "timeout": 30000}
    ],
    "PostToolUse": [
      {"matcher": "Write|Edit", "type": "command", "command": "bash ~/.claude/hooks/post-tool-write.sh", "timeout": 30000},
      {"matcher": "Bash", "type": "command", "command": "bash ~/.claude/hooks/post-tool-bash.sh", "timeout": 10000}
    ],
    "PostToolUseFailure": [
      {"type": "command", "command": "bash ~/.claude/hooks/post-tool-failure.sh", "timeout": 10000}
    ],
    "PreCompact": [
      {"type": "command", "command": "bash ~/.claude/hooks/pre-compact.sh", "timeout": 15000}
    ],
    "Stop": [
      {"type": "agent", "prompt": "Pruefe ob alle zugewiesenen Tasks erledigt sind. Kein Task darf uebersprungen oder als erledigt markiert sein ohne tatsaechlich erledigt zu sein.", "timeout": 60000}
    ],
    "SubagentStart": [
      {"type": "command", "command": "bash ~/.claude/hooks/subagent-start.sh", "timeout": 10000}
    ],
    "SubagentStop": [
      {"type": "agent", "prompt": "Pruefe die Qualitaet der Subagent-Ausgabe. Ist die Aufgabe vollstaendig und korrekt erledigt?", "timeout": 60000}
    ],
    "Notification": [
      {"type": "command", "command": "bash ~/.claude/hooks/notification.sh", "timeout": 10000}
    ],
    "TeammateIdle": [
      {"type": "agent", "prompt": "Pruefe ob dieser Agent seine Aufgaben vollstaendig erledigt hat bevor er pausiert.", "timeout": 30000}
    ],
    "TaskCompleted": [
      {"type": "agent", "prompt": "Verifiziere dass dieser Task WIRKLICH erledigt ist. Pruefe: Code geschrieben? Tests bestanden? Review OK? Nichts uebersprungen?", "timeout": 60000}
    ],
    "SessionEnd": [
      {"type": "command", "command": "bash ~/.claude/hooks/session-end.sh", "timeout": 15000}
    ]
  }
}
SETTINGSEOF
```

**Pruefung:** `cat ~/.claude/settings.json | python3 -m json.tool` → Valides JSON
**Fehlerbehandlung:** JSON-Syntax-Fehler → online JSON Validator nutzen
**Rollback:** Backup wiederherstellen (install.sh erstellt automatisch Backups)

---

## Schritt 5: Agenten-Profile

### 5.1 Grundprofil erstellen

```bash
mkdir -p ~/.claude/agents

# Grundprofil das alle Agenten erben
cat > ~/.claude/agents/grundprofil.md << 'EOF'
# Grundprofil (wird von allen Agenten geladen)
[Inhalt aus Projektplanung Abschnitt 3.0]
EOF
```

### 5.2 Individuelle Agenten erstellen

```bash
# Fuer jeden der 10 Agenten:
for agent in berater architekt coder tester reviewer designer analyst doc-scanner devops dokumentierer; do
  cat > ~/.claude/agents/$agent.md << EOF
---
name: "$agent"
description: "Agent-Beschreibung"
---
# $agent Agent
[Rules + Commands aus Projektplanung]
EOF
done
```

**Pruefung:** `ls ~/.claude/agents/` → 11 Dateien (10 Agenten + Grundprofil)
**Fehlerbehandlung:** Fehlende Datei → manuell erstellen
**Rollback:** `rm ~/.claude/agents/*.md`

---

## Schritt 6: Kommunikation

### 6.1 Slack Webhook

```bash
# 1. Slack App erstellen: https://api.slack.com/apps
# 2. Incoming Webhook aktivieren
# 3. Webhook URL speichern

cat > ~/.claude/config/communication.json << 'EOF'
{
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/DEIN/WEBHOOK/URL",
    "channel": "#claude-agent-team",
    "notify_on": ["blocker", "fertig", "fehler"]
  }
}
EOF
```

### 6.2 WhatsApp Business API

```bash
# 1. Meta Business Account: https://business.facebook.com
# 2. WhatsApp Business API einrichten
# 3. Token + Phone Number ID speichern

# In communication.json ergaenzen:
# "whatsapp": {
#   "token": "DEIN_TOKEN",
#   "phone_id": "DEINE_PHONE_ID",
#   "notify_on": ["blocker", "fertig"]
# }
```

### 6.3 Linear API

```bash
# 1. Linear Account: https://linear.app
# 2. API Key erstellen: Settings → API
# 3. Team + Project ID notieren

# In communication.json ergaenzen:
# "linear": {
#   "api_key": "DEIN_API_KEY",
#   "team_id": "TEAM_ID",
#   "project_id": "PROJECT_ID"
# }
```

**Pruefung:** Test-Nachricht senden:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Agent-Team Test"}' \
  DEINE_SLACK_WEBHOOK_URL
```

---

## Schritt 7: Fragenkatalog-System

```bash
mkdir -p ~/claude-agent-team/fragenkatalog

cat > ~/claude-agent-team/fragenkatalog/katalog.json << 'EOF'
{
  "blocker": [],
  "offen": [],
  "beantwortet": []
}
EOF
```

**Gespeichert in:** Redis (fuer schnellen Zugriff) + HippoRAG 2 (fuer Langzeit)
**Abhaengigkeit:** Redis (Schritt 1.3) + Notification Hook (Schritt 4)

---

## Schritt 8: Web-Scanner + KB-Import

```bash
cd ~/claude-agent-team

# URL-Liste erstellen
cat > config/scan-urls.json << 'EOF'
{
  "urls": [
    {
      "url": "https://docs.example.com",
      "scope": "global",
      "interval_days": 7
    }
  ]
}
EOF

# Cron-Job einrichten (Linux/Mac)
(crontab -l 2>/dev/null; echo "0 3 * * 0 cd ~/claude-agent-team && python3 mcp-servers/doc-scanner/scan.py") | crontab -

# Fuer Windows: Task Scheduler nutzen
```

**Pruefung:** `python3 mcp-servers/doc-scanner/scan.py --test`
**Abhaengigkeit:** RAG-API (Schritt 3.1) + HippoRAG 2 (Schritt 2.1)

---

## Schritt 9: Sync-System

```bash
cd ~/claude-agent-team

# Sync-Repo initialisieren
bash scripts/sync-setup.sh init

# Remote hinzufuegen
cd ~/.claude/sync-repo
git remote add origin https://github.com/DEIN-USER/claude-agent-team-config.git
git push -u origin main
```

**Pruefung:** `bash scripts/sync-setup.sh --status`
**Abhaengigkeit:** GitHub-Repo muss existieren

---

## Schritt 10: Cloud-Deployment

### 10.1 Docker Compose

```bash
cd ~/claude-agent-team

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  neo4j:
    image: neo4j:5-community
    restart: always
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc", "graph-data-science"]'
    volumes:
      - neo4j-data:/data
      - neo4j-logs:/logs

  qdrant:
    image: qdrant/qdrant:latest
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - qdrant-data:/qdrant/storage

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data

  rag-api:
    build: ./mcp-servers/rag-api
    restart: always
    ports:
      - "8100:8100"
    depends_on:
      - neo4j
      - qdrant
      - redis
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      QDRANT_URL: http://qdrant:6333
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0

  doc-scanner:
    build: ./mcp-servers/doc-scanner
    restart: always
    ports:
      - "8101:8101"
    depends_on:
      - rag-api
    environment:
      RAG_API_URL: http://rag-api:8100

volumes:
  neo4j-data:
  neo4j-logs:
  qdrant-data:
  redis-data:
EOF

# .env Datei erstellen
cat > .env << 'EOF'
NEO4J_PASSWORD=SICHERES_PASSWORT_HIER
REDIS_PASSWORD=SICHERES_PASSWORT_HIER
CLAUDE_API_KEY=DEIN_API_KEY
EOF
```

### 10.2 Deployment

```bash
# Alles starten
docker compose up -d

# Status pruefen
docker compose ps

# Logs pruefen
docker compose logs -f
```

**Pruefung:** Alle Container laufen (`docker compose ps` → Status: Up)
**Fehlerbehandlung:** `docker compose logs SERVICE_NAME` fuer Fehlerdetails
**Rollback:** `docker compose down` (Daten bleiben in Volumes)

---

## Schritt 11: Tests + Health-Check

```bash
# Health-Check Skript
cat > scripts/health-check.sh << 'HEALTHEOF'
#!/bin/bash
echo "=== Cloud Code Team Health-Check ==="

# Neo4j
echo -n "Neo4j: "
curl -s http://localhost:7474 > /dev/null && echo "OK" || echo "FEHLER"

# Qdrant
echo -n "Qdrant: "
curl -s http://localhost:6333/dashboard > /dev/null && echo "OK" || echo "FEHLER"

# Redis
echo -n "Redis: "
docker exec redis redis-cli -a $REDIS_PASSWORD ping 2>/dev/null | grep -q PONG && echo "OK" || echo "FEHLER"

# RAG-API
echo -n "RAG-API: "
curl -s http://localhost:8100/health > /dev/null && echo "OK" || echo "FEHLER"

# Doc-Scanner
echo -n "Doc-Scanner: "
curl -s http://localhost:8101/health > /dev/null && echo "OK" || echo "FEHLER"

echo "=== Ende ==="
HEALTHEOF

chmod +x scripts/health-check.sh
bash scripts/health-check.sh
```

**Erwartung:** Alle Services zeigen "OK"
**Fehlerbehandlung:** Fehlender Service → Container pruefen → neustarten

---

## Schritt 12: Dokumentation generieren

```bash
# TypeDoc fuer TypeScript
npx typedoc --entryPoints src --out docs/api

# Swagger/OpenAPI
# Wird automatisch vom PostToolUse Hook generiert

# Changelog
npx changeset version

# Storybook (wenn Frontend vorhanden)
npx storybook build -o docs/storybook
```

---

## Fehlerbehandlung: Allgemein

| Problem | Loesung |
|---------|---------|
| Container startet nicht | `docker logs CONTAINER_NAME` pruefen |
| Port belegt | `lsof -i :PORT` → Prozess beenden oder anderen Port waehlen |
| DB-Verbindung fehlschlaegt | Passwort + Host pruefen, Container laeuft? |
| MCP-Server nicht erreichbar | Firewall pruefen, Port offen? |
| Hook-Skript schlaegt fehl | `chmod +x` pruefen, `bash -x skript.sh` fuer Debug-Output |
| Rate-Limit erreicht | Model-Fallback greift automatisch |
| Agent haengt | Stop-Hook prueft, Berater kann `/stop-alle` ausfuehren |

## Rollback-Plan: Gesamt

```
Stufe 1: Service neustarten
  docker compose restart SERVICE_NAME

Stufe 2: Container neu erstellen
  docker compose down SERVICE_NAME && docker compose up -d SERVICE_NAME

Stufe 3: Daten zuruecksetzen (VORSICHT)
  docker compose down -v  ← Loescht alle Volumes!
  docker compose up -d    ← Neustart mit leeren DBs

Stufe 4: Kompletter Rollback
  git log --oneline       ← Letzten guten Commit finden
  git checkout COMMIT_ID  ← Zurueck zum guten Stand
  docker compose up -d
```
