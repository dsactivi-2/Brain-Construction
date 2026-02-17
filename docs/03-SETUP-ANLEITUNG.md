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
| **DB-Server** | Neo4j + Qdrant + Redis | 16 GB | ~30-40€ |

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

Erstelle eine zentrale Config-Datei:

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

embedding:
  model: all-MiniLM-L6-v2             # lokal, gratis, schnell
  # alternativ: text-embedding-3-small # OpenAI, besser aber kostet
EOF
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
claude mcp add rag-api -- python3 ~/claude-agent-team/mcp-servers/rag-api/server.py
```

### 4.2 Doc-Scanner Server registrieren

```bash
claude mcp add doc-scanner -- python3 ~/claude-agent-team/mcp-servers/doc-scanner/server.py
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
| **Domain** | Cloudflare | Guenstig, schnell, kostenlose SSL |
| **Monitoring** | Uptime Kuma (Self-Hosted) | Gratis, einfach, Docker |

---

## 10. Checkliste: Was DU einrichten musst

| # | Was | Wo | Wann |
|---|-----|-----|------|
| 1 | Server mieten oder Docker lokal | Hetzner/lokal | Vor allem anderen |
| 2 | Docker installieren | Server/lokal | Vor Datenbanken |
| 3 | Neo4j Passwort waehlen | .env Datei | Vor DB-Start |
| 4 | Redis Passwort waehlen | .env Datei | Vor DB-Start |
| 5 | Claude API Key erstellen | console.anthropic.com | Vor Agent-Start |
| 6 | GitHub Token erstellen | github.com/settings/tokens | Fuer GitHub-Connector |
| 7 | Notion Token erstellen | notion.so/my-integrations | Fuer Notion-Connector |
| 8 | Slack Webhook erstellen | api.slack.com/apps | Fuer Benachrichtigungen |
| 9 | WhatsApp Business (optional) | business.facebook.com | Fuer mobile Steuerung |
| 10 | Linear Account (optional) | linear.app | Fuer Task-Management |
| 11 | GitHub Repo erstellen | github.com/new | Fuer Code + Sync |
| 12 | DNS + Domain (optional) | cloudflare.com | Nur fuer Cloud mit Domain |

Alles andere machen die Agenten automatisch.
