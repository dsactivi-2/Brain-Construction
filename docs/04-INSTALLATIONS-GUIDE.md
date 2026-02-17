# INSTALLATIONS-GUIDE — Cloud Code Team 02.26

Schritt-fuer-Schritt Installation fuer Terminal und Cloud.

---

## TEIL A: Terminal-Version

### A1: Windows Installation

#### Voraussetzungen pruefen
```bash
# Git Bash oeffnen (muss installiert sein)
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

#### Schritt 5: MCP-Server starten
```bash
docker compose up -d rag-api doc-scanner
```

#### Schritt 6: Hook-Skripte installieren
```bash
bash scripts/install.sh
# Prueft ob alles da ist, kopiert Hooks + Skills + Settings
```

#### Schritt 7: MCP-Server in Claude Code registrieren
```bash
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

#### Schritt 8: Health-Check
```bash
bash scripts/health-check.sh
# Alle Services muessen "OK" zeigen
```

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

#### Schritt 5: MCP-Server starten
```bash
docker compose up -d rag-api doc-scanner
```

#### Schritt 6: Hook-Skripte installieren
```bash
bash scripts/install.sh
chmod +x ~/.claude/hooks/*.sh
```

#### Schritt 7: MCP-Server in Claude Code registrieren
```bash
claude mcp add rag-api -- python3 ~/Desktop/claude-agent-team/mcp-servers/rag-api/server.py
claude mcp add doc-scanner -- python3 ~/Desktop/claude-agent-team/mcp-servers/doc-scanner/server.py
claude mcp add github -- npx @modelcontextprotocol/server-github
claude mcp add notion -- npx @modelcontextprotocol/server-notion
```

#### Schritt 8: Health-Check
```bash
bash scripts/health-check.sh
```

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
   - Type: CPX31 (4 vCPU, 8 GB RAM) fuer Light
          oder CPX41 (8 vCPU, 16 GB RAM) fuer Standard
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

```bash
# Von deinem lokalen Rechner aus:

# MCP-Server auf Cloud zeigen lassen
claude mcp add rag-api -- curl http://DEINE_IP:8100
claude mcp add doc-scanner -- curl http://DEINE_IP:8101

# Oder: SSH Tunnel (sicherer, kein offener Port)
ssh -L 8100:localhost:8100 -L 8101:localhost:8101 claude@DEINE_IP
# Dann lokal verbinden wie bei Terminal-Version
```

### B4: Testen

```bash
# Health-Check remote
ssh claude@DEINE_IP "cd claude-agent-team && bash scripts/health-check.sh"

# Oder lokal mit SSH Tunnel:
bash scripts/health-check.sh
```

### B5: Automatischer Start nach Reboot

```bash
# Auf dem Server:
# Docker Compose startet automatisch (--restart always ist gesetzt)

# Zusaetzlich: Systemd Service fuer extra Sicherheit
sudo cat > /etc/systemd/system/claude-agent-team.service << 'EOF'
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

### B6: Monitoring einrichten

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
#   - RAG-API: http://localhost:8100/health
#   - Doc-Scanner: http://localhost:8101/health
```

### B7: SSL + Domain (optional)

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

### B8: Firewall

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

## TEIL C: Fehlerbehebung

| Problem | Loesung |
|---------|---------|
| `docker: command not found` | Docker Desktop starten (Mac/Win) oder Docker installieren (Linux) |
| `permission denied` auf Hook-Skripte | `chmod +x ~/.claude/hooks/*.sh` |
| Container startet nicht | `docker compose logs SERVICE` pruefen |
| MCP-Server nicht in Claude Code | `claude mcp list` pruefen, ggf. `claude mcp remove` + neu hinzufuegen |
| Neo4j Connection refused | Container laeuft? `docker compose ps` → `docker compose restart neo4j` |
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
