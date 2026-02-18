# Cloud Code Team 02.26 — Brain System

Du bist Teil eines Multi-Agenten-Systems mit 30-40 parallelen Agenten.
Jeder Agent hat Zugriff auf ein 6-Schichten-Gehirn-System.

## Gehirn-Architektur (6 Schichten)

| Schicht | Name | Datenbank | Zugriff |
|:-------:|------|-----------|---------|
| S1 | Core Memory | Redis (Shared) + JSON (Agent-Only) | `core_memory_read`, `core_memory_update` |
| S2 | Auto-Recall/Capture | Qdrant + Redis | `memory_search`, `memory_store`, `memory_list`, `memory_get`, `memory_forget` |
| S3 | HippoRAG 2 | Neo4j + Qdrant | `hipporag_retrieve`, `hipporag_ingest` |
| S4 | Agentic RAG | Lokal (Prozess) | `rag_route` |
| S5 | Learning Graphs | Neo4j | `learning_graph_update`, `consolidate`, `decay_prune` |
| S6 | Recall Memory | PostgreSQL | `conversation_search`, `conversation_search_date` |

## Such-Routing — Welches Tool fuer welche Frage?

BEVOR du antwortest, bestimme die richtige Suchstrategie:

### Entscheidungsbaum

```
User fragt etwas
│
├── Faktenfrage / bekanntes Wissen?
│   → core_memory_read (S1) — IMMER ZUERST
│   → Antwort im Core Memory? → Fertig
│
├── "Suche nach X" / Semantische Suche?
│   → memory_search(query) (S2) — Qdrant Vektor-Suche
│   → Findet aehnliche Erinnerungen nach Relevanz
│
├── Komplexe Zusammenhaenge / Entitaeten / Beziehungen?
│   → hipporag_retrieve(query) (S3) — Wissensgraph + PPR
│   → Findet verknuepfte Konzepte, Personen, Projekte
│
├── "Was haben wir letzte Woche gemacht?" / Historisch?
│   → conversation_search(query) (S6) — PostgreSQL Volltext
│   → conversation_search_date(start, end) fuer Zeitraeume
│
├── Unbekannt / Komplex / Mehrere Quellen noetig?
│   → rag_route(query) (S4) — Router entscheidet automatisch
│   → Sucht parallel in S2 + S3 + S6, bewertet Ergebnisse
│   → Retry bei schlechten Ergebnissen (max 3 Runden)
│
└── Neues Wissen / Wichtige Entscheidung gefallen?
    → memory_store(text, scope, type, priority) (S2)
    → core_memory_update(block, content) (S1) bei Kern-Aenderungen
```

### Routing-Beispiele

| User sagt | Tool | Schicht | Warum |
|-----------|------|:-------:|-------|
| "Wie heisst unser Projekt?" | `core_memory_read` | S1 | Basis-Fakt, immer im Core Memory |
| "Suche nach Sipgate" | `memory_search("Sipgate")` | S2 | Semantische Suche ueber alle Erinnerungen |
| "Welche Projekte haengen mit Sipgate zusammen?" | `hipporag_retrieve("Sipgate Projekte")` | S3 | Entitaets-Beziehungen im Wissensgraph |
| "Was haben wir gestern besprochen?" | `conversation_search_date(gestern)` | S6 | Zeitbasierte Suche in Konversations-Historie |
| "Finde alles ueber unsere API-Architektur" | `rag_route("API Architektur")` | S4 | Komplex — Router sucht in S2+S3+S6 parallel |

## Core Memory — Immer Geladen

Core Memory wird bei JEDEM Session-Start automatisch injiziert (via Hook).
Es enthaelt 5 Bloecke:

| Block | Inhalt | Storage | Zugriff |
|-------|--------|---------|---------|
| [USER] | Name, Rolle, Vorlieben, Kommunikationsstil | Redis (Shared) | Alle Agenten |
| [PROJEKT] | Stack, Architektur, aktuelle Phase | Redis (Shared) | Alle Agenten |
| [ENTSCHEIDUNGEN] | Architektur-Entscheidungen mit Begruendung | Redis (Shared) | Alle Agenten |
| [FEHLER-LOG] | Bekannte Fehler, Workarounds | Lokal (JSON) | Nur dieser Agent |
| [AKTUELLE-ARBEIT] | Offene Tasks, Status | Lokal (JSON) | Nur dieser Agent |

**Regeln:**
- Lies Core Memory am Anfang jeder Aufgabe
- Update Core Memory wenn sich Kern-Informationen aendern
- [USER], [PROJEKT], [ENTSCHEIDUNGEN] sind fuer ALLE Agenten sichtbar (Redis)
- [FEHLER-LOG], [AKTUELLE-ARBEIT] sind PRIVAT pro Agent (lokale JSON)

## Memory-Speicherung — Priority-Score

Beim Speichern neuer Erinnerungen IMMER Priority-Score mitgeben:

```
memory_store(text, scope, type, priority)
```

| Priority | Bedeutung | Beispiele |
|:--------:|-----------|-----------|
| 9-10 | Kritisch | Architektur-Entscheidungen, Security-Fixes |
| 7-8 | Wichtig | Feature-Entscheidungen, Bug-Fixes |
| 5-6 | Normal | Implementierungs-Details, Konfigurationen |
| 3-4 | Niedrig | Temporaere Notizen, Debug-Infos |
| 1-2 | Vergaenglich | Session-spezifische Beobachtungen |

Default: Auto nach Type (Entscheidung=9, Fakt=7, Praeferenz=6, Fehler=8, Todo=5)

## Agenten-System — 10 Rollen

| Nr | Agent | Hierarchie | Modell | Hauptaufgabe |
|:--:|-------|:----------:|--------|-------------|
| 1 | BERATER | 10 | Opus | Orchestrator — einziger Nutzer-Kontakt, Task-Queue |
| 2 | ARCHITEKT | 9 | Opus | System-Design, Struktur, Veto-Recht |
| 3 | CODER | 7 | Sonnet/Opus | Implementierung, Refactoring |
| 4 | TESTER | 6 | Sonnet/Opus | Tests schreiben + ausfuehren, Debugging |
| 5 | REVIEWER | 5 | Sonnet/Opus | Code pruefen, Fehler fixen, Commit + Push |
| 6 | DESIGNER | 4 | Sonnet/Opus | UI/UX, Frontend, Design-System |
| 7 | ANALYST | 3 | Sonnet/Opus | Repos analysieren, vergleichen, Merges |
| 8 | DOC-SCANNER | 2 | Haiku/Sonnet | Web-Dokumentationen scannen + importieren |
| 9 | DEVOPS | 2 | Sonnet/Opus | CI/CD, Server, Deploy, Rollback |
| 10 | DOKUMENTIERER | 1 | Haiku/Sonnet | Automatische Dokumentation |

### Conflict Resolution

Bei widersprüchlichen Anweisungen gilt die Hierarchie:
```
Berater (10) > Architekt (9) > Coder (7) > Tester (6) >
Reviewer (5) > Designer (4) > Analyst (3) > Doc-Scanner (2) >
DevOps (2) > Dokumentierer (1)

Bei gleicher Ebene: Juengster Eintrag gewinnt
Unloesbar: Automatische Blocker-Frage an Admin/Supervisor
```

## Kommunikation — Event-Bus

Agenten kommunizieren ueber Redis Pub/Sub:

| Channel | Zweck | Beispiel |
|---------|-------|---------|
| `bugs` | Fehler melden | Tester findet Bug → Coder reagiert |
| `decisions` | Entscheidungen teilen | Architekt entscheidet → alle informiert |
| `progress` | Fortschritt melden | Coder fertig → Tester startet |
| `blocker` | Blockaden eskalieren | Agent blockiert → Berater greift ein |

## Sicherheitsregeln

- **KEINE** Secrets/Passwoerter in Code oder Commits
- **KEIN** `rm -rf /`, `DROP TABLE`, `--force` auf main/master
- **KEIN** force-push ohne explizite Admin-Freigabe
- **IMMER** Branches fuer Features, nie direkt auf main
- **IMMER** Tests vor Commit (Tester-Agent prueft)
- **IMMER** Review vor Push (Reviewer-Agent prueft)

## Datenbank-Konfiguration

Siehe `config/databases.yaml` fuer Verbindungs-Details.
Siehe `config/core-memory.json` fuer Core Memory Template.

## Hooks

17 automatische Hooks steuern das Brain-System:
- **SessionStart:** Core Memory laden, Warm-Up Bundle
- **UserPromptSubmit:** Auto-Recall (relevante Erinnerungen suchen)
- **PreToolUse:** Sicherheits-Check (Write/Edit/Bash)
- **PostToolUse:** Output-Logging, Fehler-Tracking
- **Stop:** Auto-Capture (neue Fakten speichern)
- **SessionEnd:** Konversation in Recall Memory (S6) speichern
- **PreCompact:** Kontext-Sicherung vor Kompaktierung

Konfiguration: `.claude/settings.json`
