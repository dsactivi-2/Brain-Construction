# SETUP-ANLEITUNG — Cloud Code Team 02.26

Was DU (der Nutzer) einrichten und konfigurieren musst.

---

## 1. Server-Anforderungen

### Variante A: Alles auf einem Server

| Groesse | CPU | RAM | SSD | Kosten/Monat | Fuer wen |
|---------|-----|-----|-----|:------------:|----------|
| **Light** | 4 Cores | 16 GB | 80 GB | ~20-30€ | 1-2 Projekte, Einzelnutzer |
| **Standard** | 8 Cores | 32 GB | 150 GB | ~50-80€ | 3-5 Projekte, empfohlen |
| **Heavy** | 16 Cores | 64 GB | 300 GB | ~100-150€ | 10+ Projekte, grosse KBs |

### Variante B: Getrennte Server (empfohlen)

| Server | Aufgabe | RAM | Kosten/Monat |
|--------|---------|-----|:------------:|
| **Agent-Server** | Agenten + MCP + Docker | 8 GB | ~20-30€ |
| **DB-Server** | Neo4j + Qdrant + Redis + PostgreSQL | 16-20 GB | ~30-50€ |

> **Hinweis:** PostgreSQL fuer Recall Memory benoetigt minimal ~256 MB RAM zusaetzlich. Bei 16 GB RAM reicht das fuer die meisten Setups. Erst bei vielen parallelen Projekten oder grosser Konversationshistorie empfehlen sich 20 GB.

### Variante C: Managed Services (sparsamste)

| Server | Aufgabe | RAM | Kosten/Monat |
|--------|---------|-----|:------------:|
| **Agent-Server** | Agenten + MCP + Docker | 8 GB | ~20€ |
| **Datenbanken** | Managed Gratis-Tiers | — | ~0€ |
| **Gesamt** | | | **~20€** |

---

## 2. Datenbank-Setup

### 2.1 Neo4j (Graph-Datenbank)

**Wofuer:** Wissensgraph — speichert Entitaeten + Beziehungen

#### Option A: Self-Hosted (Docker) — empfohlen fuer Kontrolle

**Anbieter-Empfehlung:** Eigener Server oder Hetzner/DigitalOcean VPS

```bash
docker run -d \
  --name neo4j \
  --restart always \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/DEIN_SICHERES_PASSWORT \
  -e NEO4J_PLUGINS='["apoc", "graph-data-science"]' \
  -e NEO4J_server_memory_heap_initial__size=1g \
  -e NEO4J_server_memory_heap_max__size=2g \
  -e NEO4J_server_memory_pagecache_size=1g \
  -v neo4j-data:/data \
  -v neo4j-logs:/logs \
  neo4j:5-community
```

**Einstellungen erklaert:**
| Einstellung | Wert | Warum |
|------------|------|-------|
| `heap_initial_size` | 1g | Startgroesse Java Heap — genuegt fuer mittlere Graphen |
| `heap_max_size` | 2g | Maximum Heap — mehr nur bei >1 Mio Knoten |
| `pagecache_size` | 1g | Cache fuer Graph-Daten im RAM — schnellere Abfragen |
| `APOC` Plugin | aktiviert | Erweiterte Graph-Operationen (Import, Export, Algorithmen) |
| `Graph Data Science` | aktiviert | PageRank + Community Detection fuer HippoRAG 2 |

**Verbindung testen:**
```bash
# Browser: http://DEINE_IP:7474
# Login: neo4j / DEIN_PASSWORT
# Test-Query: RETURN 1
```

**Verbindung in Config:**
```yaml
neo4j:
  uri: bolt://DEINE_IP:7687
  user: neo4j
  password: DEIN_PASSWORT
```

#### Option B: Managed (Neo4j Aura) — empfohlen fuer einfaches Setup

**Anbieter:** https://neo4j.com/cloud/aura/
**Gratis-Tier:** Ja — 200k Knoten, 400k Beziehungen (reicht fuer Start)
**Bezahlt:** Ab ~65$/Monat fuer mehr Kapazitaet

```
1. Account erstellen: https://console.neo4j.io
2. "Create Instance" → "AuraDB Free"
3. Region: Europe (Frankfurt)
4. Passwort notieren!
5. Connection URI kopieren (neo4j+s://xxxxx.databases.neo4j.io)
```

**Verbindung in Config:**
```yaml
neo4j:
  uri: neo4j+s://DEINE_ID.databases.neo4j.io
  user: neo4j
  password: DEIN_PASSWORT
```

---

### 2.2 Qdrant (Vektor-Datenbank)

**Wofuer:** Embeddings — semantische Aehnlichkeitssuche

#### Option A: Self-Hosted (Docker) — empfohlen

```bash
docker run -d \
  --name qdrant \
  --restart always \
  -p 6333:6333 -p 6334:6334 \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  -e QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage \
  -e QDRANT__STORAGE__ON_DISK_PAYLOAD=true \
  -v qdrant-data:/qdrant/storage \
  qdrant/qdrant:latest
```

**Einstellungen erklaert:**
| Einstellung | Wert | Warum |
|------------|------|-------|
| Port 6333 | REST API | HTTP-Zugriff fuer MCP-Server |
| Port 6334 | gRPC | Schnellerer Zugriff fuer grosse Batch-Operationen |
| `on_disk_payload` | true | Payload auf Disk → weniger RAM-Verbrauch |

**Verbindung testen:**
```bash
curl http://DEINE_IP:6333/collections
# Erwartung: {"result":{"collections":[]},"status":"ok"}
```

**Verbindung in Config:**
```yaml
qdrant:
  url: http://DEINE_IP:6333
  collection: hipporag_embeddings
  vector_size: 384  # fuer all-MiniLM-L6-v2
```

#### Option B: Managed (Qdrant Cloud)

**Anbieter:** https://cloud.qdrant.io
**Gratis-Tier:** Ja — 1 GB Speicher, 1 Cluster

```
1. Account erstellen: https://cloud.qdrant.io
2. "Create Cluster" → Free Tier
3. Region: Europe
4. API Key generieren
5. Cluster URL kopieren
```

**Verbindung in Config:**
```yaml
qdrant:
  url: https://DEINE_ID.eu-central.aws.cloud.qdrant.io:6333
  api_key: DEIN_API_KEY
  collection: hipporag_embeddings
```

---

### 2.3 Redis (Cache + Queue)

**Wofuer:** Smart Cache, Task-Queue, Fragenkatalog, schnelle Zugriffe

#### Option A: Self-Hosted (Docker) — empfohlen

```bash
docker run -d \
  --name redis \
  --restart always \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server \
    --appendonly yes \
    --requirepass DEIN_SICHERES_PASSWORT \
    --maxmemory 512mb \
    --maxmemory-policy allkeys-lru
```

**Einstellungen erklaert:**
| Einstellung | Wert | Warum |
|------------|------|-------|
| `appendonly` | yes | Daten persistent auf Disk (kein Datenverlust bei Neustart) |
| `requirepass` | Passwort | Schutz vor unbefugtem Zugriff |
| `maxmemory` | 512mb | Begrenzung RAM-Verbrauch (fuer Light reicht das) |
| `maxmemory-policy` | allkeys-lru | Bei vollem RAM: Aelteste Eintraege loeschen |

**Verbindung testen:**
```bash
redis-cli -h DEINE_IP -a DEIN_PASSWORT ping
# Antwort: PONG
```

**Verbindung in Config:**
```yaml
redis:
  url: redis://:DEIN_PASSWORT@DEINE_IP:6379/0
```

#### Option B: Managed (Redis Cloud)

**Anbieter:** https://redis.com/cloud/
**Gratis-Tier:** Ja — 30 MB (reicht fuer Cache + Queue)

```
1. Account erstellen: https://app.redislabs.com
2. "New Database" → Free
3. Region: Europe
4. Endpoint + Password kopieren
```

---

### 2.4 Alle Datenbanken verbinden

Erstelle zuerst den Config-Ordner (falls noch nicht vorhanden):

```bash
mkdir -p ~/.claude/config
```

Dann die zentrale Config-Datei:

```bash
cat > ~/.claude/config/databases.yaml << 'EOF'
# Datenbank-Konfiguration — Cloud Code Team 02.26

neo4j:
  uri: bolt://localhost:7687          # oder neo4j+s://xxx.neo4j.io
  user: neo4j
  password: DEIN_NEO4J_PASSWORT

qdrant:
  url: http://localhost:6333           # oder https://xxx.cloud.qdrant.io
  api_key: null                        # nur bei Managed noetig
  collection: hipporag_embeddings
  vector_size: 384

redis:
  url: redis://:DEIN_REDIS_PASSWORT@localhost:6379/0

recall_memory:
  type: postgresql                     # oder sqlite
  host: localhost
  port: 5432
  database: recall_memory
  user: recall_user
  password: SICHERES_PASSWORT

embedding:
  model: all-MiniLM-L6-v2             # lokal, gratis, schnell
  # alternativ: text-embedding-3-small # OpenAI, besser aber kostet
EOF
```

> **Hinweis zu Embedding-Modellen:** Dieses Projekt nutzt zwei verschiedene Embedding-Pipelines fuer zwei verschiedene Collections:
> - **`all-MiniLM-L6-v2`** (384 Dimensionen) — fuer HippoRAG (Qdrant-Collection `hipporag_embeddings`)
> - **`nomic-embed-text`** (768 Dimensionen) — fuer Mem0 Self-Hosted (Qdrant-Collection `mem0_memories`)
>
> Beide Modelle laufen parallel. Die unterschiedlichen Dimensionen sind kein Problem, da jede Collection ihre eigene Konfiguration hat.

---

## 2.5 Core Memory Setup (Gehirn-Schicht 1)

**Wofuer:** Persistenter Kontext der IMMER im Agenten-Kontext geladen ist — wie ein Notizbuch das der Agent bei jedem Start liest.

Das Core Memory besteht aus 5 Bloecken mit insgesamt 20.000 Zeichen Kapazitaet.

### Datei erstellen

```bash
cat > ~/.claude/core-memory.json << 'EOF'
{
  "version": 1,
  "max_total_chars": 20000,
  "blocks": {
    "USER": {
      "max_chars": 4000,
      "content": "",
      "description": "Wer ist der Nutzer? Name, Rolle, Vorlieben, Kommunikationsstil, wichtige Kontexte"
    },
    "PROJEKT": {
      "max_chars": 4000,
      "content": "",
      "description": "Aktuelles Projekt: Name, Stack, Architektur, wichtige Entscheidungen, Ziele"
    },
    "ENTSCHEIDUNGEN": {
      "max_chars": 4000,
      "content": "",
      "description": "Getroffene Architektur- und Design-Entscheidungen mit Begruendung (WARUM so und nicht anders)"
    },
    "FEHLER-LOG": {
      "max_chars": 4000,
      "content": "",
      "description": "Bekannte Fehler, Workarounds, Was-nicht-funktioniert-hat — damit der Agent sie nicht wiederholt"
    },
    "AKTUELLE-ARBEIT": {
      "max_chars": 4000,
      "content": "",
      "description": "Was wird gerade gemacht? Offene Tasks, naechste Schritte, Blocker — wird bei jedem SessionEnd aktualisiert"
    }
  }
}
EOF
```

### Bloecke erklaert

| Block | Was kommt rein | Beispiel |
|-------|---------------|----------|
| **USER** | Nutzer-Infos, Vorlieben, Stil | "Nutzer: Max, bevorzugt TypeScript, will immer Tests" |
| **PROJEKT** | Projekt-Kontext, Stack, Ziele | "Projekt: SaaS App, Next.js + Supabase, MVP bis Q2" |
| **ENTSCHEIDUNGEN** | Architektur-Entscheidungen + Gruende | "Entscheidung: Kein ORM → weil direkte SQL-Queries schneller" |
| **FEHLER-LOG** | Fehler + Workarounds | "Bug: Redis Timeout bei >1MB Payload → Chunking nutzen" |
| **AKTUELLE-ARBEIT** | Laufende Tasks + naechste Schritte | "Aktuell: Auth-System implementieren, Blocker: OAuth Config" |

### Wie es funktioniert

- **SessionStart Hook (H-01)** laedt `core-memory.json` automatisch in den Kontext
- Jeder Agent sieht beim Start sofort alle 5 Bloecke
- Bloecke werden durch Agenten aktualisiert (z.B. bei SessionEnd)
- **Limit:** Jeder Block max 4.000 Zeichen, gesamt max 20.000 Zeichen
- **Speicherort:** `~/.claude/core-memory.json`

---

## 2.6 Auto-Recall/Capture Setup — Mem0-Prinzip (Gehirn-Schicht 2)

**Wofuer:** Automatisches Erinnern und Speichern von Fakten — wie ein Langzeitgedaechtnis das im Hintergrund arbeitet. Basiert auf dem Mem0-Prinzip.

### Option A: Mem0 Cloud (einfachster Weg)

```
1. Account erstellen: https://app.mem0.ai
2. API Key generieren: Dashboard → API Keys → "Create Key"
3. API Key kopieren
```

**Konfiguration:**
```bash
cat > ~/.claude/config/memory.json << 'EOF'
{
  "mem0": {
    "provider": "cloud",
    "api_key": "m0-DEIN_MEM0_API_KEY",
    "org_id": "DEINE_ORG_ID",
    "project_id": "DEIN_PROJEKT_ID"
  },
  "auto_recall": true,
  "auto_capture": true,
  "scopes": {
    "long_term": "user",
    "short_term": "session"
  }
}
EOF
```

### Option B: Self-Hosted mit Qdrant + Ollama (volle Kontrolle)

Du hast Qdrant bereits (Abschnitt 2.2). Zusaetzlich brauchst du Ollama fuer lokale Embeddings:

```bash
# Ollama installieren (fuer lokale Embeddings)
docker run -d \
  --name ollama \
  --restart always \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  ollama/ollama:latest

# Embedding-Modell herunterladen
docker exec ollama ollama pull nomic-embed-text
```

**Konfiguration fuer Self-Hosted:**
```bash
cat > ~/.claude/config/memory.json << 'EOF'
{
  "mem0": {
    "provider": "self-hosted",
    "vector_store": {
      "provider": "qdrant",
      "url": "http://localhost:6333",
      "collection": "mem0_memories"
    },
    "embedder": {
      "provider": "ollama",
      "url": "http://localhost:11434",
      "model": "nomic-embed-text"
    }
  },
  "auto_recall": true,
  "auto_capture": true,
  "scopes": {
    "long_term": "user",
    "short_term": "session"
  }
}
EOF
```

### Einstellungen erklaert

| Einstellung | Wert | Warum |
|------------|------|-------|
| `auto_recall` | true | **UserPromptSubmit Hook (H-04)** sucht automatisch relevante Erinnerungen und injiziert sie in den Kontext |
| `auto_capture` | true | **Stop Hook (H-11)** extrahiert automatisch neue Fakten aus der Antwort und speichert sie |
| `long_term` Scope | user | Erinnerungen gelten nutzer-weit — ueber alle Sessions und Projekte hinweg |
| `short_term` Scope | session | Temporaere Erinnerungen nur fuer die aktuelle Session |

### Agent-Tools (5 Werkzeuge)

Die folgenden Tools stehen allen Agenten automatisch zur Verfuegung:

| Tool | Funktion | Beispiel |
|------|----------|---------|
| `memory_search` | Semantische Suche in Erinnerungen | `memory_search("Redis Konfiguration")` |
| `memory_store` | Neue Erinnerung speichern | `memory_store("Redis max 512MB fuer Light Setup")` |
| `memory_list` | Alle Erinnerungen auflisten (gefiltert) | `memory_list(scope="long_term", limit=20)` |
| `memory_get` | Einzelne Erinnerung abrufen per ID | `memory_get("mem_abc123")` |
| `memory_forget` | Erinnerung loeschen (veraltet/falsch) | `memory_forget("mem_abc123")` |

### Verbindung testen

```bash
# Mem0 Cloud:
curl -H "Authorization: Token m0-DEIN_KEY" https://api.mem0.ai/v1/memories/

# Self-Hosted (Qdrant Collection pruefen):
curl http://localhost:6333/collections/mem0_memories
```

---

## 2.7 Recall Memory Setup (Gehirn-Schicht 6)

**Wofuer:** Speichert die komplette rohe Konversationshistorie — jede Nachricht, jeder Tool-Call, jede Session. Fuer spaetere Analyse und Suche.

### Option A: PostgreSQL (Docker) — empfohlen fuer Produktion

```bash
docker run -d \
  --name recall-db \
  --restart always \
  -p 5432:5432 \
  -e POSTGRES_DB=recall_memory \
  -e POSTGRES_USER=recall \
  -e POSTGRES_PASSWORD=DEIN_SICHERES_PASSWORT \
  -v recall-data:/var/lib/postgresql/data \
  postgres:16-alpine
```

**Tabellen-Struktur erstellen:**
```bash
docker exec -i recall-db psql -U recall -d recall_memory << 'SQL'
CREATE TABLE IF NOT EXISTS conversations (
  id            SERIAL PRIMARY KEY,
  session_id    VARCHAR(64) NOT NULL,
  timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  role          VARCHAR(16) NOT NULL,   -- 'user', 'assistant', 'system', 'tool'
  content       TEXT,
  tool_calls    JSONB,                  -- Tool-Aufrufe als JSON (nullable)
  metadata      JSONB                   -- Zusaetzliche Metadaten (Agent-Name, Projekt, etc.)
);

CREATE INDEX idx_conversations_session ON conversations(session_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX idx_conversations_role ON conversations(role);
CREATE INDEX idx_conversations_content_search ON conversations USING gin(to_tsvector('german', content));
SQL
```

**Verbindung in Config:**
```yaml
recall_memory:
  provider: postgresql
  host: localhost
  port: 5432
  database: recall_memory
  user: recall
  password: DEIN_SICHERES_PASSWORT
```

### Option B: SQLite (einfacher, fuer Einzelnutzer)

```bash
# Keine Installation noetig — SQLite ist ueberall verfuegbar
mkdir -p ~/.claude/data

# Datei wird automatisch erstellt bei erstem Zugriff:
# ~/.claude/data/recall-memory.sqlite
```

**Verbindung in Config:**
```yaml
recall_memory:
  provider: sqlite
  path: ~/.claude/data/recall-memory.sqlite
```

### Wie es funktioniert

- **SessionEnd Hook (H-17)** speichert automatisch die komplette Konversation
- Jede Nachricht wird einzeln mit Zeitstempel gespeichert
- Tool-Calls werden als JSON in der `tool_calls` Spalte gespeichert
- Volltextsuche ueber `content` moeglich (PostgreSQL: German Stemming)

### Tabellen-Struktur erklaert

| Spalte | Typ | Beschreibung |
|--------|-----|-------------|
| `session_id` | VARCHAR(64) | Eindeutige Session-ID — gruppiert alle Nachrichten einer Session |
| `timestamp` | TIMESTAMPTZ | Zeitpunkt der Nachricht |
| `role` | VARCHAR(16) | Wer hat gesprochen: `user`, `assistant`, `system`, `tool` |
| `content` | TEXT | Der eigentliche Nachrichteninhalt |
| `tool_calls` | JSONB | Tool-Aufrufe und deren Ergebnisse (nur bei Assistant-Nachrichten) |
| `metadata` | JSONB | Zusaetzliche Infos: Agent-Name, Projekt-ID, Tags |

### Agent-Tools (2 Werkzeuge)

| Tool | Funktion | Beispiel |
|------|----------|---------|
| `conversation_search(query)` | Volltextsuche ueber alle gespeicherten Konversationen | `conversation_search("Redis Timeout Problem")` |
| `conversation_search_date(from, to)` | Konversationen in einem Zeitraum finden | `conversation_search_date("2026-02-01", "2026-02-17")` |

### Verbindung testen

```bash
# PostgreSQL:
docker exec recall-db psql -U recall -d recall_memory -c "SELECT COUNT(*) FROM conversations;"

# SQLite:
sqlite3 ~/.claude/data/recall-memory.sqlite "SELECT COUNT(*) FROM conversations;"
```

---

## 3. Docker + Docker Compose Setup

### Installation

**Mac:**
```bash
# Docker Desktop installieren
brew install --cask docker
# Docker Desktop starten → Symbol in Menueleiste
```

**Windows:**
```bash
# Docker Desktop herunterladen: https://docker.com/products/docker-desktop
# Installieren + WSL 2 Backend aktivieren
# Neustart
```

**Linux (Ubuntu):**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Ausloggen + einloggen
```

### Pruefen
```bash
docker --version     # Docker 24+ erwartet
docker compose version  # Docker Compose 2+ erwartet
```

---

## 4. MCP-Server Einrichtung

### 4.1 RAG-API Server registrieren

```bash
# In Claude Code:
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
```

### 4.2 Doc-Scanner Server registrieren

```bash
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
```

### 4.3 GitHub Connector

```bash
# GitHub Personal Access Token erstellen:
# https://github.com/settings/tokens → "Generate new token (classic)"
# Rechte: repo, read:org, read:user

export GITHUB_TOKEN=ghp_DEIN_TOKEN

claude mcp add github -- npx @modelcontextprotocol/server-github
```

### 4.4 Notion Connector

```bash
# Notion Integration erstellen:
# https://www.notion.so/my-integrations → "New integration"
# Internal Integration → Capabilities: Read+Write

export NOTION_TOKEN=ntn_DEIN_TOKEN

claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

### 4.5 Pruefen

```bash
claude mcp list
# Erwartung:
# rag-api      running
# doc-scanner  running
# github       running
# notion       running
```

---

## 5. Claude API Einrichtung

```bash
# API Key erstellen: https://console.anthropic.com/settings/keys
# Key sicher speichern:

export ANTHROPIC_API_KEY=sk-ant-DEIN_KEY

# In .env Datei:
echo "ANTHROPIC_API_KEY=sk-ant-DEIN_KEY" >> ~/claude-agent-team/.env
```

**Wichtig:** .env ist in .gitignore → wird nie committed!

---

## 6. Slack/WhatsApp/Linear Setup

### 6.1 Slack

```
1. https://api.slack.com/apps → "Create New App"
2. "From scratch" → Name: "Claude Agent Team"
3. "Incoming Webhooks" → aktivieren
4. "Add New Webhook to Workspace"
5. Channel waehlen: #claude-agent-team
6. Webhook URL kopieren
```

### 6.2 WhatsApp Business API

```
1. https://business.facebook.com → Account erstellen
2. https://developers.facebook.com → App erstellen
3. WhatsApp → "Get Started"
4. Temporaere Nummer zum Testen nutzen
5. Token + Phone Number ID kopieren
```

**Kosten:** Erste 1000 Nachrichten/Monat gratis, danach ~0.005€/Nachricht

### 6.3 Linear

```
1. https://linear.app → Account/Workspace erstellen
2. Settings → API → "Personal API Key" erstellen
3. Team ID: Settings → Teams → ID aus URL kopieren
```

### 6.4 Alles in Config speichern

```bash
cat > ~/.claude/config/communication.json << 'EOF'
{
  "slack": {
    "webhook_url": "https://hooks.slack.com/services/XXX/XXX/XXX",
    "channel": "#claude-agent-team",
    "notify_on": ["blocker", "fertig", "fehler", "meilenstein"]
  },
  "whatsapp": {
    "enabled": false,
    "token": "DEIN_META_TOKEN",
    "phone_id": "DEINE_PHONE_ID",
    "notify_on": ["blocker", "fertig"]
  },
  "linear": {
    "enabled": false,
    "api_key": "lin_api_DEIN_KEY",
    "team_id": "TEAM_ID",
    "notify_on": ["neue_aufgabe", "fertig"]
  },
  "default_channel": "slack"
}
EOF
```

---

## 7. GitHub Repo + CI/CD

### 7.1 Repo erstellen

```bash
# Auf GitHub:
# https://github.com/new
# Name: claude-agent-team
# Private: Ja
# Erstellen

# Lokal verbinden:
cd ~/Desktop/claude-agent-team
git remote add origin https://github.com/DEIN-USER/claude-agent-team.git
git push -u origin master
```

### 7.2 CI/CD (GitHub Actions)

```bash
mkdir -p .github/workflows

cat > .github/workflows/health-check.yml << 'EOF'
name: Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Alle 6 Stunden
  workflow_dispatch:         # Manuell ausloesbar

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Health Check
        run: bash scripts/health-check.sh
        env:
          NEO4J_URL: ${{ secrets.NEO4J_URL }}
          QDRANT_URL: ${{ secrets.QDRANT_URL }}
          REDIS_URL: ${{ secrets.REDIS_URL }}
EOF
```

---

## 8. DNS + SSL (Cloud)

Nur noetig wenn Cloud-Deployment mit eigener Domain:

```bash
# Caddy als Reverse Proxy (automatisches SSL)
docker run -d \
  --name caddy \
  --restart always \
  -p 80:80 -p 443:443 \
  -v caddy-data:/data \
  -v ./Caddyfile:/etc/caddy/Caddyfile \
  caddy:2-alpine
```

```
# Caddyfile
agents.deinedomain.com {
  reverse_proxy rag-api:8100
}

docs.deinedomain.com {
  reverse_proxy doc-scanner:8101
}
```

> **Wichtig — Docker-Netzwerk:** Damit Caddy die Servicenamen `rag-api` und `doc-scanner` aufloesen kann, muessen alle Container im **selben Docker-Netzwerk** sein. Bei `docker compose` ist das automatisch der Fall. Bei einzelnen `docker run`-Befehlen musst du ein gemeinsames Netzwerk erstellen:
> ```bash
> docker network create agent-net
> # Dann jeden Container mit --network agent-net starten
> ```
> **Alternative:** Verwende `localhost:8100` und `localhost:8101` statt Servicenamen, wenn alle Container auf demselben Host laufen und Ports gemappt sind.

---

## 9. Empfehlungen: Welcher Anbieter fuer was

| Service | Empfehlung | Warum |
|---------|-----------|-------|
| **VPS/Server** | Hetzner Cloud | Bestes Preis-Leistungs-Verhaeltnis, Rechenzentren in DE |
| **Alternative VPS** | DigitalOcean | Einfaches Interface, gute Docs |
| **Neo4j** | Self-Hosted (Docker) | Volle Kontrolle, kein Limit |
| **Neo4j Managed** | Neo4j Aura Free | Gratis zum Starten |
| **Vektor-DB** | Self-Hosted Qdrant | Gratis, performant, einfach |
| **Vektor-DB Managed** | Qdrant Cloud Free | Gratis zum Starten |
| **Redis** | Self-Hosted | Gratis, minimal RAM |
| **Redis Managed** | Redis Cloud Free | Gratis, 30 MB reicht fuer Cache |
| **PostgreSQL** | Self-Hosted (Docker) | Standard fuer Recall Memory |
| **PostgreSQL Managed** | Supabase Free (500 MB) oder Neon Free (512 MB) | Gratis zum Starten |
| **Domain** | Cloudflare | Guenstig, schnell, kostenlose SSL |
| **Monitoring** | Uptime Kuma (Self-Hosted) | Gratis, einfach, Docker |

---

## 10. Gehirn-System Uebersicht (6 Schichten)

Das vollstaendige Gehirn-System besteht aus 6 Schichten:

| Schicht | Name | Setup-Abschnitt | Speicher | Zweck |
|:-------:|------|:---------:|----------|-------|
| **S1** | Core Memory | 2.5 | JSON-Datei | Persistenter Kontext — immer im Agenten-Kontext geladen |
| **S2** | Auto-Recall/Capture (Mem0) | 2.6 | Qdrant / Mem0 Cloud | Automatisches Erinnern + Speichern von Fakten |
| **S3** | HippoRAG 2 | 2.1 + 2.2 | Neo4j + Qdrant | Wissensgraph + PageRank — strukturiertes Langzeitwissen |
| **S4** | Agentic RAG | — (automatisch) | — | Intelligente Suche-Steuerung: WANN, WO, WIE suchen |
| **S5** | Agentic Learning Graphs | — (automatisch) | Neo4j | Agent baut eigenes Wissensnetz — selbst-erweiternd |
| **S6** | Recall Memory | 2.7 | PostgreSQL / SQLite | Komplette rohe Konversationshistorie |

**Schichten S4 und S5** erfordern kein eigenes Setup — sie nutzen die bestehenden Datenbanken (Neo4j, Qdrant) und werden durch die Agenten-Logik automatisch gesteuert.

---

## 11. Checkliste: Was DU einrichten musst

| # | Was | Wo | Wann |
|---|-----|-----|------|
| 1 | Server mieten oder Docker lokal | Hetzner/lokal | Vor allem anderen |
| 2 | Docker installieren | Server/lokal | Vor Datenbanken |
| 3 | `mkdir -p ~/.claude/config` erstellen | Terminal | Vor Config-Dateien |
| 4 | Neo4j Passwort waehlen | .env Datei | Vor DB-Start |
| 5 | Redis Passwort waehlen | .env Datei | Vor DB-Start |
| 6 | Core Memory erstellen | ~/.claude/core-memory.json | Vor Agent-Start |
| 7 | Mem0 einrichten (Cloud oder Self-Hosted) | ~/.claude/config/memory.json | Vor Agent-Start |
| 8 | Recall Memory DB starten | Docker (PostgreSQL) oder SQLite | Vor Agent-Start |
| 9 | Claude API Key erstellen | console.anthropic.com | Vor Agent-Start |
| 10 | GitHub Token erstellen | github.com/settings/tokens | Fuer GitHub-Connector |
| 11 | Notion Token erstellen | notion.so/my-integrations | Fuer Notion-Connector |
| 12 | Slack Webhook erstellen | api.slack.com/apps | Fuer Benachrichtigungen |
| 13 | WhatsApp Business (optional) | business.facebook.com | Fuer mobile Steuerung |
| 14 | Linear Account (optional) | linear.app | Fuer Task-Management |
| 15 | GitHub Repo erstellen | github.com/new | Fuer Code + Sync |
| 16 | DNS + Domain (optional) | cloudflare.com | Nur fuer Cloud mit Domain |

Alles andere machen die Agenten automatisch.

---

## 12. Verwandte Dokumente

| Dokument | Beschreibung |
|----------|-------------|
| [01-PROJEKTPLANUNG.md](01-PROJEKTPLANUNG.md) | Gesamtarchitektur, Agenten-Rollen, Hook-System, Gehirn-Schichten |
| [02-RUNBOOK.md](02-RUNBOOK.md) | Betriebshandbuch — Wartung, Troubleshooting, Monitoring-Prozesse |
| [04-INSTALLATIONS-GUIDE.md](04-INSTALLATIONS-GUIDE.md) | Schritt-fuer-Schritt Installation fuer Windows, Mac und Cloud |
