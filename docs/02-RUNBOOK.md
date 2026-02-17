# RUNBOOK — Cloud Code Team 02.26

Bau- und Deploy-Anleitung fuer die Agenten die dieses System erstellen und betreiben.

---

## Uebersicht: Bau-Reihenfolge

```
Schritt 1: Infrastruktur (Datenbanken + Server)
    │
    ▼
Schritt 2: Gehirn-System (HippoRAG 2 + Agentic RAG + Learning Graphs
         + Core Memory + Auto-Recall/Capture + Recall Memory)
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

## Voraussetzungen

Bevor mit der Installation begonnen wird, muessen folgende Werkzeuge installiert sein:

| Werkzeug | Version | Hinweis |
|----------|---------|---------|
| Docker Desktop | aktuell | Fuer alle Container-Dienste |
| Git Bash ODER WSL2 | — | Alle Befehle sind fuer Unix-Shell geschrieben. Auf Windows muss Git Bash oder WSL2 verwendet werden |
| Python | 3.10+ | Fuer Gehirn-System, MCP-Server, Skripte |
| Node.js | 18+ | Fuer MCP-Connectoren und Dokumentation |
| npm | (mit Node.js) | Paketmanager fuer Node.js |
| Git | aktuell | Versionskontrolle |

**Hinweis zu Pfaden auf Windows:**
- `~` steht fuer das Home-Verzeichnis
- In Git Bash entspricht `~` dem Pfad `/c/Users/NUTZERNAME`
- In WSL2 entspricht `~` dem Pfad `/home/NUTZERNAME`
- Alle Befehle in diesem Runbook nutzen Unix-Syntax und muessen in Git Bash oder WSL2 ausgefuehrt werden

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
curl http://localhost:6333/collections
```

**Pruefung:** http://localhost:6333/collections erreichbar (API-Endpunkt, zuverlaessiger als /dashboard)
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

### 1.4 PostgreSQL (Recall Memory)

**Zweck:** Recall Memory — Speichert komplette Konversationshistorie (Schicht 6)

> **Hinweis:** Fuer lokales Entwickeln kann statt PostgreSQL auch SQLite verwendet werden (siehe Schritt 2.6). PostgreSQL wird fuer den produktiven Docker-Compose Betrieb empfohlen (Schritt 10).

**Befehle:**
```bash
# Docker Container starten
docker run -d \
  --name recall-db \
  --restart always \
  -p 5432:5432 \
  -e POSTGRES_DB=recall_memory \
  -e POSTGRES_USER=recall_user \
  -e POSTGRES_PASSWORD=SICHERES_PASSWORT \
  -v recall-data:/var/lib/postgresql/data \
  postgres:16-alpine

# Verbindung testen
docker exec recall-db pg_isready -U recall_user -d recall_memory
```

**Pruefung:** `pg_isready` gibt "accepting connections" zurueck
**Fehlerbehandlung:** Port belegt → `docker ps` pruefen, alten Container stoppen
**Rollback:** `docker stop recall-db && docker rm recall-db`

### 1.5 Abhaengigkeiten zwischen Datenbanken

```
Neo4j       → Unabhaengig, kann zuerst starten
Qdrant      → Unabhaengig, kann parallel starten
Redis       → Unabhaengig, kann parallel starten
PostgreSQL  → Unabhaengig, kann parallel starten (fuer Recall Memory)

Alle 4 muessen laufen BEVOR Schritt 2 beginnt.
```

> **Siehe auch:** 04-INSTALLATIONS-GUIDE.md fuer die Schritt-fuer-Schritt Installation der Datenbanken.

### 1.6 Shared/Cloud vs. Agent-Only/Lokal Architektur

Bei 30-40 parallelen Agenten: Shared-Daten in Cloud-DBs, Agent-Only lokal.

```
CLOUD (Shared — alle 30-40 Agenten):
├── Redis          → Core Memory Shared + Task-Queue + Event-Bus + Warm-Up Cache
├── Qdrant         → Auto-Recall Vektoren (S2) + HippoRAG Embeddings (S3)
├── Neo4j          → Wissensgraph (S3) + Learning Graphs (S5)
└── PostgreSQL     → Recall Memory (S6), Connection Pool: 40

LOKAL (Agent-Only — isoliert pro Agent):
├── agents/agent-XXX-core.json → [AKTUELLE-ARBEIT], [FEHLER-LOG]
├── Agentic RAG Logik          → Router + Evaluator (S4)
├── Daily Notes                → Markdown auf Disk
└── Session State              → Nur waehrend Session
```

**Core Memory Split:**
- Shared-Bloecke ([USER], [PROJEKT], [ENTSCHEIDUNGEN]) → Redis
  Nur Admin/Berater schreibt, alle Agenten lesen
- Agent-Only-Bloecke ([AKTUELLE-ARBEIT], [FEHLER-LOG]) → lokale JSON
  Nur dieser Agent liest + schreibt, keine Locking-Probleme

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

### 2.4 Core Memory (Immer-im-Kontext-Schicht)

**Zweck:** Feste Speicherbloecke die bei JEDEM API-Call im System-Prompt mitgeschickt werden. Der Agent hat dadurch permanenten Zugriff auf Nutzer-Infos, Projektkontext, getroffene Entscheidungen, bekannte Fehler und die aktuelle Arbeit — ohne suchen zu muessen.

**Konzept:**
```
┌──────────────────────────────────────────────┐
│              CORE MEMORY (≤20.000 Zeichen)   │
│                                              │
│  ┌─────────────┐  ┌──────────────────────┐   │
│  │ USER (4k)   │  │ PROJEKT (4k)         │   │
│  │ Name, Prefs │  │ Stack, Ziele, Regeln │   │
│  └─────────────┘  └──────────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────┐    │
│  │ ENTSCHEID. (4k) │  │ FEHLER-LOG (4k) │    │
│  │ Warum X, Y, Z   │  │ Bekannte Bugs   │    │
│  └─────────────────┘  └─────────────────┘    │
│  ┌────────────────────────┐                  │
│  │ AKTUELLE-ARBEIT (4k)   │                  │
│  │ Was gerade passiert     │                  │
│  └────────────────────────┘                  │
└──────────────────────────────────────────────┘
```

**Befehle:**
```bash
cd ~/claude-agent-team/brain
mkdir -p core_memory

# Core-Memory Konfiguration erstellen
cat > core_memory/core-memory.json << 'EOF'
{
  "max_size_chars": 20000,
  "blocks": {
    "user": {
      "label": "USER",
      "limit": 4000,
      "value": ""
    },
    "projekt": {
      "label": "PROJEKT",
      "limit": 4000,
      "value": ""
    },
    "entscheidungen": {
      "label": "ENTSCHEIDUNGEN",
      "limit": 4000,
      "value": ""
    },
    "fehler_log": {
      "label": "FEHLER-LOG",
      "limit": 4000,
      "value": ""
    },
    "aktuelle_arbeit": {
      "label": "AKTUELLE-ARBEIT",
      "limit": 4000,
      "value": ""
    }
  }
}
EOF
```

**Core-Memory Tools (2 Befehle fuer den Agenten):**

| Tool | Beschreibung |
|------|-------------|
| `core_memory_read(block)` | Liest einen einzelnen Block oder alle Bloecke (wenn `block` leer ist) mit aktuellem Fuellstand |
| `core_memory_update(block, operation, inhalt, alt)` | Aendert einen Block. Operationen: `append` (Text anfuegen), `replace` (Text ersetzen, benoetigt `alt` fuer den zu ersetzenden Text), `remove` (Text entfernen) |

**Injection in System-Prompt:**
```bash
# SessionStart Hook laedt Core Memory und injiziert es
cat > ~/.claude/hooks/core-memory-inject.sh << 'COREEOF'
#!/bin/bash
# Core Memory in den System-Prompt injizieren
CORE_MEM_FILE="$HOME/claude-agent-team/brain/core_memory/core-memory.json"

if [ -f "$CORE_MEM_FILE" ]; then
  echo "=== CORE MEMORY START ==="
  python3 -c "
import json
with open('$CORE_MEM_FILE') as f:
    data = json.load(f)
for key, block in data['blocks'].items():
    if block['value']:
        print(f\"<{block['label']}>\\n{block['value']}\\n</{block['label']}>\")
"
  echo "=== CORE MEMORY END ==="
fi
COREEOF
chmod +x ~/.claude/hooks/core-memory-inject.sh
```

**Pruefung:**
```bash
# Core-Memory JSON validieren
python3 -c "import json; json.load(open('core_memory/core-memory.json')); print('Core-Memory JSON: OK')"

# Testblock schreiben und lesen
python3 -c "
import json
f = 'core_memory/core-memory.json'
data = json.load(open(f))
data['blocks']['user']['value'] = 'Test-Nutzer'
json.dump(data, open(f, 'w'), indent=2)
print('Schreiben OK — USER Block:', data['blocks']['user']['value'])
"
```

**Fehlerbehandlung:** JSON-Syntax-Fehler → `python3 -m json.tool core_memory/core-memory.json`
**Rollback:** `rm -rf ~/claude-agent-team/brain/core_memory`

### 2.5 Auto-Recall / Auto-Capture (Mem0-Style Schicht)

**Zweck:** Automatisches Speichern und Abrufen von Erinnerungen im Hintergrund. Bei jedem Nutzer-Prompt werden relevante Erinnerungen gesucht und injiziert (Recall). Nach jeder Antwort werden neue Fakten/Entscheidungen extrahiert und gespeichert (Capture). Funktioniert wie menschliches Langzeit- und Kurzzeitgedaechtnis.

**Konzept:**
```
Nutzer-Prompt ──► [UserPromptSubmit Hook]
                        │
                        ▼
               ┌─────────────────┐
               │  AUTO-RECALL    │
               │  Suche relevante│
               │  Erinnerungen   │
               └────────┬────────┘
                        │
                        ▼
               Erinnerungen werden
               in Kontext injiziert
                        │
                        ▼
               Claude generiert Antwort
                        │
                        ▼
               ┌─────────────────┐
               │  AUTO-CAPTURE   │
               │  Extrahiere neue│
               │  Fakten/Wissen  │
               └────────┬────────┘
                        │
                        ▼
            ┌───────────┴───────────┐
            ▼                       ▼
   Kurzzeit-Speicher        Langzeit-Speicher
   (Session-Scope)          (User/Projekt-Scope)
```

**Memory-Scopes:**

| Scope | Lebensdauer | Beispiel |
|-------|-------------|---------|
| `session` | Nur aktuelle Session | "Nutzer arbeitet gerade an Feature X" |
| `user` | Permanent pro Nutzer | "Nutzer bevorzugt TypeScript" |
| `projekt` | Permanent pro Projekt | "Projekt nutzt Next.js + Prisma" |
| `global` | Permanent fuer alle | "Firmenregel: Keine var, immer const/let" |

**Befehle — Auto-Recall Hook (UserPromptSubmit):**

> **Hinweis:** Claude Code uebergibt Hook-Daten via stdin als JSON, NICHT als Umgebungsvariablen. Das Skript muss stdin lesen und mit `jq` oder `python3` parsen.

```bash
cat > ~/.claude/hooks/auto-recall.sh << 'RECALLEOF'
#!/bin/bash
# Auto-Recall: Relevante Erinnerungen vor Antwort suchen und injizieren
# Hook-Daten kommen via stdin als JSON
INPUT=$(cat -)
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys, os
sys.path.insert(0, "$BRAIN_DIR")

from auto_memory.recall import search_memories

# Hook-Daten aus stdin parsen
hook_data = json.loads('''$INPUT''')
prompt = hook_data.get("prompt", "")

if not prompt:
    sys.exit(0)

# Semantische Suche ueber alle Memory-Scopes
results = search_memories(
    query=prompt,
    scopes=["session", "user", "projekt", "global"],
    top_k=10,
    min_score=0.6
)

if results:
    print("=== ERINNERUNGEN (AUTO-RECALL) ===")
    for mem in results:
        print(f"[{mem['scope']}] {mem['text']} (Score: {mem['score']:.2f})")
    print("=== ENDE ERINNERUNGEN ===")
PYEOF
RECALLEOF
chmod +x ~/.claude/hooks/auto-recall.sh
```

**Befehle — Auto-Capture Hook (Stop):**

> **Hinweis:** Claude Code uebergibt Hook-Daten via stdin als JSON, NICHT als Umgebungsvariablen. Das Skript muss stdin lesen und mit `jq` oder `python3` parsen.

```bash
cat > ~/.claude/hooks/auto-capture.sh << 'CAPTUREEOF'
#!/bin/bash
# Auto-Capture: Neue Fakten/Entscheidungen nach Antwort extrahieren und speichern
# Hook-Daten kommen via stdin als JSON
INPUT=$(cat -)
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys
sys.path.insert(0, "$BRAIN_DIR")

from auto_memory.capture import extract_and_store

# Hook-Daten aus stdin parsen
hook_data = json.loads('''$INPUT''')
conversation = hook_data.get("conversation", "")

if not conversation:
    sys.exit(0)

# Extrahiere neue Erinnerungen aus der Konversation
new_memories = extract_and_store(
    conversation=conversation,
    extract_types=["fakt", "entscheidung", "praeferenz", "fehler", "todo"],
    dedup=True  # Keine Duplikate speichern
)

if new_memories:
    for mem in new_memories:
        print(f"[GESPEICHERT] [{mem['scope']}] {mem['type']}: {mem['text']}")
PYEOF
CAPTUREEOF
chmod +x ~/.claude/hooks/auto-capture.sh
```

**settings.json Erweiterung — Hooks fuer Auto-Recall/Capture:**

> **Hinweis:** Hook-Daten werden von Claude Code automatisch via stdin als JSON uebergeben. Die Befehle brauchen KEINE Argumente wie `$PROMPT` oder `$CONVERSATION` — diese Umgebungsvariablen existieren nicht.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "bash ~/.claude/hooks/auto-recall.sh",
        "timeout": 8000
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "bash ~/.claude/hooks/auto-capture.sh",
        "timeout": 10000
      }
    ]
  }
}
```

> **Hinweis:** Diese Hooks werden zu den bestehenden `UserPromptSubmit`- und `Stop`-Hooks in Schritt 4.2 hinzugefuegt (Array erweitern, nicht ersetzen).

**5 Memory-Tools (fuer manuellen Zugriff durch den Agenten):**

| Tool | Beschreibung |
|------|-------------|
| `memory_store(text, scope, type)` | Erinnerung manuell speichern |
| `memory_search(query, scope, top_k)` | Erinnerungen semantisch suchen |
| `memory_forget(memory_id)` | Einzelne Erinnerung loeschen |
| `memory_get(memory_id)` | Einzelne Erinnerung abrufen |
| `memory_list(scope, type, limit)` | Erinnerungen auflisten/filtern |

**Auto-Memory Modul erstellen:**
```bash
cd ~/claude-agent-team/brain
mkdir -p auto_memory

cat > auto_memory/__init__.py << 'EOF'
# Auto-Memory — Mem0-Style Recall + Capture
# Automatisches Speichern und Abrufen von Erinnerungen
# Scopes: session, user, projekt, global
# Storage: Qdrant (Vektoren) + Redis (Session-Cache) + Neo4j (Beziehungen)
EOF

cat > auto_memory/recall.py << 'EOF'
# Recall-Modul: Sucht relevante Erinnerungen basierend auf semantischer Aehnlichkeit
# Wird durch UserPromptSubmit Hook automatisch aufgerufen
# Nutzt Qdrant fuer Vektor-Suche + Redis fuer Session-Cache
def search_memories(query: str, scopes: list, top_k: int = 10, min_score: float = 0.6):
    pass  # Implementierung in Bau-Phase
EOF

cat > auto_memory/capture.py << 'EOF'
# Capture-Modul: Extrahiert Fakten/Entscheidungen aus Konversation
# Wird durch Stop Hook automatisch aufgerufen
# Nutzt LLM fuer Extraktion + Qdrant/Neo4j fuer Speicherung
def extract_and_store(conversation: str, extract_types: list, dedup: bool = True):
    pass  # Implementierung in Bau-Phase
EOF
```

**Pruefung:**
```bash
# Module importierbar?
python3 -c "from auto_memory.recall import search_memories; print('Recall-Modul: OK')"
python3 -c "from auto_memory.capture import extract_and_store; print('Capture-Modul: OK')"

# Hook-Skripte ausfuehrbar?
ls -la ~/.claude/hooks/auto-recall.sh ~/.claude/hooks/auto-capture.sh
```

**Fehlerbehandlung:** Import-Fehler → `sys.path` pruefen, `__init__.py` vorhanden?
**Rollback:** `rm -rf ~/claude-agent-team/brain/auto_memory && rm ~/.claude/hooks/auto-recall.sh ~/.claude/hooks/auto-capture.sh`

### 2.6 Recall Memory (Konversations-Archiv-Schicht)

**Zweck:** Speichert JEDE abgeschlossene Konversation als Rohdaten. Ermoeglicht spaeteres Durchsuchen aller bisherigen Gespraeche nach Inhalt oder Datum. Das ist das "episodische Gedaechtnis" — der Agent kann sich an fruehere Gespraeche erinnern.

**Konzept:**
```
Session endet ──► [SessionEnd Hook]
                        │
                        ▼
               ┌─────────────────────┐
               │  RECALL MEMORY      │
               │  Speichere komplette│
               │  Konversation als   │
               │  durchsuchbares     │
               │  Dokument           │
               └─────────┬───────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     Qdrant (Vektoren)      PostgreSQL/SQLite
     fuer semantische       (Metadaten:
      Suche                  Datum, Agent,
                             Session-ID)
```

**Datenbank-Tabelle (SQLite):**
```bash
cd ~/claude-agent-team/brain
mkdir -p recall_memory

cat > recall_memory/init_db.py << 'EOF'
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")

def init():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            agent_name TEXT DEFAULT 'unknown',
            started_at DATETIME NOT NULL,
            ended_at DATETIME NOT NULL,
            message_count INTEGER DEFAULT 0,
            summary TEXT,
            raw_conversation TEXT NOT NULL,
            embedding_ids TEXT,
            tags TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_date
        ON conversations(started_at)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_agent
        ON conversations(agent_name)
    """)
    conn.commit()
    conn.close()
    print(f"Recall-Memory DB initialisiert: {DB_PATH}")

if __name__ == "__main__":
    init()
EOF

python3 recall_memory/init_db.py
```

**SessionEnd Hook — Konversation speichern:**

> **Hinweis:** Claude Code uebergibt Hook-Daten via stdin als JSON, NICHT als Umgebungsvariablen. `CLAUDE_CONVERSATION`, `CLAUDE_SESSION_ID` und `CLAUDE_AGENT_NAME` existieren nicht als Umgebungsvariablen. Das Skript muss stdin lesen und die JSON-Daten parsen.

```bash
cat > ~/.claude/hooks/session-end-recall.sh << 'RECALLENDEOF'
#!/bin/bash
# Recall Memory: Komplette Konversation bei Session-Ende speichern
# Hook-Daten kommen via stdin als JSON
INPUT=$(cat -)
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sqlite3, uuid, os
from datetime import datetime

DB_PATH = os.path.join("$BRAIN_DIR", "recall_memory", "conversations.db")

# Hook-Daten aus stdin parsen
hook_data = json.loads('''$INPUT''')
CONV_DATA = hook_data.get("conversation", "")
SESSION_ID = hook_data.get("session_id", "unknown")
AGENT_NAME = hook_data.get("agent_name", "unknown")

if CONV_DATA:
    conn = sqlite3.connect(DB_PATH)
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO conversations (id, session_id, agent_name, started_at, ended_at, raw_conversation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (conv_id, SESSION_ID, AGENT_NAME, now, now, CONV_DATA))

    conn.commit()
    conn.close()
    print(f"[RECALL] Konversation gespeichert: {conv_id}")
else:
    print("[RECALL] Keine Konversationsdaten — uebersprungen")
PYEOF
RECALLENDEOF
chmod +x ~/.claude/hooks/session-end-recall.sh
```

> **Hinweis:** Dieser Hook wird zum bestehenden `SessionEnd`-Hook-Array in Schritt 4.2 hinzugefuegt.

**settings.json Erweiterung — SessionEnd Hook:**
```json
{
  "hooks": {
    "SessionEnd": [
      {
        "type": "command",
        "command": "bash ~/.claude/hooks/session-end-recall.sh",
        "timeout": 20000
      }
    ]
  }
}
```

**Such-Tools (2 Werkzeuge fuer den Agenten):**

| Tool | Beschreibung | Beispiel |
|------|-------------|---------|
| `conversation_search(query, limit)` | Semantische Suche ueber alle bisherigen Konversationen | `conversation_search("Docker Deployment Fehler")` |
| `conversation_search_date(start, end, agent)` | Konversationen nach Datum und optional Agent filtern | `conversation_search_date("2026-02-01", "2026-02-17", agent="coder")` |

**Such-Modul erstellen:**
```bash
cat > recall_memory/search.py << 'EOF'
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "conversations.db")

def conversation_search(query: str, limit: int = 10):
    """Durchsucht alle gespeicherten Konversationen nach Inhalt.
    Nutzt SQLite FTS oder Qdrant-Vektoren fuer semantische Suche."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT id, session_id, agent_name, started_at, summary,
               substr(raw_conversation, 1, 500) as preview
        FROM conversations
        WHERE raw_conversation LIKE ?
        ORDER BY started_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))
    results = cursor.fetchall()
    conn.close()
    return results

def conversation_search_date(start: str, end: str, agent: str = None, limit: int = 20):
    """Sucht Konversationen nach Datum (und optional Agent)."""
    conn = sqlite3.connect(DB_PATH)
    if agent:
        cursor = conn.execute("""
            SELECT id, session_id, agent_name, started_at, summary,
                   substr(raw_conversation, 1, 500) as preview
            FROM conversations
            WHERE started_at BETWEEN ? AND ? AND agent_name = ?
            ORDER BY started_at DESC
            LIMIT ?
        """, (start, end, agent, limit))
    else:
        cursor = conn.execute("""
            SELECT id, session_id, agent_name, started_at, summary,
                   substr(raw_conversation, 1, 500) as preview
            FROM conversations
            WHERE started_at BETWEEN ? AND ?
            ORDER BY started_at DESC
            LIMIT ?
        """, (start, end, limit))
    results = cursor.fetchall()
    conn.close()
    return results
EOF

cat > recall_memory/__init__.py << 'EOF'
# Recall Memory — Konversations-Archiv
# Speichert jede abgeschlossene Konversation als durchsuchbares Dokument
# Storage: SQLite (Metadaten + Volltext) + Qdrant (Vektor-Embeddings)
# Tools: conversation_search, conversation_search_date
EOF
```

**Pruefung:**
```bash
# DB existiert und Tabelle angelegt?
python3 -c "
import sqlite3
conn = sqlite3.connect('recall_memory/conversations.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tabellen:', [t[0] for t in tables])
conn.close()
"

# Such-Modul importierbar?
python3 -c "from recall_memory.search import conversation_search, conversation_search_date; print('Recall-Search: OK')"

# Hook ausfuehrbar?
ls -la ~/.claude/hooks/session-end-recall.sh
```

**Fehlerbehandlung:** DB-Fehler → `rm recall_memory/conversations.db && python3 recall_memory/init_db.py`
**Rollback:** `rm -rf ~/claude-agent-team/brain/recall_memory && rm ~/.claude/hooks/session-end-recall.sh`

### 2.7 Zusammenspiel der 3 neuen Gehirn-Schichten (S1, S2, S6)

> **Hinweis zur Nummerierung:** Die Schichten sind Teil der globalen Schichten-Architektur. Hier werden die 3 NEUEN Schichten beschrieben: Schicht 1 (S1), Schicht 2 (S2) und Schicht 6 (S6). Die Schichten 3-5 sind in der Gesamt-Architektur definiert (siehe 01-PROJEKTPLANUNG.md).

```
┌─────────────────────────────────────────────────────────────┐
│                    GEHIRN-SYSTEM v2                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 1 (S1): CORE MEMORY (Schritt 2.4)            │  │
│  │ → Immer im Kontext, sofort verfuegbar                │  │
│  │ → 5 Bloecke, max 20k Zeichen                        │  │
│  │ → Injection via SessionStart Hook                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                         ▲ liest                             │
│                         │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 2 (S2): AUTO-RECALL/CAPTURE (Schritt 2.5)    │  │
│  │ → Automatisch bei jedem Prompt (Recall)              │  │
│  │ → Automatisch nach jeder Antwort (Capture)           │  │
│  │ → Kurzzeit + Langzeit Scopes                         │  │
│  │ → Kann Core Memory aktualisieren                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                         ▲ durchsucht                        │
│                         │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 6 (S6): RECALL MEMORY (Schritt 2.6)          │  │
│  │ → Komplette Konversationen archiviert                │  │
│  │ → Durchsuchbar nach Inhalt + Datum                   │  │
│  │ → SessionEnd Hook speichert automatisch              │  │
│  └───────────────────────────────────────────────────────┘  │
│                         ▲ baut auf                          │
│                         │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Basis: HippoRAG 2 + Agentic RAG + Learning Graphs   │  │
│  │ (Schritte 2.1 — 2.3)                                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Reihenfolge beim Setup:**
1. Zuerst HippoRAG 2 + Agentic RAG + Learning Graphs (Schritte 2.1–2.3)
2. Dann Core Memory (Schritt 2.4) — braucht nur Dateisystem
3. Dann Auto-Recall/Capture (Schritt 2.5) — braucht Qdrant + Redis + Neo4j
4. Dann Recall Memory (Schritt 2.6) — braucht SQLite + Qdrant

**Der gesamte Schritt 2 (alle 6 Gehirn-Schichten) muss abgeschlossen sein BEVOR Schritt 3 (MCP-Server) beginnt.**

> **Siehe auch:** 01-PROJEKTPLANUNG.md Abschnitt Gehirn-System fuer die vollstaendige Schichten-Architektur. 03-SETUP-ANLEITUNG.md fuer detaillierte Konfigurationseinstellungen.

### 2.8 HippoRAG-Service (Schicht 3 — Implementierung)

**Zweck:** PersonalizedPageRank-Algorithmus fuer den Wissensgraphen

**Befehle:**
```bash
cd ~/claude-agent-team/brain
mkdir -p hipporag-service && cd hipporag-service

# Struktur erstellen
cat > entity_extractor.py << 'PYEOF'
"""LLM extrahiert Entitaeten + Beziehungen aus Text → Neo4j"""
# Eingehender Text → LLM-Prompt → (Subjekt, Praedikat, Objekt) Tripel
# Tripel → Neo4j MERGE Statements
PYEOF

cat > ppr.py << 'PYEOF'
"""PersonalizedPageRank ueber Neo4j Wissensgraph"""
# Query → Seed-Knoten identifizieren → PPR laufen lassen
# Top-K Knoten + zugehoerige Vektoren aus Qdrant zurueckgeben
PYEOF

cat > retriever.py << 'PYEOF'
"""Query → PPR → Qdrant → Top-K relevante Ergebnisse"""
# Kombination: Graph-Traversal (Neo4j) + Vektor-Aehnlichkeit (Qdrant)
# Ergebnis: Ranked Liste von Wissens-Chunks
PYEOF

cat > server.py << 'PYEOF'
"""MCP/REST Endpoint fuer HippoRAG-Service"""
# POST /retrieve → Query → retriever.py → Top-K Ergebnisse
# POST /ingest   → Text → entity_extractor.py → Neo4j + Qdrant
PYEOF
```

**Pruefung:** `curl http://localhost:8102/health` gibt `{"status": "ok"}`
**Fehlerbehandlung:** Neo4j/Qdrant nicht erreichbar → Degraded Mode Warnung
**Rollback:** `rm -rf ~/claude-agent-team/brain/hipporag-service`

### 2.9 Agentic RAG (Schicht 4 — Implementierung)

**Zweck:** Intelligente Suchsteuerung — entscheidet WO und WIE gesucht wird

**Befehle:**
```bash
cd ~/claude-agent-team/brain
mkdir -p agentic-rag && cd agentic-rag

cat > router.py << 'PYEOF'
"""Entscheidet welche Schicht(en) abgefragt werden"""
# Einfache Faktenfrage → S1 (Core Memory) zuerst
# Semantische Suche → S2 (Auto-Recall, Qdrant)
# Komplexe Zusammenhaenge → S3 (HippoRAG, Neo4j + Qdrant)
# Historische Frage → S6 (Recall Memory, PostgreSQL)
# Unbekannt → Multi-Source: S2 + S3 + S6 parallel
PYEOF

cat > evaluator.py << 'PYEOF'
"""Bewertet ob Suchergebnis gut genug ist"""
# Relevanz-Score < Schwellenwert → Retry mit anderer Quelle
# Konfidenz-Check: Sind die Top-3 Ergebnisse konsistent?
# Bei Widerspruch → alle Quellen abfragen + LLM entscheidet
PYEOF

cat > feedback.py << 'PYEOF'
"""Feedback-Loop: Falsches Wissen korrigieren"""
# Agent markiert Ergebnis als "veraltet" oder "falsch"
# Priority-Score des Eintrags sinkt
# Decay wird beschleunigt → Eintrag wird frueher geprunt
PYEOF

cat > orchestrator.py << 'PYEOF'
"""Multi-Step Orchestrierung: Suche → Bewerte → Verfeinere"""
# Schritt 1: Router waehlt Quellen
# Schritt 2: Parallele Abfrage
# Schritt 3: Evaluator bewertet
# Schritt 4: Falls noetig → Retry mit verfeinerter Query
# Max 3 Retry-Runden, dann bestes Ergebnis zurueckgeben
PYEOF
```

**Pruefung:** `python3 -c "from agentic_rag.router import route_query; print('Agentic RAG: OK')"`
**Fehlerbehandlung:** Bei Ausfall einzelner Schichten → Degraded Mode (verfuegbare Quellen nutzen)
**Rollback:** `rm -rf ~/claude-agent-team/brain/agentic-rag`

### 2.10 Learning Graphs (Schicht 5 — Implementierung)

**Zweck:** Selbst-erweiterendes Wissensnetz — waechst mit jeder Session

**Befehle:**
```bash
cd ~/claude-agent-team/brain
mkdir -p learning-graphs && cd learning-graphs

cat > pattern_detector.py << 'PYEOF'
"""Erkennt wiederkehrende Muster aus Agenten-Interaktionen"""
# Analysiert: Welche Tools werden oft zusammen genutzt?
# Welche Fehler treten wiederholt auf?
# Welche Entscheidungen wurden revidiert?
PYEOF

cat > graph_updater.py << 'PYEOF'
"""SessionEnd-Hook → neue Knoten/Kanten in Neo4j"""
# Jede Session erzeugt: Genutzte Tools, Entscheidungen, Ergebnisse
# Neue Kanten: "Tool A wurde nach Tool B genutzt" (Workflow-Pattern)
# Neue Knoten: Gelernte Fakten, Fehler-Muster
PYEOF

cat > consolidator.py << 'PYEOF'
"""Woechentlicher Cronjob: Verdichte + Prune den Graph"""
# Konsolidierung: S6 Rohdaten → Fakten extrahieren → Neo4j
# Decay: Score sinkt fuer Eintraege >90 Tage ohne Abruf
# Prune: Eintraege unter Schwellenwert → Archiv/Loeschung
# Snapshot VOR Konsolidierung (Rollback moeglich)
PYEOF
```

**Pruefung:** `python3 -c "from learning_graphs.graph_updater import update_graph; print('Learning Graphs: OK')"`
**Fehlerbehandlung:** Neo4j nicht erreichbar → Aenderungen lokal puffern, spaeter synchronisieren
**Rollback:** `rm -rf ~/claude-agent-team/brain/learning-graphs`

### 2.11 Gehirn-Mechanismen

#### Konsolidierung (Cronjob — wie Schlaf)
```bash
# Cronjob einrichten (woechentlich Sonntag 03:00)
crontab -e
# Eintrag:
0 3 * * 0 cd ~/claude-agent-team/brain && python3 learning-graphs/consolidator.py --mode=consolidate 2>&1 >> logs/consolidation.log

# Was passiert:
# 1. Graph-Snapshot erstellen (neo4j-admin dump)
# 2. S6 (PostgreSQL) → Letzte 7 Tage Konversationen lesen
# 3. LLM extrahiert Fakten + Beziehungen
# 4. Neue Knoten/Kanten → Neo4j (S3/S5)
# 5. Log schreiben
```

#### Decay/Pruning (Cronjob — aktives Vergessen)
```bash
# Cronjob einrichten (taeglich 04:00)
0 4 * * * cd ~/claude-agent-team/brain && python3 learning-graphs/consolidator.py --mode=decay 2>&1 >> logs/decay.log

# Was passiert:
# 1. Alle Eintraege pruefen: Letzter Abruf > 90 Tage?
# 2. Ja → Priority-Score um 1 senken
# 3. Score < 2 → In Archiv verschieben
# 4. Archiv > 180 Tage → Endgueltig loeschen
```

#### Priority-Scoring
```bash
# Wird automatisch bei jedem memory_store gesetzt:
# Blocker beantwortet → Score 9
# Bug gefixt → Score 8
# Architektur-Entscheidung → Score 9
# Feature implementiert → Score 6
# Routine-Commit → Score 2
# Standard-Log → Score 1

# Auto-Recall (S2) sortiert nach Score: Hoehere zuerst
# Context-Budget: Max 3.000 Tokens → Top-K nach Score
```

### 2.12 Betriebsmechanismen (30-40 Agenten)

#### Cross-Agent Event-Bus
```bash
# Redis Pub/Sub Kanaele einrichten
redis-cli -a SICHERES_PASSWORT << 'REDIS'
# Kanaele werden automatisch bei erstem PUBLISH erstellt:
# bugs       → Agent meldet Bug-Fund
# decisions  → Architektur-Entscheidung getroffen
# progress   → Fortschritts-Update
# blocker    → Agent ist blockiert, braucht Hilfe
REDIS

# Agenten subscriben auf relevante Kanaele via Hook
```

#### Warm-Up Bundle
```bash
# Redis Key fuer Schnellstart-Paket pro Projekt
redis-cli -a SICHERES_PASSWORT << 'REDIS'
# Struktur: warmup:<projekt-id>
# Inhalt: Core Memory Shared + Top-20 Erinnerungen + Task-Queue
# Wird bei jeder Aenderung an Shared-Daten aktualisiert
# Agent-Start: 1x HGET warmup:<projekt-id> → <100ms einsatzbereit
REDIS
```

#### Degraded Mode
```bash
# Health-Check erweitert: Prueft jede DB + setzt Degraded-Flags
# Neo4j down  → Flag: HIPPORAG_DISABLED=true, S3/S5 deaktiviert
# Qdrant down → Flag: VECTOR_SEARCH_DISABLED=true, S2 nur Redis
# Redis down  → Flag: CACHE_DISABLED=true, direkte DB-Queries
# PG down     → Flag: RECALL_FALLBACK=sqlite, SQLite WAL lokal

# Agent bekommt im Kontext:
# "WARNUNG: Eingeschraenkter Modus — [Neo4j] nicht erreichbar.
#  Schicht 3 (HippoRAG) und Schicht 5 (Learning Graphs) deaktiviert."
```

#### Conflict Resolution
```bash
# Hierarchie fuer Shared-Writes:
# Berater (10) > Architekt (9) > Coder (7) > Tester (6) >
# Reviewer (5) > Designer (4) > Analyst (3) > Doc-Scanner (2) >
# DevOps (2) > Dokumentierer (1)
#
# Bei Konflikt: Hoechste Hierarchie gewinnt
# Bei gleicher Ebene: Juengster Eintrag gewinnt
# Unloesbar: Automatische Blocker-Frage an Admin/Supervisor
```

#### Versioning / Graph-Rollback
```bash
# Snapshot vor jeder Konsolidierung
neo4j-admin dump --database=neo4j --to-path=backups/graph-$(date +%Y%m%d).dump

# Max 7 Snapshots behalten (aeltere rotieren)
ls -t backups/graph-*.dump | tail -n +8 | xargs rm -f

# Rollback bei vergiftetem Graph:
neo4j-admin load --database=neo4j --from-path=backups/graph-DATUM.dump --overwrite-destination
```

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
# Tools (kanonische Namen — siehe 01-PROJEKTPLANUNG.md FN-051 bis FN-059):
#   - memory_store: Erinnerung speichern
#   - memory_search: Erinnerungen durchsuchen (semantisch + Graph)
#   - memory_list: Erinnerungen auflisten/filtern
#   - memory_get: Einzelne Erinnerung abrufen
#   - memory_forget: Erinnerung loeschen
#   - core_memory_read: Core Memory lesen
#   - core_memory_update: Core Memory aktualisieren
#   - conversation_search: Konversationen durchsuchen
#   - conversation_search_date: Konversationen nach Datum suchen
EOF

# Server starten
# uvicorn mcp_servers.rag_api.server:app --host 0.0.0.0 --port 8100
```

**Pruefung:** `curl http://localhost:8100/health`
**Fehlerbehandlung:** Port belegt → anderen Port waehlen
**Rollback:** Prozess beenden: `kill $(lsof -t -i:8100)` (Linux/Mac) oder in PowerShell: `netstat -aon | findstr :8100` und dann `taskkill /PID <PID> /F`

### 3.2 Doc-Scanner MCP-Server

**Zweck:** Web-Dokumentationen scannen + importieren

**Befehle:**
```bash
mkdir -p mcp-servers/doc-scanner

pip install beautifulsoup4 playwright aiohttp

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

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer detaillierte MCP-Server-Konfiguration und API-Key-Einrichtung.

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
# settings.json mit ALLEN Hooks schreiben (einschliesslich Gehirn-System-Hooks)
# WICHTIG: Diese Datei enthaelt ALLE Hook-Konfigurationen. Nicht einzeln ueberschreiben!
cat > ~/.claude/settings.json << 'SETTINGSEOF'
{
  "hooks": {
    "SessionStart": [
      {"matcher": "startup", "type": "command", "command": "bash ~/.claude/hooks/session-start-startup.sh", "timeout": 15000},
      {"matcher": "compact", "type": "command", "command": "bash ~/.claude/hooks/session-start-compact.sh", "timeout": 10000},
      {"matcher": "resume", "type": "command", "command": "bash ~/.claude/hooks/session-start-resume.sh", "timeout": 15000},
      {"type": "command", "command": "bash ~/.claude/hooks/core-memory-inject.sh", "timeout": 10000}
    ],
    "UserPromptSubmit": [
      {"type": "command", "command": "bash ~/.claude/hooks/user-prompt-submit.sh", "timeout": 5000},
      {"type": "command", "command": "bash ~/.claude/hooks/auto-recall.sh", "timeout": 8000}
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
      {"type": "agent", "prompt": "Pruefe ob alle zugewiesenen Tasks erledigt sind. Kein Task darf uebersprungen oder als erledigt markiert sein ohne tatsaechlich erledigt zu sein.", "timeout": 60000},
      {"type": "command", "command": "bash ~/.claude/hooks/auto-capture.sh", "timeout": 10000}
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
      {"type": "command", "command": "bash ~/.claude/hooks/session-end.sh", "timeout": 15000},
      {"type": "command", "command": "bash ~/.claude/hooks/session-end-recall.sh", "timeout": 20000}
    ]
  }
}
SETTINGSEOF
```

**Pruefung:** `cat ~/.claude/settings.json | python3 -m json.tool` → Valides JSON
**Fehlerbehandlung:** JSON-Syntax-Fehler → online JSON Validator nutzen
**Rollback:** Backup wiederherstellen (install.sh erstellt automatisch Backups)

> **Siehe auch:** 01-PROJEKTPLANUNG.md Abschnitt Hook-System fuer die vollstaendige Hook-Beschreibung. 03-SETUP-ANLEITUNG.md fuer Debugging-Tipps.

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

> **Siehe auch:** 01-PROJEKTPLANUNG.md Abschnitt Agenten-Rollen fuer die detaillierten Rollenbeschreibungen.

---

## Schritt 6: Kommunikation

### 6.1 Slack Webhook

```bash
# 1. Slack App erstellen: https://api.slack.com/apps
# 2. Incoming Webhook aktivieren
# 3. Webhook URL speichern

mkdir -p ~/.claude/config
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

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer detaillierte Webhook-Konfiguration und Benachrichtigungs-Einstellungen.

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

> **Siehe auch:** 01-PROJEKTPLANUNG.md Abschnitt Fragenkatalog fuer die vollstaendige Spezifikation.

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

# Fuer Windows: Task Scheduler (schtasks) nutzen
# schtasks /create /tn "ClaudeAgentScan" /tr "python3 %USERPROFILE%\claude-agent-team\mcp-servers\doc-scanner\scan.py" /sc weekly /d SUN /st 03:00
```

**Pruefung:** `python3 mcp-servers/doc-scanner/scan.py --test`
**Abhaengigkeit:** RAG-API (Schritt 3.1) + HippoRAG 2 (Schritt 2.1)

> **Hinweis:** Das Skript `scan.py` wird in der Bau-Phase erstellt. Hier wird nur die Konfiguration vorbereitet.

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer URL-Listen-Konfiguration und Scan-Intervalle.

---

## Schritt 9: Sync-System

```bash
cd ~/claude-agent-team

# Sync-Repo initialisieren
# Hinweis: sync-setup.sh wird in der Bau-Phase erstellt
bash scripts/sync-setup.sh init

# Remote hinzufuegen
cd ~/.claude/sync-repo
git remote add origin https://github.com/DEIN-USER/claude-agent-team-config.git
git push -u origin main
```

**Pruefung:** `bash scripts/sync-setup.sh --status`
**Abhaengigkeit:** GitHub-Repo muss existieren

> **Hinweis:** Das Skript `sync-setup.sh` wird in der Bau-Phase erstellt. Hier wird nur der Ablauf dokumentiert.

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer Sync-Konfiguration und Konfliktloesung.

---

## Schritt 10: Cloud-Deployment

### 10.1 Docker Compose

```bash
cd ~/claude-agent-team

cat > docker-compose.yml << 'EOF'
services:
  neo4j:
    image: neo4j:5-community
    container_name: neo4j
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
    container_name: qdrant
    restart: always
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant-data:/qdrant/storage

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data

  recall-db:
    image: postgres:16-alpine
    container_name: recall-db
    restart: always
    environment:
      POSTGRES_DB: recall_memory
      POSTGRES_USER: recall_user
      POSTGRES_PASSWORD: ${RECALL_DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - recall-data:/var/lib/postgresql/data

  rag-api:
    build: ./mcp-servers/rag-api
    container_name: rag-api
    restart: always
    ports:
      - "8100:8100"
    depends_on:
      - neo4j
      - qdrant
      - redis
      - recall-db
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      QDRANT_URL: http://qdrant:6333
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      RECALL_DB_URL: postgresql://recall_user:${RECALL_DB_PASSWORD}@recall-db:5432/recall_memory

  doc-scanner:
    build: ./mcp-servers/doc-scanner
    container_name: doc-scanner
    restart: always
    ports:
      - "8101:8101"
    depends_on:
      - rag-api
    environment:
      RAG_API_URL: http://rag-api:8100

  hipporag:
    build: ./brain/hipporag-service
    container_name: hipporag
    restart: always
    ports:
      - "8102:8102"
    depends_on:
      - neo4j
      - qdrant
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      QDRANT_URL: http://qdrant:6333

  learning-graphs:
    build: ./brain/learning-graphs
    container_name: learning-graphs
    restart: always
    depends_on:
      - neo4j
    environment:
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}

  # --- Optionale Services ---
  # Ollama (lokales LLM, z.B. fuer Embedding oder Extraktion)
  # Auskommentieren und anpassen falls benoetigt:
  # ollama:
  #   image: ollama/ollama:latest
  #   container_name: ollama
  #   restart: always
  #   ports:
  #     - "11434:11434"
  #   volumes:
  #     - ollama-data:/root/.ollama

volumes:
  neo4j-data:
  neo4j-logs:
  qdrant-data:
  redis-data:
  recall-data:
  # ollama-data:
EOF

# .env Datei erstellen
cat > .env << 'EOF'
NEO4J_PASSWORD=SICHERES_PASSWORT
REDIS_PASSWORD=SICHERES_PASSWORT
RECALL_DB_PASSWORD=SICHERES_PASSWORT
CLAUDE_API_KEY=DEIN_API_KEY
EOF
```

> **Hinweis:** Die Dockerfiles fuer `rag-api` und `doc-scanner` (unter `./mcp-servers/rag-api/Dockerfile` und `./mcp-servers/doc-scanner/Dockerfile`) werden in der Bau-Phase erstellt. Ohne diese Dateien schlaegt `docker compose build` fehl.

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

> **Siehe auch:** 04-INSTALLATIONS-GUIDE.md fuer die vollstaendige Docker-Deployment-Anleitung.

---

## Schritt 11: Tests + Health-Check

```bash
# Health-Check Skript
cat > scripts/health-check.sh << 'HEALTHEOF'
#!/bin/bash
echo "=== Cloud Code Team Health-Check ==="

# .env laden fuer Passwoerter
if [ -f "$HOME/claude-agent-team/.env" ]; then
  source "$HOME/claude-agent-team/.env"
fi

# Neo4j
echo -n "Neo4j: "
curl -s http://localhost:7474 > /dev/null && echo "OK" || echo "FEHLER"

# Qdrant
echo -n "Qdrant: "
curl -s http://localhost:6333/collections > /dev/null && echo "OK" || echo "FEHLER"

# Redis
echo -n "Redis: "
docker exec redis redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q PONG && echo "OK" || echo "FEHLER"

# PostgreSQL (Recall-DB)
echo -n "Recall-DB: "
docker exec recall-db pg_isready -U recall_user -d recall_memory > /dev/null 2>&1 && echo "OK" || echo "FEHLER"

# RAG-API
echo -n "RAG-API: "
curl -s http://localhost:8100/health > /dev/null && echo "OK" || echo "FEHLER"

# Doc-Scanner
echo -n "Doc-Scanner: "
curl -s http://localhost:8101/health > /dev/null && echo "OK" || echo "FEHLER"

# HippoRAG-Service
echo -n "HippoRAG: "
curl -s http://localhost:8102/health > /dev/null && echo "OK" || echo "FEHLER (Degraded: S3/S5 deaktiviert)"

# Learning-Graphs
echo -n "Learning-Graphs: "
docker exec learning-graphs python3 -c "print('OK')" 2>/dev/null && echo "OK" || echo "FEHLER (Degraded: S5 deaktiviert)"

# Degraded Mode Check
echo ""
echo "=== Degraded Mode Status ==="
DEGRADED=false
curl -s http://localhost:7474 > /dev/null || { echo "WARNUNG: Neo4j down → S3/S5 deaktiviert"; DEGRADED=true; }
curl -s http://localhost:6333 > /dev/null || { echo "WARNUNG: Qdrant down → S2 nur Redis-Cache"; DEGRADED=true; }
docker exec redis redis-cli -a "$REDIS_PASSWORD" ping 2>/dev/null | grep -q PONG || { echo "WARNUNG: Redis down → Kein Cache/Event-Bus"; DEGRADED=true; }
docker exec recall-db pg_isready -U recall_user -d recall_memory > /dev/null 2>&1 || { echo "WARNUNG: PostgreSQL down → SQLite Fallback"; DEGRADED=true; }
$DEGRADED || echo "Alle Systeme normal — kein Degraded Mode"

echo "=== Ende ==="
HEALTHEOF

chmod +x scripts/health-check.sh
bash scripts/health-check.sh
```

**Erwartung:** Alle Services zeigen "OK"
**Fehlerbehandlung:** Fehlender Service → Container pruefen → neustarten

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer erweiterte Health-Check-Konfiguration und Monitoring.

---

## Schritt 12: Dokumentation generieren

> **Hinweis:** Die Node.js-Abhaengigkeiten (`package.json`, `tsconfig.json` etc.) werden in der Bau-Phase erstellt. Vor Ausfuehrung der folgenden Befehle muss `npm install` im Projektverzeichnis ausgefuehrt worden sein.

```bash
# Node.js-Abhaengigkeiten installieren (falls noch nicht geschehen)
cd ~/claude-agent-team
npm install

# TypeDoc fuer TypeScript
npx typedoc --entryPoints src --out docs/api

# Swagger/OpenAPI
# Wird automatisch vom PostToolUse Hook generiert

# Changelog
npx changeset version

# Storybook (wenn Frontend vorhanden)
npx storybook build -o docs/storybook
```

> **Siehe auch:** 03-SETUP-ANLEITUNG.md fuer Dokumentations-Standards und Vorlagen.

---

## Fehlerbehandlung: Allgemein

| Problem | Loesung |
|---------|---------|
| Container startet nicht | `docker logs CONTAINER_NAME` pruefen |
| Port belegt | `lsof -i :PORT` (Linux/Mac) oder `netstat -aon | findstr :PORT` (PowerShell/Windows) → Prozess beenden oder anderen Port waehlen |
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
  docker compose stop SERVICE_NAME && docker compose rm -f SERVICE_NAME
  docker compose up -d SERVICE_NAME

Stufe 3: Daten zuruecksetzen (VORSICHT)
  docker compose down -v  ← Loescht alle Volumes!
  docker compose up -d    ← Neustart mit leeren DBs

Stufe 4: Kompletter Rollback
  git log --oneline       ← Letzten guten Commit finden
  git checkout COMMIT_ID  ← Zurueck zum guten Stand
  docker compose up -d
```
