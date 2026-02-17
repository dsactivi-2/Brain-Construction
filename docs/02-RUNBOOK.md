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

**Core-Memory Tools (5 Befehle fuer den Agenten):**

| Tool | Beschreibung |
|------|-------------|
| `core_memory_append(block, inhalt)` | Fuegt Text an einen Block an |
| `core_memory_replace(block, alt, neu)` | Ersetzt Text innerhalb eines Blocks |
| `core_memory_remove(block, inhalt)` | Entfernt Text aus einem Block |
| `core_memory_read(block)` | Liest einen einzelnen Block |
| `core_memory_list()` | Zeigt alle Bloecke mit aktuellem Fuellstand |

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
```bash
cat > ~/.claude/hooks/auto-recall.sh << 'RECALLEOF'
#!/bin/bash
# Auto-Recall: Relevante Erinnerungen vor Antwort suchen und injizieren
PROMPT="$1"
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys, os
sys.path.insert(0, "$BRAIN_DIR")

from auto_memory.recall import search_memories

# Semantische Suche ueber alle Memory-Scopes
results = search_memories(
    query="$PROMPT",
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
```bash
cat > ~/.claude/hooks/auto-capture.sh << 'CAPTUREEOF'
#!/bin/bash
# Auto-Capture: Neue Fakten/Entscheidungen nach Antwort extrahieren und speichern
CONVERSATION="$1"
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sys
sys.path.insert(0, "$BRAIN_DIR")

from auto_memory.capture import extract_and_store

# Extrahiere neue Erinnerungen aus der Konversation
new_memories = extract_and_store(
    conversation="$CONVERSATION",
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
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "bash ~/.claude/hooks/auto-recall.sh \"$PROMPT\"",
        "timeout": 8000
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "bash ~/.claude/hooks/auto-capture.sh \"$CONVERSATION\"",
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
| `memory_add(text, scope, type)` | Erinnerung manuell hinzufuegen |
| `memory_search(query, scope, top_k)` | Erinnerungen semantisch suchen |
| `memory_delete(memory_id)` | Einzelne Erinnerung loeschen |
| `memory_update(memory_id, new_text)` | Erinnerung aktualisieren |
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
     Qdrant (Vektoren)      SQLite/Redis
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
```bash
cat > ~/.claude/hooks/session-end-recall.sh << 'RECALLENDEOF'
#!/bin/bash
# Recall Memory: Komplette Konversation bei Session-Ende speichern
BRAIN_DIR="$HOME/claude-agent-team/brain"

python3 << PYEOF
import json, sqlite3, uuid, os
from datetime import datetime

DB_PATH = os.path.join("$BRAIN_DIR", "recall_memory", "conversations.db")
CONV_DATA = os.environ.get("CLAUDE_CONVERSATION", "")
SESSION_ID = os.environ.get("CLAUDE_SESSION_ID", "unknown")
AGENT_NAME = os.environ.get("CLAUDE_AGENT_NAME", "unknown")

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

### 2.7 Zusammenspiel der 3 neuen Gehirn-Schichten

```
┌─────────────────────────────────────────────────────────────┐
│                    GEHIRN-SYSTEM v2                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 1: CORE MEMORY (Schritt 2.4)                 │  │
│  │ → Immer im Kontext, sofort verfuegbar                │  │
│  │ → 5 Bloecke, max 20k Zeichen                        │  │
│  │ → Injection via SessionStart Hook                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                         ▲ liest                             │
│                         │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 2: AUTO-RECALL/CAPTURE (Schritt 2.5)         │  │
│  │ → Automatisch bei jedem Prompt (Recall)              │  │
│  │ → Automatisch nach jeder Antwort (Capture)           │  │
│  │ → Kurzzeit + Langzeit Scopes                         │  │
│  │ → Kann Core Memory aktualisieren                     │  │
│  └───────────────────────────────────────────────────────┘  │
│                         ▲ durchsucht                        │
│                         │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Schicht 3: RECALL MEMORY (Schritt 2.6)               │  │
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

**Alle 3 Schichten muessen konfiguriert sein BEVOR Schritt 3 (MCP-Server) beginnt.**

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
