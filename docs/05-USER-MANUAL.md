# User Manual — Cloud Code Team 02.26

**Version:** 3.0
**Stand:** Februar 2026

---

## Inhaltsverzeichnis

1. [Schnelleinstieg](#1-schnelleinstieg)
2. [System-Uebersicht](#2-system-uebersicht)
3. [Die 11 Agenten](#3-die-11-agenten)
4. [Das Gehirn-System (6 Schichten)](#4-das-gehirn-system)
5. [Commands-Referenz](#5-commands-referenz)
6. [Brain-Tools Referenz](#6-brain-tools-referenz)
7. [Docker Services](#7-docker-services)
8. [Setup-Anleitung](#8-setup-anleitung)
9. [Konfiguration](#9-konfiguration)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Schnelleinstieg

### In 3 Minuten starten

```bash
# 1. Repo klonen
git clone -b ddd-v3-architecture https://github.com/dsactivi-2/Brain-Construction.git ~/Desktop/claude-agent-team
cd ~/Desktop/claude-agent-team

# 2. Mac: Automatisches Setup (Docker, DBs, Services, Profile)
./setup-mac.sh

# 3. API-Key eintragen
nano .env  # CLAUDE_API_KEY=sk-ant-...

# 4. Agent starten
claude --agent agents/berater/CLAUDE.md
```

### Was passiert beim Start?

1. **4 Datenbanken** starten (Neo4j, Qdrant, Redis, PostgreSQL)
2. **4 Brain-Services** starten (RAG-API, Doc-Scanner, HippoRAG, Learning-Graphs)
3. **11 Agent-Profile** werden geladen
4. **Hooks** verbinden das Gehirn-System automatisch
5. Der **Berater** ist dein einziger Kontaktpunkt — er koordiniert alle anderen

### Erster Befehl

```
Du: "Analysiere das Projekt in ~/my-app und erstelle einen Plan"
→ Berater empfaengt → delegiert an Analyst → Architekt prueft → Plan entsteht
```

---

## 2. System-Uebersicht

### Architektur

```
Du (Terminal / Slack / WhatsApp)
  |
  v
BERATER (Orchestrator, Hierarchie 10)
  |
  +-- ARCHITEKT (9) -------- System-Design, Veto-Recht
  +-- MEMORY-MANAGER (8) --- Brain-System Pflege, DB-Health
  +-- CODER (7) ------------ Implementierung, Refactoring
  +-- TESTER (6) ----------- Tests, Debugging
  +-- REVIEWER (5) --------- Code-Review, Commit, Push
  +-- DESIGNER (4) --------- UI/UX, Frontend
  +-- ANALYST (3) ---------- Repo-Analyse, Vergleiche
  +-- DOC-SCANNER (2) ------ Web-Doku scannen + importieren
  +-- DEVOPS (2) ----------- CI/CD, Deploy, Server
  +-- DOKUMENTIERER (1) ---- Automatische Dokumentation
  |
  v
GEHIRN-SYSTEM (6 Schichten)
  S1: Core Memory (Redis) — immer geladen
  S2: Auto-Recall/Capture (Qdrant) — automatisch
  S3: HippoRAG 2 (Neo4j+Qdrant) — Wissensgraph
  S4: Agentic RAG (lokal) — intelligente Suche
  S5: Learning Graphs (Neo4j) — selbst-lernendes Netz
  S6: Recall Memory (PostgreSQL) — komplette Historie
```

### Wie es funktioniert

1. Du gibst dem **Berater** einen Auftrag
2. Er stellt Rueckfragen wenn noetig
3. Er erstellt einen Plan und delegiert an die richtigen Agenten
4. Agenten arbeiten parallel wo moeglich
5. Das **Gehirn-System** merkt sich alles — ueber Sessions, Rechner und Projekte
6. Du bekommst das fertige Ergebnis

---

## 3. Die 11 Agenten

### BERATER — Der Orchestrator
- **Hierarchie:** 10 (hoechste)
- **Modell:** Opus
- **Was er macht:** Einziger Kontakt zum Nutzer. Empfaengt Auftraege, stellt Rueckfragen, erstellt Plaene, delegiert an andere Agenten, meldet Fortschritt.
- **Wann nutzen:** Immer — er ist dein Einstiegspunkt fuer alles.
- **Befehle:** `/briefing`, `/plan`, `/delegate`, `/fortschritt`, `/stop-alle`

### ARCHITEKT — Der System-Designer
- **Hierarchie:** 9
- **Modell:** Opus
- **Was er macht:** Prueft System-Design, hat Veto-Recht, erstellt Abhaengigkeits-Graphen, dokumentiert Architektur-Entscheidungen (ADR).
- **Wann nutzen:** Bei neuem Feature-Design, Struktur-Fragen, Technologie-Entscheidungen.
- **Befehle:** `/design`, `/veto`, `/deps`, `/adr`

### MEMORY-MANAGER — Der Gehirn-Pfleger
- **Hierarchie:** 8
- **Modell:** Sonnet (Routine) / Opus (Konsolidierung)
- **Was er macht:** Pflegt das 6-Schichten Gehirn-System. Health-Checks, Konsolidierung (S6→S3), Decay/Pruning, Graph-Snapshots, Warm-Up Cache.
- **Einziger Agent mit Zugriff auf ALLE 15 Brain-Tools.**
- **Wann nutzen:** Bei DB-Problemen, manueller Konsolidierung, Graph-Rollback.
- **Befehle:** `/health-db`, `/consolidate`, `/prune`, `/snapshot`, `/warm-up`, `/stats`, `/rollback-graph`

### CODER — Der Implementierer
- **Hierarchie:** 7
- **Modell:** Sonnet / Opus
- **Was er macht:** Schreibt Code, Refactoring, nutzt Templates, registriert Funktionen (FN-XXX) und Endpoints (EP-XXX).
- **Wann nutzen:** Bei Implementierungsaufgaben (wird vom Berater delegiert).
- **Befehle:** `/implement`, `/refactor`, `/check`, `/templates`, `/register`

### TESTER — Der Qualitaetspruefer
- **Hierarchie:** 6
- **Modell:** Sonnet / Opus
- **Was er macht:** Schreibt Tests, fuehrt sie aus, analysiert Fehler (Root-Cause), misst Coverage.
- **Wann nutzen:** Nach Code-Aenderungen (wird automatisch getriggert).
- **Befehle:** `/test`, `/debug`, `/coverage`, `/regression`

### REVIEWER — Der Code-Pruefer
- **Hierarchie:** 5
- **Modell:** Sonnet / Opus
- **Was er macht:** Prueft Code-Qualitaet, fixt kleine Fehler selbst, macht Commit + Push.
- **Wann nutzen:** Nach Implementierung (automatisch nach Coder).
- **Befehle:** `/review`, `/commit`, `/repo`, `/changelog`

### DESIGNER — Der UI/UX-Experte
- **Hierarchie:** 4
- **Modell:** Sonnet / Opus
- **Was er macht:** Erstellt UI-Komponenten, Design-System, Accessibility-Checks.
- **Wann nutzen:** Bei Frontend-Aufgaben, UI-Design, Responsive-Design.
- **Befehle:** `/design-ui`, `/theme`, `/responsive`, `/a11y`

### ANALYST — Der Repo-Analyst
- **Hierarchie:** 3
- **Modell:** Sonnet / Opus
- **Was er macht:** Analysiert Repos tiefgehend, vergleicht Code, plant Merges, erstellt Dependency-Maps.
- **Wann nutzen:** Bei Repo-Analyse, Code-Vergleichen, Merge-Planung.
- **Befehle:** `/analyze`, `/compare`, `/merge-plan`, `/deps-map`

### DOC-SCANNER — Der Doku-Scanner
- **Hierarchie:** 2
- **Modell:** Haiku / Sonnet
- **Was er macht:** Scannt Web-Dokumentationen, erkennt Aenderungen, importiert in Wissensgraph.
- **Wann nutzen:** Externe Doku einlesen, API-Doku ueberwachen.
- **Befehle:** `/scan`, `/scan-list`, `/scan-add`, `/scan-diff`, `/kb-import`

### DEVOPS — Der Infrastruktur-Manager
- **Hierarchie:** 2
- **Modell:** Sonnet / Opus
- **Was er macht:** CI/CD Pipelines, Docker-Orchestrierung, Deployment, Rollback.
- **Wann nutzen:** Bei Deployment, Server-Konfiguration, Infrastruktur-Aenderungen.
- **Befehle:** `/deploy`, `/env`, `/ci`, `/health`, `/rollback`

### DOKUMENTIERER — Der Doku-Generator
- **Hierarchie:** 1
- **Modell:** Haiku / Sonnet
- **Was er macht:** Generiert automatisch 9 Arten von Dokumentation (API-Docs, Registry, Changelogs, Handbuecher).
- **Wann nutzen:** Nach Code-Aenderungen (automatisch via Hook).
- **Befehle:** `/docs`, `/registry`, `/changelog`, `/api-docs`

---

## 4. Das Gehirn-System

### Die 6 Schichten

| Schicht | Name | Was es macht | Datenbank | Latenz |
|:-------:|------|-------------|-----------|--------|
| **S1** | Core Memory | Immer im Kontext. Projekt-Info, User-Praeferenzen, aktuelle Arbeit | Redis + JSON | <5ms |
| **S2** | Auto-Recall/Capture | Automatisch relevante Erinnerungen laden/speichern | Qdrant + Redis | ~20ms |
| **S3** | HippoRAG 2 | Wissensgraph mit PageRank. Entitaeten + Beziehungen | Neo4j + Qdrant | ~24ms |
| **S4** | Agentic RAG | Intelligente Suchsteuerung. Entscheidet WO gesucht wird | Lokal (Prozess) | 0ms |
| **S5** | Learning Graphs | Selbst-lernendes Wissensnetz. Waechst mit jeder Interaktion | Neo4j | ~24ms |
| **S6** | Recall Memory | Komplette rohe Konversationshistorie. Nichts geht verloren | PostgreSQL | ~4ms |

### Wie die Schichten zusammenarbeiten

```
Du fragst etwas
  → S1: Core Memory pruefen (sofort da, 0 Latenz)
  → S2: Auto-Recall injiziert relevante Erinnerungen
  → S4: Agentic RAG entscheidet: Muss ich tiefer suchen?
    → S3: HippoRAG 2 durchsucht Wissensgraph + PageRank
    → Gut genug? → Antwort liefern
    → Nicht genug? → Weitere Suche (Web, Code, Docs)
  → S5: Neues Wissen → Learning Graphs erweitern
  → S2: Auto-Capture speichert neue Fakten
  → S6: Komplette Konversation wird gespeichert (bei Session-Ende)
```

### 3 Gehirn-Mechanismen

| Mechanismus | Was | Zyklus |
|-------------|-----|--------|
| **Konsolidierung** | S6 (Rohdaten) → LLM-Analyse → S3 (strukturiertes Wissen) | Woechentlich |
| **Decay/Pruning** | Alte, ungenutzte Erinnerungen verlieren Score → Archiv | Taeglich |
| **Priority-Scoring** | Jede Erinnerung bekommt Score 1-10 (hoeher = wichtiger) | Bei jedem Speichern |

---

## 5. Commands-Referenz

### Globale Commands (alle Agenten)

| Command | Was |
|---------|-----|
| `/status` | Agent-Status anzeigen |
| `/memory` | Wissensdatenbank durchsuchen (alle 6 Schichten) |
| `/save` | Manuell in DB speichern |
| `/fragen` | Offene Fragen im Katalog anzeigen |
| `/profil` | Aktive Profile anzeigen |
| `/cache` | Cache abfragen |
| `/tools` | Verfuegbare Tools anzeigen |

### Berater-Commands

| Command | Was |
|---------|-----|
| `/briefing` | Strukturiertes Briefing starten |
| `/plan` | Aufgabenplan erstellen |
| `/delegate` | Task an Agent zuweisen |
| `/katalog` | Fragenkatalog anzeigen |
| `/fortschritt` | Status aller Agenten |
| `/stop-alle` | Alle Agenten stoppen |
| `/weiter` | Naechsten Schritt ausfuehren |

### Memory-Manager Commands

| Command | Was |
|---------|-----|
| `/health-db` | Health-Check aller 4 Cloud-DBs |
| `/consolidate` | Manuelle Konsolidierung (S6→S3) |
| `/prune` | Manuelles Decay/Pruning |
| `/snapshot` | Graph-Snapshot erstellen |
| `/warm-up` | Warm-Up Cache refreshen |
| `/seed` | Initiale Brain-Population |
| `/stats` | Brain-System Statistiken |
| `/rollback-graph` | Graph auf Snapshot zuruecksetzen |

### Weitere Agent-Commands

| Agent | Commands |
|-------|----------|
| Architekt | `/design`, `/veto`, `/deps`, `/adr` |
| Coder | `/implement`, `/refactor`, `/check`, `/templates`, `/register` |
| Tester | `/test`, `/debug`, `/coverage`, `/regression` |
| Reviewer | `/review`, `/commit`, `/repo`, `/changelog` |
| Designer | `/design-ui`, `/theme`, `/responsive`, `/a11y` |
| Analyst | `/analyze`, `/compare`, `/merge-plan`, `/deps-map` |
| Doc-Scanner | `/scan`, `/scan-list`, `/scan-add`, `/scan-diff`, `/kb-import` |
| DevOps | `/deploy`, `/env`, `/ci`, `/health`, `/rollback` |
| Dokumentierer | `/docs`, `/registry`, `/changelog`, `/api-docs` |

---

## 6. Brain-Tools Referenz

### 15 Tools (FN-051 bis FN-069)

| FN-ID | Tool | Schicht | Was |
|-------|------|:-------:|-----|
| FN-051 | `core_memory_read` | S1 | Core Memory lesen |
| FN-052 | `core_memory_update` | S1 | Core Memory aktualisieren |
| FN-053 | `memory_search` | S2 | Semantische Suche in Erinnerungen |
| FN-054 | `memory_store` | S2 | Erinnerung speichern (Priority 1-10) |
| FN-055 | `memory_list` | S2 | Alle Erinnerungen auflisten |
| FN-056 | `memory_get` | S2 | Einzelne Erinnerung abrufen |
| FN-057 | `memory_forget` | S2 | Erinnerung loeschen |
| FN-058 | `conversation_search` | S6 | Konversationen durchsuchen |
| FN-059 | `conversation_search_date` | S6 | Konversationen nach Datum suchen |
| FN-064 | `hipporag_ingest` | S3 | Text in Wissensgraph aufnehmen |
| FN-065 | `hipporag_retrieve` | S3 | Wissen aus Wissensgraph abrufen |
| FN-066 | `learning_graph_update` | S5 | Learning Graph aktualisieren |
| FN-067 | `consolidate` | S5 | Konsolidierung ausfuehren |
| FN-068 | `decay_prune` | S5 | Decay/Pruning ausfuehren |
| FN-069 | `rag_route` | S4 | Query intelligent routen |

### Welcher Agent hat welche Tools?

| Agent | Tools | Anzahl |
|-------|-------|:------:|
| Berater | Alle ausser consolidate, decay_prune | 13 |
| Memory-Manager | **ALLE 15** | 15 |
| Architekt | core_memory, memory_*, hipporag_*, conversation_*, rag_route | 12 |
| Coder | core_memory, memory_*, hipporag_retrieve, conversation_search, rag_route | 11 |
| Tester | core_memory, memory_*, hipporag_retrieve, conversation_search, rag_route | 12 |
| Designer | core_memory, memory_search/store, hipporag_retrieve, rag_route | 10 |
| DevOps | core_memory, memory_*, hipporag_*, conversation_*, rag_route | 12 |

---

## 7. Docker Services

### 8 Services

| Service | Port | Health-Check | Zweck |
|---------|------|-------------|-------|
| **neo4j** | 7474 (Browser), 7687 (Bolt) | http://localhost:7474 | Wissensgraph (S3+S5) |
| **qdrant** | 6333 | http://localhost:6333/dashboard | Vektor-Embeddings (S2+S3) |
| **redis** | 6379 | `redis-cli ping` | Core Memory + Cache + Event-Bus |
| **recall-db** | 5432 | `pg_isready` | Recall Memory (S6) |
| **rag-api** | 8100 | http://localhost:8100/health | Agentic RAG Router (S4) |
| **doc-scanner** | 8101 | http://localhost:8101/health | Web-Doku Scanner |
| **hipporag** | 8102 | http://localhost:8102/health | HippoRAG + spaCy NER |
| **learning-graphs** | — | `docker compose ps` | Learning Graphs (S5) |

### Haeufige Befehle

```bash
# Status aller Services
docker compose ps

# Logs eines Service
docker compose logs -f rag-api

# Neustart eines Service
docker compose restart hipporag

# Alles stoppen
docker compose down

# Alles starten
docker compose up -d

# Neu bauen (nach Code-Aenderung)
docker compose build hipporag && docker compose up -d hipporag
```

---

## 8. Setup-Anleitung

### Voraussetzungen

| Tool | Mac | Windows |
|------|-----|---------|
| Docker Desktop | `brew install --cask docker` | https://docs.docker.com/desktop/install/windows-install/ |
| Python 3.10+ | `brew install python3` | https://python.org |
| Git | `brew install git` | https://git-scm.com |
| Claude CLI | `npm install -g @anthropic-ai/claude-code` | `npm install -g @anthropic-ai/claude-code` |
| Node.js (fuer Claude CLI) | `brew install node` | https://nodejs.org |

### Mac Setup (automatisch)

```bash
git clone -b ddd-v3-architecture https://github.com/dsactivi-2/Brain-Construction.git ~/Desktop/claude-agent-team
cd ~/Desktop/claude-agent-team
./setup-mac.sh
```

Das Script macht:
1. Prerequisites pruefen
2. Repository klonen/aktualisieren
3. `.env` mit zufaelligem DB-Passwort generieren
4. Docker Services starten (4 DBs + 4 Brain Services)
5. Health-Checks aller 8 Services
6. Agent-Profile mergen und deployen
7. Claude Code Konfiguration einrichten (MCP + Hooks)

### Windows Setup (manuell)

```bash
git clone -b ddd-v3-architecture https://github.com/dsactivi-2/Brain-Construction.git ~/Desktop/claude-agent-team
cd ~/Desktop/claude-agent-team

# .env erstellen (Vorlage kopieren und Passwort + API-Key eintragen)
cp .env.example .env
nano .env

# Docker Services starten
docker compose up -d

# Warten bis alles laeuft (~30 Sekunden)
curl http://localhost:8100/health

# Profile mergen
python config/agent-profiles/merge_profiles.py
```

### Nach dem Setup

1. **`.env` anpassen:**
   - `CLAUDE_API_KEY=sk-ant-...` eintragen
   - Optional: Cloud-URIs fuer Fallback eintragen

2. **Agent starten:**
   ```bash
   cd ~/Desktop/claude-agent-team
   claude --agent agents/berater/CLAUDE.md
   ```

3. **Health pruefen:**
   ```bash
   curl http://localhost:8100/health
   # Erwartete Antwort: {"status":"ok","backends":{"qdrant":"connected","neo4j":"connected",...}}
   ```

---

## 9. Konfiguration

### Wichtige Dateien

| Datei | Was |
|-------|-----|
| `.env` | Datenbank-Passwoerter, API-Keys, Cloud-URIs |
| `.claude/settings.json` | MCP Server + Hook-Definitionen (Projekt-Level) |
| `config/databases.yaml` | Datenbank-Verbindungen |
| `config/core-memory.json` | Core Memory Template (5 Bloecke) |
| `agents/{name}/CLAUDE.md` | Agent-Anweisungen |
| `agents/{name}/profile.json` | Gemerged Agent-Profil (JSON) |
| `docker-compose.yml` | Docker Service-Definitionen |

### .env Variablen

| Variable | Beschreibung |
|----------|-------------|
| `NEO4J_PASSWORD` | Neo4j Datenbank-Passwort |
| `REDIS_PASSWORD` | Redis Passwort |
| `RECALL_DB_PASSWORD` | PostgreSQL Passwort |
| `NEO4J_URI` | Local: `bolt://localhost:7687` |
| `QDRANT_URL` | Local: `http://localhost:6333` |
| `REDIS_URL` | Local: `redis://:PASSWORD@localhost:6379/0` |
| `RECALL_DB_URL` | Local: `postgresql://recall_user:PASSWORD@localhost:5432/recall_memory` |
| `CLAUDE_API_KEY` | Anthropic API Key |
| `*_CLOUD_*` | Cloud-Fallback URIs (optional) |

### Hooks (17 automatische Aktionen)

Die Hooks sind in `.claude/settings.json` definiert und laufen automatisch:

| Hook | Wann | Was passiert |
|------|------|-------------|
| SessionStart | Agent startet | Core Memory laden, Warm-Up Bundle |
| UserPromptSubmit | User tippt | Auto-Recall (relevante Erinnerungen laden) |
| PreToolUse (Write) | Vor Code-Aenderung | Sicherheits-Check |
| PreToolUse (Bash) | Vor Shell-Befehl | Gefaehrliche Befehle blockieren |
| PostToolUse | Nach Aktion | Output loggen, Fehler tracken |
| Stop | Agent stoppt | Auto-Capture (neue Fakten speichern) |
| SessionEnd | Session endet | Konversation in Recall Memory (S6) |
| PreCompact | Vor Komprimierung | Kontext in HippoRAG sichern |

---

## 10. Troubleshooting

### Service startet nicht

```bash
# Logs pruefen
docker compose logs rag-api

# Service neu starten
docker compose restart rag-api

# Alles neu bauen
docker compose down && docker compose up -d --build
```

### Datenbank nicht erreichbar

```bash
# Health-Check
curl http://localhost:8100/health

# Einzelne DB pruefen
docker exec redis redis-cli -a "DEIN_PASSWORD" ping
docker exec recall-db pg_isready -U recall_user
curl http://localhost:7474
curl http://localhost:6333/collections
```

### Brain-Tools funktionieren nicht

1. Pruefen ob MCP Server konfiguriert ist:
   ```bash
   cat .claude/settings.json | python3 -m json.tool | grep brain-tools
   ```

2. Pruefen ob Python-Pfad stimmt:
   ```bash
   python3 mcp-servers/brain-tools/server.py --help
   ```

3. Pruefen ob alle DBs laufen:
   ```bash
   docker compose ps
   ```

### Degraded Mode

Wenn eine Datenbank ausfaellt:

| DB Down | Was geht nicht | Was geht weiter | Fallback |
|---------|---------------|-----------------|----------|
| Neo4j | S3+S5 (Wissensgraph) | S1, S2, S4, S6 | — |
| Qdrant | S2 Vektoren, S3 Embeddings | S1, S6 | Redis-Cache |
| Redis | S1 Shared, Event-Bus, Cache | S1 lokal, S3, S6 | Direkte DB-Queries |
| PostgreSQL | S6 Cloud | S1, S2, S3, S5 | SQLite+WAL lokal |

### Performance-Referenzwerte

| Metrik | Erwarteter Wert |
|--------|----------------|
| Core Memory laden (Redis) | <5ms |
| Vektor-Suche (Qdrant) | ~20ms |
| Wissensgraph-Query (Neo4j) | ~24ms |
| Recall Memory Query (PostgreSQL) | ~4ms |
| Warm-Up Bundle (Redis GET) | <5ms |
| Agent-Start bis einsatzbereit | <100ms |
