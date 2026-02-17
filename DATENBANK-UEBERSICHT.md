# Datenbank-Uebersicht — Cloud Code Team 02.26

Erstellt: 2026-02-17
Zugangsdaten: Siehe Desktop/DATENBANK-ZUGAENGE.md (NICHT in Git!)

---

## 1. Neo4j (Wissensgraph)

**Zweck:** Schicht 3 (HippoRAG) + Schicht 5 (Learning Graphs) — Wissensgraph, Entitaeten, Beziehungen

| | Lokal | Cloud |
|--|-------|-------|
| Anbieter | Docker | Neo4j Aura |
| URL | localhost:7474 / bolt://localhost:7687 | https://console.neo4j.io/ |
| Image | neo4j:5-community | — |
| Plugins | APOC, Graph Data Science | — |
| Volume | neo4j-data | — |
| Status | Laeuft | Noch nicht eingerichtet |

---

## 2. Qdrant (Vektor-Datenbank)

**Zweck:** Schicht 2 (Auto-Recall, semantische Suche) + Schicht 3 (HippoRAG Embeddings)

| | Lokal | Cloud |
|--|-------|-------|
| Anbieter | Docker | Qdrant Cloud |
| URL | localhost:6333 (API) / :6334 (gRPC) | https://cloud.qdrant.io/ |
| Image | qdrant/qdrant:latest | — |
| Collections | hipporag_embeddings, mem0_memories | — |
| Vektoren | 384 Dimensionen, Cosine | — |
| Volume | qdrant-data | — |
| Status | Laeuft | API Key vorhanden, Cluster noch nicht erstellt |

---

## 3. Redis (Cache + Event-Bus)

**Zweck:** Core Memory Shared, Event-Bus (Pub/Sub), Warm-Up Bundle, Task-Queue

| | Lokal | Cloud |
|--|-------|-------|
| Anbieter | Docker | Redis Labs |
| URL | localhost:6379 | redis-11832.c250.eu-central-1-1.ec2.cloud.redislabs.com:11832 |
| Image | redis:7-alpine | — |
| Volume | redis-data | — |
| Status | Laeuft | Verbunden |

---

## 4. PostgreSQL (Recall Memory)

**Zweck:** Schicht 6 (Recall Memory) — Rohe Konversationshistorie, jede Nachricht gespeichert

| | Lokal | Cloud |
|--|-------|-------|
| Anbieter | Docker | Neon.tech |
| URL | localhost:5432 | ep-sweet-tooth-ag6ed99g-pooler.c-2.eu-central-1.aws.neon.tech |
| Version | PostgreSQL 16 | PostgreSQL 17.7 |
| Image | postgres:16-alpine | — |
| Datenbank | recall_memory | neondb |
| Volume | recall-data | — |
| Tabelle | conversations (erstellt) | conversations (erstellt) |
| Status | Laeuft | Verbunden |

### Tabellen-Schema (conversations)
```
id            SERIAL PRIMARY KEY
session_id    VARCHAR(64) NOT NULL
timestamp     TIMESTAMPTZ NOT NULL DEFAULT NOW()
role          VARCHAR(16) NOT NULL    -- user, assistant, system, tool
content       TEXT
tool_calls    JSONB
metadata      JSONB
```
Indizes: session_id, timestamp, role

---

## 5. SQLite (Lokaler Fallback)

**Zweck:** Offline-Fallback fuer Recall Memory

- **Pfad:** brain/recall_memory/conversations.db
- **Gleiches Schema** wie PostgreSQL (ohne JSONB, statt TEXT)
- **Kein Docker noetig**

---

## 6. Core Memory (JSON)

**Zweck:** Schicht 1 — Persistenter Kontext, immer geladen

- **Live-Datei:** ~/.claude/core-memory.json
- **Template:** config/core-memory.json

| Block | Storage | Zugriff |
|-------|---------|---------|
| [USER] | Redis (Shared) | Alle Agenten |
| [PROJEKT] | Redis (Shared) | Alle Agenten |
| [ENTSCHEIDUNGEN] | Redis (Shared) | Alle Agenten |
| [FEHLER-LOG] | Lokal (JSON) | Nur dieser Agent |
| [AKTUELLE-ARBEIT] | Lokal (JSON) | Nur dieser Agent |

---

## Datei-Struktur

### Projekt
```
claude-agent-team/
├── docker-compose.yml         ← 4 DB-Container
├── config/
│   ├── databases.yaml         ← Connection Strings (NICHT in Git!)
│   ├── core-memory.json       ← Template
│   ├── mem0-config.json       ← Mem0 Provider
│   └── communication.json     ← Slack/WhatsApp/Linear
├── brain/
│   ├── recall_memory/         ← SQLite Fallback
│   ├── auto_memory/           ← Python-Module (noch leer)
│   ├── hipporag_service/      ← S3 Service (noch leer)
│   ├── agentic_rag/           ← S4 Service (noch leer)
│   ├── learning_graphs/       ← S5 Service (noch leer)
│   └── logs/                  ← Fehler-Logs
└── scripts/
    ├── init-brain.sh          ← Einmal-Setup
    └── health-check.sh        ← Alle DBs pruefen
```

### Docker Volumes
```
neo4j-data      ← Neo4j Graph-Daten
neo4j-logs      ← Neo4j Logs
qdrant-data     ← Qdrant Vektor-Daten
redis-data      ← Redis Cache-Daten
recall-data     ← PostgreSQL Recall Memory
```

---

## Docker-Befehle

```bash
docker compose up -d          # Alle 4 DBs starten
docker compose ps             # Status pruefen
docker compose down           # Stoppen
docker compose logs -f        # Logs anschauen
```

---

## Cloud-Dashboards

| Dienst | Dashboard |
|--------|-----------|
| Neo4j Aura | https://console.neo4j.io/ |
| Qdrant Cloud | https://cloud.qdrant.io/ |
| Redis Cloud | https://app.redislabs.com/ |
| Neon PostgreSQL | https://console.neon.tech/ |
| GitHub Repo | https://github.com/dsactivi-2/Brain-Construction |

---

## Zugangsdaten

**NICHT in diesem Dokument!**
Siehe: `C:\Users\ds\Desktop\DATENBANK-ZUGAENGE.md` (nur lokal, nicht in Git)
