# INSTALLATIONS-GUIDE — Cloud Code Team 02.26

Schritt-fuer-Schritt Installation fuer Terminal und Cloud.

---

## TEIL A: Terminal-Version

### A1: Windows Installation

#### Voraussetzungen

> **Wichtig:** Unter Windows wird **Git Bash** oder **WSL2** als Shell vorausgesetzt. Alle Befehle in dieser Anleitung verwenden Unix-Syntax.

#### Voraussetzungen installieren
```bash
# Git Bash oder WSL2 oeffnen

# Claude Code CLI installieren (falls noch nicht vorhanden)
npm install -g @anthropic-ai/claude-code
```

#### Voraussetzungen pruefen
```bash
git --version          # Git 2.x erwartet
node --version         # Node.js 18+ erwartet
npm --version          # npm 9+ erwartet
python3 --version      # Python 3.10+ erwartet
pip3 --version         # pip vorhanden
docker --version       # Docker 24+ erwartet
claude --version       # Claude Code CLI installiert
```

#### Schritt 1: Repo klonen
```bash
cd ~/Desktop
git clone https://github.com/DEIN-USER/claude-agent-team.git
cd claude-agent-team
```

#### Schritt 2: Python-Abhaengigkeiten
```bash
python3 -m venv venv
source venv/Scripts/activate    # Windows Git Bash
pip install -r requirements.txt
```

#### Schritt 3: Datenbanken starten
```bash
# Docker Desktop muss laufen!
docker compose up -d neo4j qdrant redis
# Warten bis alle Container laufen:
docker compose ps
```

#### Schritt 4: .env Datei erstellen
```bash
cp .env.example .env
# Bearbeiten mit Editor:
notepad .env
# Passwoerter + API-Keys eintragen
```

#### Schritt 5: Hook-Skripte installieren
```bash
bash scripts/install.sh
# Prueft ob alles da ist, kopiert Hooks + Skills + Settings
```

#### Schritt 6: MCP-Server in Claude Code registrieren

> **Hinweis:** Fuer lokale Entwicklung werden MCP-Server direkt ueber `claude mcp add` gestartet. Docker-basierte MCP-Server (`docker compose up -d rag-api doc-scanner`) sind nur fuer die Cloud-Variante (Teil B) vorgesehen.

```bash
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

#### Schritt 7: Health-Check
```bash
bash scripts/health-check.sh
# Alle Services muessen "OK" zeigen
```

#### Schritt 8: Gehirn-System einrichten

```bash
# 1. Core Memory (Schicht 1) — immer im Kontext
mkdir -p ~/.claude
cat > ~/.claude/core-memory.json << 'EOF'
{
  "blocks": {
    "user": { "value": "", "limit": 4000 },
    "projekt": { "value": "", "limit": 4000 },
    "entscheidungen": { "value": "", "limit": 4000 },
    "fehler_log": { "value": "", "limit": 4000 },
    "aktuelle_arbeit": { "value": "", "limit": 4000 }
  }
}
EOF

# 2. Auto-Recall/Capture (Schicht 2) — Mem0
mkdir -p ~/.claude/config
cat > ~/.claude/config/memory.json << 'EOF'
{
  "provider": "mem0",
  "api_key": "DEIN_MEM0_API_KEY",
  "org_id": "DEINE_ORG_ID",
  "project_id": "DEIN_PROJECT_ID"
}
EOF

# 3. Recall Memory (Schicht 6) — Chat-Historie
# Option A: SQLite (einfach)
# Wird automatisch in ~/.claude/data/recall.db erstellt
mkdir -p ~/.claude/data

# Option B: PostgreSQL (siehe 03-SETUP-ANLEITUNG.md Abschnitt 2.7)
```

> **Details:** Siehe [03-SETUP-ANLEITUNG.md](03-SETUP-ANLEITUNG.md) Abschnitte 2.5 (Core Memory), 2.6 (Mem0) und 2.7 (Recall Memory) fuer ausfuehrliche Erklaerungen und Konfigurationsoptionen.

#### Schritt 9: Testen
```bash
claude
# In Claude Code:
/profil-laden berater
# Berater sollte antworten
```

#### Schritt 10: Fertig
```
Windows Terminal-Installation abgeschlossen.
Alle Agenten sind ueber Claude Code CLI verfuegbar.
```

---

### A2: Mac Installation

#### Voraussetzungen installieren
```bash
# Homebrew (wenn nicht vorhanden)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Tools installieren
brew install git node python3
brew install --cask docker

# Claude Code CLI installieren
npm install -g @anthropic-ai/claude-code
```

#### Voraussetzungen pruefen
```bash
git --version          # Git 2.x
node --version         # Node.js 18+
python3 --version      # Python 3.10+
docker --version       # Docker 24+
claude --version       # Claude Code CLI
```

#### Schritt 1: Repo klonen
```bash
cd ~/Desktop
git clone https://github.com/DEIN-USER/claude-agent-team.git
cd claude-agent-team
```

#### Schritt 2: Python-Abhaengigkeiten
```bash
python3 -m venv venv
source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

#### Schritt 3: Datenbanken starten
```bash
# Docker Desktop starten (aus Applications)
docker compose up -d neo4j qdrant redis
docker compose ps   # Alle "Up"?
```

#### Schritt 4: .env Datei erstellen
```bash
cp .env.example .env
nano .env    # oder: open -e .env
# Passwoerter + API-Keys eintragen
```

#### Schritt 5: Hook-Skripte installieren
```bash
bash scripts/install.sh
chmod +x ~/.claude/hooks/*.sh
```

#### Schritt 6: MCP-Server in Claude Code registrieren

> **Hinweis:** Fuer lokale Entwicklung werden MCP-Server direkt ueber `claude mcp add` gestartet. Docker-basierte MCP-Server sind nur fuer die Cloud-Variante (Teil B) vorgesehen.

```bash
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

#### Schritt 7: Health-Check
```bash
bash scripts/health-check.sh
```

#### Schritt 8: Gehirn-System einrichten

```bash
# 1. Core Memory (Schicht 1) — immer im Kontext
mkdir -p ~/.claude
cat > ~/.claude/core-memory.json << 'EOF'
{
  "blocks": {
    "user": { "value": "", "limit": 4000 },
    "projekt": { "value": "", "limit": 4000 },
    "entscheidungen": { "value": "", "limit": 4000 },
    "fehler_log": { "value": "", "limit": 4000 },
    "aktuelle_arbeit": { "value": "", "limit": 4000 }
  }
}
EOF

# 2. Auto-Recall/Capture (Schicht 2) — Mem0
mkdir -p ~/.claude/config
cat > ~/.claude/config/memory.json << 'EOF'
{
  "provider": "mem0",
  "api_key": "DEIN_MEM0_API_KEY",
  "org_id": "DEINE_ORG_ID",
  "project_id": "DEIN_PROJECT_ID"
}
EOF

# 3. Recall Memory (Schicht 6) — Chat-Historie
# Option A: SQLite (einfach)
# Wird automatisch in ~/.claude/data/recall.db erstellt
mkdir -p ~/.claude/data

# Option B: PostgreSQL (siehe 03-SETUP-ANLEITUNG.md Abschnitt 2.7)
```

> **Details:** Siehe [03-SETUP-ANLEITUNG.md](03-SETUP-ANLEITUNG.md) Abschnitte 2.5 (Core Memory), 2.6 (Mem0) und 2.7 (Recall Memory) fuer ausfuehrliche Erklaerungen und Konfigurationsoptionen.

#### Schritt 9: Testen
```bash
claude
/profil-laden berater
```

#### Schritt 10: Fertig
```
Mac Terminal-Installation abgeschlossen.
```

---

## TEIL B: Cloud-Version

### B1: Server aufsetzen

#### Empfehlung: Hetzner Cloud

```
1. https://console.hetzner.cloud → Account erstellen
2. "Add Server"
   - Location: Falkenstein (DE) oder Nuernberg (DE)
   - Image: Ubuntu 24.04
   - Type: CPX41 (8 vCPU, 16 GB RAM) fuer Light-Variante
          oder CX51 (8 vCPU, 32 GB RAM) fuer Standard-Variante
   - SSH Key hinzufuegen
   - Networking: Public IPv4
3. "Create & Buy"
4. IP-Adresse notieren
```

#### Server vorbereiten

```bash
# Mit Server verbinden
ssh root@DEINE_IP

# System updaten
apt update && apt upgrade -y

# Docker installieren
curl -fsSL https://get.docker.com | sh

# Docker Compose installieren (falls nicht dabei)
apt install docker-compose-plugin -y

# Nicht-Root User erstellen
adduser claude
usermod -aG docker claude
su - claude
```

### B2: Docker deployen

```bash
# Als User "claude" auf dem Server:

# Repo klonen
git clone https://github.com/DEIN-USER/claude-agent-team.git
cd claude-agent-team

# .env erstellen
cp .env.example .env
nano .env
# Passwoerter + API-Keys eintragen

# Alles starten
docker compose up -d

# Status pruefen
docker compose ps
# Alle Container muessen "Up" zeigen

# Logs pruefen
docker compose logs -f --tail=50
# Strg+C zum Beenden
```

### B3: Services verbinden

Die MCP-Server laufen via Docker auf dem Cloud-Server. Lokal verbindest du dich per **SSH-Tunnel**, damit keine Ports oeffentlich offen sein muessen.

```bash
# Von deinem lokalen Rechner aus:

# 1. SSH-Tunnel oeffnen (alle relevanten Ports)
ssh -L 8100:localhost:8100 \
    -L 8101:localhost:8101 \
    -L 7687:localhost:7687 \
    -L 6333:localhost:6333 \
    -L 6379:localhost:6379 \
    -L 5432:localhost:5432 \
    claude@DEINE_IP

# 2. In einem neuen Terminal: MCP-Server lokal registrieren
#    (die Tunnel leiten die Verbindung zum Server weiter)
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

> **Erklaerung der Ports:**
> | Port | Service | Zweck |
> |------|---------|-------|
> | 8100 | RAG-API | MCP-Server fuer Wissensbasis |
> | 8101 | Doc-Scanner | MCP-Server fuer Dokumentenanalyse |
> | 7687 | Neo4j (Bolt) | Graph-Datenbank |
> | 6333 | Qdrant | Vektor-Datenbank |
> | 6379 | Redis | Cache + Queue |
> | 5432 | PostgreSQL | Recall Memory |

### B4: Testen

```bash
# Health-Check remote
ssh claude@DEINE_IP "cd claude-agent-team && bash scripts/health-check.sh"

# Oder lokal mit SSH Tunnel:
bash scripts/health-check.sh
```

### B5: Gehirn-System einrichten (lokal)

Auch bei der Cloud-Variante wird das Gehirn-System **lokal** konfiguriert:

```bash
# 1. Core Memory (Schicht 1) — immer im Kontext
mkdir -p ~/.claude
cat > ~/.claude/core-memory.json << 'EOF'
{
  "blocks": {
    "user": { "value": "", "limit": 4000 },
    "projekt": { "value": "", "limit": 4000 },
    "entscheidungen": { "value": "", "limit": 4000 },
    "fehler_log": { "value": "", "limit": 4000 },
    "aktuelle_arbeit": { "value": "", "limit": 4000 }
  }
}
EOF

# 2. Auto-Recall/Capture (Schicht 2) — Mem0
mkdir -p ~/.claude/config
cat > ~/.claude/config/memory.json << 'EOF'
{
  "provider": "mem0",
  "api_key": "DEIN_MEM0_API_KEY",
  "org_id": "DEINE_ORG_ID",
  "project_id": "DEIN_PROJECT_ID"
}
EOF

# 3. Recall Memory (Schicht 6) — Chat-Historie
# PostgreSQL laeuft auf dem Cloud-Server (via SSH-Tunnel erreichbar auf localhost:5432)
# Konfiguration in ~/.claude/config/databases.yaml (siehe 03-SETUP-ANLEITUNG.md Abschnitt 2.4)
```

> **Details:** Siehe [03-SETUP-ANLEITUNG.md](03-SETUP-ANLEITUNG.md) Abschnitte 2.5, 2.6 und 2.7 fuer ausfuehrliche Erklaerungen.

### B6: Automatischer Start nach Reboot (auf dem Server)

```bash
# Auf dem Server:
# Docker Compose startet automatisch (--restart always ist gesetzt)

# Zusaetzlich: Systemd Service fuer extra Sicherheit
sudo tee /etc/systemd/system/claude-agent-team.service << 'EOF'
[Unit]
Description=Claude Agent Team
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/claude/claude-agent-team
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable claude-agent-team
sudo systemctl start claude-agent-team
```

### B7: Monitoring einrichten

```bash
# Uptime Kuma (Self-Hosted Monitoring)
docker run -d \
  --name uptime-kuma \
  --restart always \
  -p 3001:3001 \
  -v uptime-kuma-data:/app/data \
  louislam/uptime-kuma:1

# Browser: http://DEINE_IP:3001
# Monitors hinzufuegen:
#   - Neo4j: http://localhost:7474
#   - Qdrant: http://localhost:6333
#   - Redis: TCP localhost:6379
#   - PostgreSQL: TCP localhost:5432
#   - RAG-API: http://localhost:8100/health
#   - Doc-Scanner: http://localhost:8101/health
#   - Ollama (optional): http://localhost:11434/api/tags
```

### B8: SSL + Domain (optional)

```bash
# Caddy als Reverse Proxy mit automatischem SSL:

cat > Caddyfile << 'EOF'
agents.deinedomain.com {
  reverse_proxy rag-api:8100
}
docs.deinedomain.com {
  reverse_proxy doc-scanner:8101
}
monitor.deinedomain.com {
  reverse_proxy uptime-kuma:3001
}
EOF

# Caddy zum Docker Compose hinzufuegen:
# (Bereits in docker-compose.yml vorbereitet)
docker compose up -d caddy
```

### B9: Firewall

```bash
# Nur noetige Ports oeffnen
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp     # HTTP (Caddy)
sudo ufw allow 443/tcp    # HTTPS (Caddy)
# NICHT oeffnen: 7474, 6333, 6379, 8100, 8101 (nur intern!)
sudo ufw enable
```

---

## Hinweis zu referenzierten Dateien

Die folgenden Dateien werden in dieser Anleitung referenziert, aber erst im Rahmen der Projekteinrichtung erstellt:

| Datei | Beschreibung | Erstellt in |
|-------|-------------|-------------|
| `docker-compose.yml` | Docker Compose Konfiguration fuer alle Services | 02-RUNBOOK.md, Abschnitt Deployment |
| `requirements.txt` | Python-Abhaengigkeiten fuer MCP-Server | 02-RUNBOOK.md, Abschnitt Projektstruktur |
| `.env.example` | Vorlage fuer Umgebungsvariablen (Passwoerter, API-Keys) | 02-RUNBOOK.md, Abschnitt Konfiguration |
| `scripts/install.sh` | Installations-Skript (kopiert Hooks, Skills, Settings) | 02-RUNBOOK.md, Abschnitt Skripte |
| `scripts/health-check.sh` | Prueft ob alle Services erreichbar sind | 02-RUNBOOK.md, Abschnitt Monitoring |

> **Wenn eine dieser Dateien noch nicht existiert:** Erstelle zuerst das Grundgeruest gemaess [02-RUNBOOK.md](02-RUNBOOK.md), bevor du die Installationsschritte ausfuehrst.

---

## TEIL C: Fehlerbehebung

| Problem | Loesung |
|---------|---------|
| `docker: command not found` | Docker Desktop starten (Mac/Win) oder Docker installieren (Linux) |
| `permission denied` auf Hook-Skripte | `chmod +x ~/.claude/hooks/*.sh` |
| Container startet nicht | `docker compose logs SERVICE` pruefen |
| MCP-Server nicht in Claude Code | `claude mcp list` pruefen, ggf. `claude mcp remove` + neu hinzufuegen |
| Neo4j Connection refused | Container laeuft? `docker compose ps` → `docker compose restart neo4j` |
| PostgreSQL Connection refused | Container laeuft? `docker compose ps` → `docker exec recall-db pg_isready` pruefen. Port 5432 belegt? Anderen Port nutzen: `-p 5433:5432` |
| PostgreSQL Authentifizierung fehlgeschlagen | Passwort in `.env` und `databases.yaml` abgleichen. Ggf. Volume loeschen und neu erstellen: `docker volume rm recall-data` |
| Mem0 API-Fehler / 401 Unauthorized | API-Key in `~/.claude/config/memory.json` pruefen. Bei Cloud: Key auf https://app.mem0.ai erneuern |
| Ollama-Modell nicht gefunden | `docker exec ollama ollama list` pruefen. Modell nachladen: `docker exec ollama ollama pull nomic-embed-text` |
| Core Memory nicht gefunden | Datei `~/.claude/core-memory.json` existiert? `ls -la ~/.claude/core-memory.json` pruefen. Ggf. Schritt 8/9 (Gehirn-Setup) wiederholen |
| `~/.claude/config/` Ordner fehlt | `mkdir -p ~/.claude/config` ausfuehren. Dieser Schritt wird leicht vergessen |
| Rate-Limit erreicht | Model-Fallback greift automatisch, oder kurz warten |
| Health-Check schlaegt fehl | Einzelne Services pruefen: `docker compose logs SERVICE_NAME` |
| Git push rejected | `git pull --rebase` zuerst ausfuehren |
| Python venv nicht gefunden | `source venv/bin/activate` (Mac) oder `source venv/Scripts/activate` (Win) |
| Port belegt | `lsof -i :PORT` (Mac/Linux) oder `netstat -ano | findstr PORT` (Windows) |

---

## TEIL D: Schnellstart-Zusammenfassung

### Terminal (5 Minuten wenn Docker laeuft)
```bash
git clone REPO_URL && cd claude-agent-team
cp .env.example .env && nano .env
docker compose up -d
bash scripts/install.sh
bash scripts/health-check.sh
claude
```

### Cloud (15 Minuten)
```bash
ssh root@IP
curl -fsSL https://get.docker.com | sh
adduser claude && usermod -aG docker claude
su - claude
git clone REPO_URL && cd claude-agent-team
cp .env.example .env && nano .env
docker compose up -d
bash scripts/health-check.sh
```

---

## Verwandte Dokumente

| Dokument | Beschreibung |
|----------|-------------|
| [01-PROJEKTPLANUNG.md](01-PROJEKTPLANUNG.md) | Gesamtarchitektur, Agenten-Rollen, Hook-System, Gehirn-Schichten |
| [02-RUNBOOK.md](02-RUNBOOK.md) | Betriebshandbuch — Wartung, Troubleshooting, Monitoring-Prozesse |
| [03-SETUP-ANLEITUNG.md](03-SETUP-ANLEITUNG.md) | Detailliertes Setup aller Datenbanken, MCP-Server, Gehirn-Schichten |
