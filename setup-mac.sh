#!/bin/bash
# ============================================================
# Cloud Code Team 02.26 — Mac Setup Script
# Brain Construction: 6-Layer Memory System + 11 Agents
# ============================================================
# Dieses Script richtet das komplette System auf einem Mac ein:
#   1. Prerequisites pruefen (Docker, Python, Git, Claude CLI)
#   2. Repository klonen / aktualisieren
#   3. .env konfigurieren
#   4. Docker Services starten (4 DBs + 4 Brain Services)
#   5. Health-Checks
#   6. Agent-Profile deployen (merge)
#   7. Claude Code Hooks einrichten
# ============================================================

set -e

# --- Farben ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step()  { echo -e "\n${CYAN}═══════════════════════════════════════════${NC}"; echo -e "${CYAN}  $1${NC}"; echo -e "${CYAN}═══════════════════════════════════════════${NC}\n"; }

# --- Konfiguration ---
REPO_URL="https://github.com/dsactivi-2/Brain-Construction.git"
BRANCH="ddd-v3-architecture"
INSTALL_DIR="$HOME/Desktop/claude-agent-team"

# ============================================================
# SCHRITT 1: Prerequisites
# ============================================================
step "Schritt 1/7: Prerequisites pruefen"

check_cmd() {
    if command -v "$1" &>/dev/null; then
        ok "$1 gefunden: $(command -v "$1")"
        return 0
    else
        error "$1 nicht gefunden!"
        return 1
    fi
}

MISSING=0

# Docker
if check_cmd docker; then
    if docker info &>/dev/null; then
        ok "Docker laeuft"
    else
        error "Docker ist installiert aber nicht gestartet. Bitte Docker Desktop starten."
        MISSING=1
    fi
else
    error "Docker nicht installiert. Installiere: https://docs.docker.com/desktop/install/mac-install/"
    MISSING=1
fi

# Docker Compose (v2 built-in)
if docker compose version &>/dev/null; then
    ok "Docker Compose v2: $(docker compose version --short)"
else
    error "Docker Compose nicht verfuegbar"
    MISSING=1
fi

# Python 3
if check_cmd python3; then
    ok "Python: $(python3 --version)"
else
    error "Python3 nicht installiert. Installiere: brew install python3"
    MISSING=1
fi

# Git
if check_cmd git; then
    ok "Git: $(git --version)"
else
    error "Git nicht installiert. Installiere: brew install git"
    MISSING=1
fi

# Claude CLI (optional)
if check_cmd claude; then
    ok "Claude CLI gefunden"
else
    warn "Claude CLI nicht gefunden. Installiere spaeter: npm install -g @anthropic-ai/claude-code"
fi

if [ $MISSING -ne 0 ]; then
    error "Fehlende Prerequisites — bitte installieren und nochmal starten."
    exit 1
fi

# ============================================================
# SCHRITT 2: Repository klonen / aktualisieren
# ============================================================
step "Schritt 2/7: Repository"

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Repository existiert bereits in $INSTALL_DIR"
    cd "$INSTALL_DIR"

    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
        info "Wechsle von $CURRENT_BRANCH zu $BRANCH"
        git checkout "$BRANCH"
    fi

    info "Pullen der neuesten Aenderungen..."
    git pull origin "$BRANCH"
    ok "Repository aktualisiert"
else
    info "Klone Repository nach $INSTALL_DIR"
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    ok "Repository geklont"
fi

# ============================================================
# SCHRITT 3: .env konfigurieren
# ============================================================
step "Schritt 3/7: Environment (.env)"

if [ -f "$INSTALL_DIR/.env" ]; then
    ok ".env existiert bereits"
    info "Inhalt pruefen..."

    # Pruefen ob alle Keys vorhanden
    REQUIRED_KEYS=("NEO4J_PASSWORD" "REDIS_PASSWORD" "RECALL_DB_PASSWORD" "NEO4J_URI" "QDRANT_URL" "REDIS_URL" "RECALL_DB_URL")
    ALL_OK=1
    for key in "${REQUIRED_KEYS[@]}"; do
        if grep -q "^${key}=" "$INSTALL_DIR/.env"; then
            ok "  $key gesetzt"
        else
            error "  $key fehlt!"
            ALL_OK=0
        fi
    done

    if [ $ALL_OK -eq 0 ]; then
        warn "Fehlende Keys in .env — bitte manuell ergaenzen"
    fi
else
    info "Erstelle .env aus Template..."

    # Zufaelliges Passwort generieren
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | head -c 40)

    cat > "$INSTALL_DIR/.env" << ENVEOF
# === Cloud Code Team 02.26 — Environment Variables ===
# DIESE DATEI NIE COMMITTEN! (ist in .gitignore)

# --- Database Passwords ---
NEO4J_PASSWORD=${DB_PASSWORD}
REDIS_PASSWORD=${DB_PASSWORD}
RECALL_DB_PASSWORD=${DB_PASSWORD}

# --- Local URIs (Docker) ---
NEO4J_URI=bolt://localhost:7687
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://:${DB_PASSWORD}@localhost:6379/0
RECALL_DB_URL=postgresql://recall_user:${DB_PASSWORD}@localhost:5432/recall_memory

# --- Cloud URIs (Fallback) --- Bitte manuell eintragen falls vorhanden
# NEO4J_CLOUD_URI=neo4j+s://xxx.databases.neo4j.io
# QDRANT_API_KEY=dein-api-key
# REDIS_CLOUD_URL=redis://default:xxx@host:port/0
# RECALL_CLOUD_URL=postgresql://user:pass@host/db?sslmode=require

# --- API Keys ---
CLAUDE_API_KEY=DEIN_API_KEY
ENVEOF

    ok ".env erstellt mit generiertem Passwort"
    warn "Bitte CLAUDE_API_KEY und Cloud-URIs manuell in .env eintragen!"
fi

# ============================================================
# SCHRITT 4: Docker Services starten
# ============================================================
step "Schritt 4/7: Docker Services starten"

cd "$INSTALL_DIR"

# Phase 1: Datenbanken zuerst
info "Phase 1: Datenbanken starten..."
docker compose up -d neo4j qdrant redis recall-db

info "Warte 15 Sekunden auf DB-Initialisierung..."
sleep 15

# Phase 2: Brain Services
info "Phase 2: Brain Services bauen + starten..."
info "  (Das kann beim ersten Mal 10-20 Minuten dauern — grosse ML-Modelle)"
docker compose up -d --build rag-api doc-scanner hipporag learning-graphs

ok "Alle 8 Services gestartet"

# ============================================================
# SCHRITT 5: Health-Checks
# ============================================================
step "Schritt 5/7: Health-Checks"

info "Warte 20 Sekunden auf Service-Initialisierung..."
sleep 20

HEALTH_OK=1

# Datenbanken
check_health() {
    local name="$1"
    local check="$2"
    if eval "$check" &>/dev/null; then
        ok "$name"
    else
        error "$name — nicht erreichbar"
        HEALTH_OK=0
    fi
}

info "--- Datenbanken ---"
check_health "Neo4j (7474)"     "curl -sf http://localhost:7474"
check_health "Qdrant (6333)"    "curl -sf http://localhost:6333/collections"
check_health "PostgreSQL (5432)" "docker exec recall-db pg_isready -U recall_user -d recall_memory"

REDIS_PW=$(grep REDIS_PASSWORD "$INSTALL_DIR/.env" | cut -d= -f2)
check_health "Redis (6379)" "docker exec redis redis-cli -a '$REDIS_PW' ping"

info "--- Brain Services ---"
check_health "rag-api (8100)"     "curl -sf http://localhost:8100/health"
check_health "doc-scanner (8101)" "curl -sf http://localhost:8101/health"
check_health "hipporag (8102)"    "curl -sf http://localhost:8102/health"

# learning-graphs hat keinen HTTP-Endpunkt
if docker compose ps learning-graphs --format "{{.Status}}" 2>/dev/null | grep -q "Up"; then
    ok "learning-graphs (internal)"
else
    error "learning-graphs — nicht gestartet"
    HEALTH_OK=0
fi

if [ $HEALTH_OK -eq 0 ]; then
    warn "Einige Services sind nicht healthy. Logs pruefen mit: docker compose logs <service>"
    warn "Weiter mit Setup trotzdem..."
fi

# ============================================================
# SCHRITT 6: Agent-Profile deployen
# ============================================================
step "Schritt 6/7: Agent-Profile mergen + deployen"

cd "$INSTALL_DIR"

# Pruefen ob merge_profiles.py existiert (in config/agent-profiles oder separat)
MERGE_SCRIPT=""
if [ -f "config/agent-profiles/merge_profiles.py" ]; then
    MERGE_SCRIPT="config/agent-profiles/merge_profiles.py"
elif [ -f "merge_profiles.py" ]; then
    MERGE_SCRIPT="merge_profiles.py"
fi

if [ -n "$MERGE_SCRIPT" ]; then
    info "Merge-Script gefunden: $MERGE_SCRIPT"
    python3 "$MERGE_SCRIPT"
    ok "Profile gemerged"
else
    # Pruefen ob Profile bereits gemerged sind
    MERGED_COUNT=$(find agents -name "profile.json" 2>/dev/null | wc -l)
    if [ "$MERGED_COUNT" -ge 11 ]; then
        ok "$MERGED_COUNT gemerged Profile bereits vorhanden"
    else
        warn "Kein Merge-Script gefunden und nur $MERGED_COUNT Profile vorhanden"
        warn "Bitte merge_profiles.py manuell ausfuehren"
    fi
fi

# Verifizieren
info "Agent-Verzeichnisse:"
for dir in agents/*/; do
    name=$(basename "$dir")
    claude_md="—"
    profile="—"
    [ -f "$dir/CLAUDE.md" ] && claude_md="$(du -h "$dir/CLAUDE.md" | cut -f1)"
    [ -f "$dir/profile.json" ] && profile="$(du -h "$dir/profile.json" | cut -f1)"
    printf "  %-20s CLAUDE.md=%-6s profile.json=%s\n" "$name" "$claude_md" "$profile"
done

# ============================================================
# SCHRITT 7: Claude Code Konfiguration (Projekt-Level)
# ============================================================
step "Schritt 7/7: Claude Code Konfiguration"

# --- 7a: PROJEKT-Settings (.claude/settings.json im Repo) ---
# Das ist die WICHTIGE Datei — MCP Server + Hooks + Permissions
PROJECT_CLAUDE_DIR="$INSTALL_DIR/.claude"
mkdir -p "$PROJECT_CLAUDE_DIR"

info "Schreibe Projekt-Settings: $PROJECT_CLAUDE_DIR/settings.json"
info "  (MCP brain-tools Server + 12 Hook-Definitionen)"

cat > "$PROJECT_CLAUDE_DIR/settings.json" << SETTINGSEOF
{
  "mcpServers": {
    "brain-tools": {
      "command": "python3",
      "args": ["${INSTALL_DIR}/mcp-servers/brain-tools/server.py"],
      "cwd": "${INSTALL_DIR}",
      "env": {
        "BRAIN_DIR": "${INSTALL_DIR}/brain",
        "CONFIG_DIR": "${INSTALL_DIR}/config",
        "HF_HUB_DISABLE_SYMLINKS_WARNING": "1",
        "TOKENIZERS_PARALLELISM": "false"
      }
    }
  },
  "hooks": {
    "SessionStart": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/session-start-startup.sh", "timeout": 15000},
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/core-memory-inject.sh", "timeout": 10000}
    ],
    "UserPromptSubmit": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/user-prompt-submit.sh", "timeout": 5000},
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/auto-recall.sh", "timeout": 8000}
    ],
    "PreToolUse": [
      {"matcher": "Write|Edit", "type": "agent", "prompt": "Pruefe ob diese Code-Aenderung sicher ist. Keine Secrets, keine Injection, keine gefaehrlichen Patterns.", "timeout": 30000},
      {"matcher": "Bash", "type": "agent", "prompt": "Pruefe ob dieser Bash-Befehl sicher ist. Blockiere: rm -rf /, DROP TABLE, --force auf main/master, Secrets in Befehlen.", "timeout": 30000}
    ],
    "PostToolUse": [
      {"matcher": "Write|Edit", "type": "command", "command": "bash ${INSTALL_DIR}/hooks/post-tool-write.sh", "timeout": 30000},
      {"matcher": "Bash", "type": "command", "command": "bash ${INSTALL_DIR}/hooks/post-tool-bash.sh", "timeout": 10000}
    ],
    "PostToolUseFailure": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/post-tool-failure.sh", "timeout": 10000}
    ],
    "PreCompact": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/pre-compact.sh", "timeout": 15000}
    ],
    "Stop": [
      {"type": "agent", "prompt": "Pruefe ob alle zugewiesenen Tasks erledigt sind. Kein Task darf uebersprungen oder als erledigt markiert sein ohne tatsaechlich erledigt zu sein.", "timeout": 60000},
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/auto-capture.sh", "timeout": 10000}
    ],
    "SubagentStart": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/subagent-start.sh", "timeout": 10000}
    ],
    "SubagentStop": [
      {"type": "agent", "prompt": "Pruefe die Qualitaet der Subagent-Ausgabe. Ist die Aufgabe vollstaendig und korrekt erledigt?", "timeout": 60000}
    ],
    "Notification": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/notification.sh", "timeout": 10000}
    ],
    "TaskCompleted": [
      {"type": "agent", "prompt": "Verifiziere dass dieser Task WIRKLICH erledigt ist. Pruefe: Code geschrieben? Tests bestanden? Review OK? Nichts uebersprungen?", "timeout": 60000}
    ],
    "SessionEnd": [
      {"type": "command", "command": "bash ${INSTALL_DIR}/hooks/session-end-recall.sh", "timeout": 20000}
    ]
  }
}
SETTINGSEOF

ok "Projekt-Settings geschrieben (MCP + 12 Hooks)"

# --- 7b: Hook-Script Stubs erstellen (falls nicht vorhanden) ---
HOOKS_DIR="$INSTALL_DIR/hooks"
mkdir -p "$HOOKS_DIR"

HOOK_SCRIPTS=(
    "session-start-startup.sh"
    "core-memory-inject.sh"
    "user-prompt-submit.sh"
    "auto-recall.sh"
    "post-tool-write.sh"
    "post-tool-bash.sh"
    "post-tool-failure.sh"
    "pre-compact.sh"
    "auto-capture.sh"
    "subagent-start.sh"
    "notification.sh"
    "session-end-recall.sh"
)

CREATED_HOOKS=0
for hook in "${HOOK_SCRIPTS[@]}"; do
    if [ ! -f "$HOOKS_DIR/$hook" ]; then
        cat > "$HOOKS_DIR/$hook" << HOOKEOF
#!/bin/bash
# Hook: $hook
# TODO: Implementierung folgt
# Siehe docs/01-PROJEKTPLANUNG.md fuer Details
exit 0
HOOKEOF
        chmod +x "$HOOKS_DIR/$hook"
        CREATED_HOOKS=$((CREATED_HOOKS + 1))
    fi
done

if [ $CREATED_HOOKS -gt 0 ]; then
    ok "$CREATED_HOOKS Hook-Stubs erstellt in hooks/"
else
    ok "Alle Hook-Scripts existieren bereits"
fi

# --- 7c: User-Level Permissions (optional, fuer Komfort) ---
USER_CLAUDE_DIR="$HOME/.claude"
mkdir -p "$USER_CLAUDE_DIR"

if [ ! -f "$USER_CLAUDE_DIR/settings.json" ]; then
    info "Erstelle User-Level Permissions..."
    cat > "$USER_CLAUDE_DIR/settings.json" << 'USERSETTINGSEOF'
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch",
      "mcp__brain-tools__*"
    ],
    "deny": []
  }
}
USERSETTINGSEOF
    ok "User-Settings erstellt (Brain-Tools auto-allowed)"
else
    ok "User-Settings existieren bereits (nicht ueberschrieben)"
    info "Tipp: mcp__brain-tools__* zu permissions.allow hinzufuegen falls fehlend"
fi

# ============================================================
# FERTIG
# ============================================================
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SETUP KOMPLETT!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Installationsort:  $INSTALL_DIR"
echo "  Branch:            $BRANCH"
echo ""
echo "  Docker Services:   docker compose ps"
echo "  Logs ansehen:      docker compose logs -f <service>"
echo "  Services stoppen:  docker compose down"
echo "  Services starten:  docker compose up -d"
echo ""
echo "  Brain-System URLs:"
echo "    Neo4j Browser:   http://localhost:7474"
echo "    Qdrant Dashboard: http://localhost:6333/dashboard"
echo "    RAG API:         http://localhost:8100/health"
echo "    Doc Scanner:     http://localhost:8101/health"
echo "    HippoRAG:        http://localhost:8102/health"
echo ""
echo "  Agenten starten (Beispiel):"
echo "    cd $INSTALL_DIR"
echo "    claude --agent agents/berater/CLAUDE.md"
echo ""

if ! command -v claude &>/dev/null; then
    echo -e "${YELLOW}  HINWEIS: Claude CLI noch installieren:${NC}"
    echo "    npm install -g @anthropic-ai/claude-code"
    echo ""
fi

echo -e "${YELLOW}  NAECHSTE SCHRITTE:${NC}"
echo "    1. CLAUDE_API_KEY in .env eintragen"
echo "    2. Cloud-URIs in .env eintragen (optional, fuer Fallback)"
echo "    3. Hooks implementieren (17 Hooks fuer Brain-System)"
echo "    4. Tests ausfuehren"
echo ""
