# USER-MANUAL DETAIL — Admin-Version

## Cloud Code Team 02.26

**Version:** 1.0.0
**Rolle:** Administrator (Vollzugriff)
**Stand:** 2026-02-17

---

## INHALTSVERZEICHNIS

| Kapitel | Titel | Seite |
|---------|-------|:-----:|
| 1 | Systemuebersicht | 3 |
| 2 | Agenten | 5 |
| 2.1 | Berater (Orchestrator) | 5 |
| 2.2 | Architekt | 8 |
| 2.3 | Coder | 10 |
| 2.4 | Tester + Debugger | 12 |
| 2.5 | Reviewer | 14 |
| 2.6 | Designer | 16 |
| 2.7 | Analyst | 18 |
| 2.8 | Doc-Scanner | 20 |
| 2.9 | DevOps | 22 |
| 2.10 | Dokumentierer | 24 |
| 3 | Hooks | 26 |
| 4 | Gehirn-System (6-Schichten) | 30 |
| 4.0 | Core Memory (Schicht 1) | 30 |
| 4.1 | Auto-Recall + Auto-Capture (Schicht 2) | 32 |
| 4.2 | HippoRAG 2 (Schicht 3) | 34 |
| 4.3 | Agentic RAG (Schicht 4) | 36 |
| 4.4 | Agentic Learning Graphs (Schicht 5) | 38 |
| 4.5 | Recall Memory (Schicht 6) | 40 |
| 5 | Profil-System | 44 |
| 6 | Fragenkatalog | 46 |
| 7 | Multi-Model Routing | 48 |
| 8 | Kommunikation | 49 |
| 9 | Connectoren + MCP | 51 |
| 10 | Web-Scanner | 53 |
| 11 | Datenbanken | 57 |
| 12 | Funktions-Registry | 60 |
| 13 | Endpoint-Registry | 64 |
| 14 | Einstellungen | 67 |
| 15 | Administration | 72 |
| 16 | Fehlerbehebung | 77 |
| A | Anhang: Alle Commands | 80 |
| B | Anhang: Alle Rules | 83 |
| C | Anhang: Alle Hook-Konfigurationen | 86 |

> **Verwandte Dokumente:**
> Ersteinrichtung → 04-INSTALLATIONS-GUIDE.md | Detaillierte Einstellungen → 03-SETUP-ANLEITUNG.md | Kurzanleitung → 06-USER-MANUAL-KURZ-ADMIN.md

---

## Seite 3 — Kapitel 1: Systemuebersicht

### 1.1 Was ist das Cloud Code Team?

Ein autonomes Multi-Agent-System bestehend aus 10 spezialisierten KI-Agenten die koordiniert zusammenarbeiten. Das System wird von einem Berater-Agenten orchestriert und nutzt ein 6-schichtiges Gehirn-System fuer persistentes Gedaechtnis.

### 1.2 Komponenten

| Komponente | Anzahl | Funktion |
|-----------|:------:|----------|
| Agenten | 10 | Spezialisierte Arbeiter |
| Hooks | 17 | Automatische Qualitaets- und Sicherheits-Kontrolle |
| Datenbanken | 4 | Neo4j (Graph), Qdrant (Vektor), Redis (Cache), PostgreSQL/SQLite (Recall Memory) |
| MCP-Server | 4+ | RAG-API, Doc-Scanner, GitHub, Notion |
| Kommunikation | 4 | Terminal, Slack, WhatsApp, Linear |

### 1.3 Architektur-Diagramm

```
Nutzer → [Slack/WhatsApp/Linear/Terminal]
           │
           ▼
         BERATER ──► Task-Queue
           │
    ┌──────┼──────────────────────┐
    ▼      ▼      ▼      ▼       ▼
 ARCHITEKT CODER DESIGNER ANALYST DEVOPS
    │      │      │       │       │
    └──────┴──────┴───────┴───────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
 TESTER REVIEWER DOC-SCANNER
           │
           ▼
    HOOKS (17x automatisch)
           │
           ▼
    GEHIRN (6 Schichten: Core Memory → Auto-Recall → HippoRAG 2 → Agentic RAG → Learning Graphs → Recall Memory)
```

---

## Seite 5 — Kapitel 2: Agenten

### 2.1 Berater (Orchestrator)

**ID:** AGT-001
**Modell-Default:** Opus
**Rolle:** Einziger Kontakt zum Nutzer, koordiniert alle Agenten

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-001 | Briefing starten | Strukturiertes Briefing mit Rueckfragen an den Nutzer | Nutzer-Eingabe (Text) | Frageliste + Zusammenfassung |
| FN-002 | Komplexitaet bewerten | Bewertet Task-Komplexitaet 1-3, weist Modell zu | Task-Beschreibung | Stufe (1-3) + Modell (Haiku/Sonnet/Opus) |
| FN-003 | Task-Queue erstellen | Erstellt priorisierte Aufgabenliste | Briefing-Ergebnis | Sortierte Task-Liste mit Abhaengigkeiten |
| FN-004 | Agent zuweisen | Weist Task an spezifischen Agent mit Modell-Stufe | Task + Agent-Name + Stufe | Bestaetigung + Agent-Status |
| FN-005 | Fortschritt melden | Sendet Status-Update an Nutzer | Meilenstein-Info | Notification (Slack/WhatsApp) |
| FN-006 | Fragenkatalog verwalten | Schreibt/liest Fragen im Katalog | Frage + Optionen + Prio | Katalog-Eintrag |
| FN-007 | Fallback ausfuehren | Weist Task an anderen Agent wenn einer versagt | Fehlgeschlagener Task + Grund | Neuer Agent-Zuweisung |
| FN-008 | Alle stoppen | Stoppt alle Agenten sofort | — | Bestaetigung |

#### Commands

| Command | FN-ID | Syntax | Beispiel |
|---------|-------|--------|---------|
| `/briefing` | FN-001 | `/briefing` | `/briefing` |
| `/plan` | FN-002 | `/plan` | `/plan` |
| `/delegate` | FN-004 | `/delegate AGENT TASK` | `/delegate coder "Login-Seite bauen"` |
| `/katalog` | FN-006 | `/katalog [filter]` | `/katalog blocker` |
| `/fortschritt` | FN-005 | `/fortschritt` | `/fortschritt` |
| `/stop-alle` | FN-008 | `/stop-alle` | `/stop-alle` |
| `/weiter` | FN-060 | `/weiter` | `/weiter` |

#### Rules

| Rule-ID | Rule | Prioritaet |
|---------|------|:----------:|
| R-01-01 | Einziger Kontakt zum Nutzer | Kritisch |
| R-01-02 | Rueckfragen bei Unklarheiten — nie raten | Kritisch |
| R-01-03 | Komplexitaet bewerten + Modell zuweisen | Hoch |
| R-01-04 | Task-Queue mit Prioritaet erstellen | Hoch |
| R-01-05 | Proaktiv zuweisen — nie warten | Kritisch |
| R-01-06 | Kein Agent ohne Freigabe | Kritisch |
| R-01-07 | Blocker sofort an Nutzer | Kritisch |
| R-01-08 | Nicht-Blocker in Katalog | Hoch |
| R-01-09 | Fortschritt bei Meilensteinen melden | Mittel |
| R-01-10 | Alle Fragen vor Start stellen | Hoch |
| R-01-11 | Fallback bei Agent-Versagen | Hoch |

#### Einstellungen

| Einstellung | Default | Optionen | Beschreibung |
|------------|---------|----------|-------------|
| `model` | opus | haiku, sonnet, opus | Standard-Modell |
| `auto_delegate` | true | true, false | Automatisch zuweisen oder manuell |
| `notification_channel` | slack | slack, whatsapp, linear, all | Bevorzugter Benachrichtigungskanal |
| `max_parallel_agents` | 4 | 1-10 | Maximale parallele Agenten |
| `question_threshold` | 3 | 1-10 | Ab wie vielen offenen Fragen Notification |

---

### 2.2 Architekt

**ID:** AGT-002
**Modell-Default:** Opus
**Rolle:** System-Design, Struktur, Veto-Recht

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-009 | Design erstellen | System-Design fuer neues Feature | Anforderungen | Design-Dokument + Diagramm |
| FN-010 | Veto ausueben | Design blockieren mit Begruendung | Design-Vorschlag | Veto + Begruendung + Alternative |
| FN-011 | Abhaengigkeiten mappen | Abhaengigkeits-Graph erstellen | Feature/Modul | Graph (Nodes + Edges) |
| FN-012 | ADR schreiben | Architecture Decision Record | Entscheidung + Kontext | ADR-Dokument in DB |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/design` | FN-009 | `/design BESCHREIBUNG` |
| `/veto` | FN-010 | `/veto BEGRUENDUNG` |
| `/deps` | FN-011 | `/deps MODUL` |
| `/adr` | FN-012 | `/adr TITEL` |

---

### 2.3 Coder

**ID:** AGT-003
**Modell-Default:** Sonnet (Standard), Opus (komplex)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-013 | Implementieren | Code schreiben nach Anweisung | Task + Architektur-Vorgabe | Code + FN-IDs registriert |
| FN-014 | Refactoren | Code ueberarbeiten nach Feedback | Review-Feedback | Refactored Code |
| FN-015 | Code pruefen | Anweisung gegen bestehenden Code pruefen | Anweisung + Codebase | Fit/Nicht-Fit + Begruendung |
| FN-016 | Funktion registrieren | Neue Funktion in Registry eintragen | Funktionsname + Details | FN-ID |
| FN-017 | Endpoint registrieren | Neuen Endpoint in Registry eintragen | Endpoint + Details | EP-ID |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/implement` | FN-013 | `/implement TASK` |
| `/refactor` | FN-014 | `/refactor FEEDBACK` |
| `/check` | FN-015 | `/check ANWEISUNG` |
| `/register` | FN-016/017 | `/register fn FUNKTIONSNAME` oder `/register ep ENDPOINT` |
| `/templates` | — | `/templates [SPRACHE]` |

---

### 2.4 Tester + Debugger

**ID:** AGT-004
**Modell-Default:** Sonnet (Tests), Opus (komplexe Bugs)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-018 | Tests schreiben | Unit/Integration Tests erstellen | Code + Anforderungen | Test-Dateien |
| FN-019 | Tests ausfuehren | Alle Tests laufen lassen | Test-Pfad | Ergebnis (Pass/Fail + Details) |
| FN-020 | Debuggen | Root-Cause Analyse bei Fehler | Fehlerbeschreibung + Code | Root-Cause + Fix-Vorschlag |
| FN-021 | Coverage messen | Test-Abdeckung berechnen | Projekt-Pfad | Coverage-Report (%) |
| FN-022 | Regression testen | Regressions-Tests nach Fix | Fix-Beschreibung | Regressions-Report |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/test` | FN-019 | `/test [PFAD]` |
| `/debug` | FN-020 | `/debug FEHLERBESCHREIBUNG` |
| `/coverage` | FN-021 | `/coverage` |
| `/regression` | FN-022 | `/regression` |

> **Hinweis:** FN-018 (Tests schreiben) wird automatisch vom Tester-Agent ausgefuehrt (kein manueller Command).

---

### 2.5 Reviewer

**ID:** AGT-005
**Modell-Default:** Sonnet (Standard), Opus (Architektur-Review)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-023 | Code reviewen | Code-Qualitaet pruefen | Code-Diff | Review-Ergebnis + Kommentare |
| FN-024 | Auto-Fix | Kleine Fehler selbst korrigieren | Review-Befund | Korrigierter Code |
| FN-025 | Commit + Push | Code committen und pushen | Dateien + Message | Commit-Hash + Push-Status |
| FN-026 | Changelog erstellen | Aenderungs-Eintrag generieren | Commit-Info | Changelog-Eintrag |
| FN-027 | Repo konfigurieren | Repo-URL beim ersten Mal setzen | Repo-URL | Bestaetigung |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/review` | FN-023 | `/review` |
| `/commit` | FN-025 | `/commit [MESSAGE]` |
| `/repo` | FN-027 | `/repo URL` |
| `/changelog` | FN-026 | `/changelog` |

> **Hinweis:** FN-024 (Auto-Fix) wird automatisch vom Reviewer-Agent ausgefuehrt (kein manueller Command).

---

### 2.6 Designer

**ID:** AGT-006
**Modell-Default:** Sonnet (Komponenten), Opus (Design-System)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-028 | UI erstellen | Frontend-Komponente designen + bauen | Anforderungen | Komponente + Styling |
| FN-029 | Design-System | Tokens/Theme verwalten | Token-Name + Wert | Aktualisiertes Theme |
| FN-030 | Responsive Check | Responsive-Verhalten pruefen | Komponente | Report (Breakpoints) |
| FN-031 | a11y Check | Accessibility pruefen | Komponente | WCAG-Report |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/design-ui` | FN-028 | `/design-ui BESCHREIBUNG` |
| `/theme` | FN-029 | `/theme [show\|set KEY VALUE]` |
| `/responsive` | FN-030 | `/responsive KOMPONENTE` |
| `/a11y` | FN-031 | `/a11y KOMPONENTE` |

---

### 2.7 Analyst

**ID:** AGT-007
**Modell-Default:** Sonnet (Analyse), Opus (komplexe Vergleiche)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-032 | Repo analysieren | Tiefgehende Inhaltsanalyse | Repo-URL/Pfad | Analyse-Report (Funktionen, Klassen, Deps) |
| FN-033 | Repos vergleichen | Zwei Repos inhaltlich vergleichen | Repo-A + Repo-B | Vergleichs-Report (Ueberschneidungen, Unique) |
| FN-034 | Merge planen | Merge-Strategie vorschlagen | Repo-A + Repo-B | Merge-Plan mit Konflikten |
| FN-035 | Dependency Map | Abhaengigkeits-Karte erstellen | Repo-Pfad | Visueller Dependency-Graph |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/analyze` | FN-032 | `/analyze REPO` |
| `/compare` | FN-033 | `/compare REPO-A REPO-B` |
| `/merge-plan` | FN-034 | `/merge-plan REPO-A REPO-B` |
| `/deps-map` | FN-035 | `/deps-map REPO` |

---

### 2.8 Doc-Scanner

**ID:** AGT-008
**Modell-Default:** Haiku (Routine), Sonnet (komplexe Docs)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-036 | URL scannen | Webseite scannen + in DB importieren | URL | Scan-Ergebnis (Entitaeten, Beziehungen) |
| FN-037 | URL-Liste verwalten | Ueberwachte URLs anzeigen/aendern | — | URL-Liste mit Status |
| FN-038 | URL hinzufuegen | Neue URL zur Ueberwachung | URL + Scope (Global/Projekt) | Bestaetigung |
| FN-039 | Diff anzeigen | Aenderungen seit letztem Scan | URL | Diff-Report |
| FN-040 | KB importieren | Lokale Docs in KB importieren | Pfad + Scope | Import-Report |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/scan` | FN-036 | `/scan URL` |
| `/scan-list` | FN-037 | `/scan-list` |
| `/scan-add` | FN-038 | `/scan-add URL [global\|projekt]` |
| `/scan-diff` | FN-039 | `/scan-diff URL` |
| `/kb-import` | FN-040 | `/kb-import PFAD [global\|projekt]` |

---

### 2.9 DevOps

**ID:** AGT-009
**Modell-Default:** Sonnet (Standard), Opus (Infrastruktur)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-041 | Deployen | Deployment auf Staging/Production | Target (staging/prod) | Deploy-Status |
| FN-042 | Env verwalten | Environment-Variablen setzen/lesen | Key + Value | Bestaetigung |
| FN-043 | CI/CD verwalten | Pipeline anzeigen/aendern | Pipeline-Config | Aktualisierte Pipeline |
| FN-044 | Health-Check | Server-Gesundheit pruefen | — | Health-Report aller Services |
| FN-045 | Rollback | Letztes Deployment zurueckrollen | — | Rollback-Bestaetigung |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/deploy` | FN-041 | `/deploy [staging\|prod]` |
| `/env` | FN-042 | `/env [list\|set KEY VALUE\|get KEY]` |
| `/ci` | FN-043 | `/ci [show\|edit]` |
| `/health` | FN-044 | `/health` |
| `/rollback` | FN-045 | `/rollback` |

---

### 2.10 Dokumentierer (Hybrid)

**ID:** AGT-010
**Modell-Default:** Haiku (Tool-generiert), Sonnet (Verfeinerung)

#### Funktionen

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-046 | Auto-Docs | Docs ueber Tools generieren (TypeDoc, Swagger) | Projekt-Pfad | Generierte Docs |
| FN-047 | Docs verfeinern | Tool-Docs manuell verbessern | Doc-Pfad + Kontext | Verfeinerte Docs |
| FN-048 | Registry fuehren | Funktions- + Endpoint-Registry pflegen | — | Aktuelle Registry |
| FN-049 | Manual erstellen | User-Manual generieren | Rolle (Admin/Supervisor/Worker) | Manual-Dokument |
| FN-050 | API-Docs | Swagger/OpenAPI generieren | API-Pfad | OpenAPI Spec |

#### Commands

| Command | FN-ID | Syntax |
|---------|-------|--------|
| `/docs` | FN-046 | `/docs [generate\|update]` |
| `/docs-refine` | FN-047 | `/docs-refine PFAD` |
| `/registry` | FN-048 | `/registry [fn\|ep\|all]` |
| `/manual` | FN-049 | `/manual [admin\|supervisor\|worker]` |
| `/api-docs` | FN-050 | `/api-docs` |

---

## Seite 26 — Kapitel 3: Hooks

### 3.1 Hook-Uebersicht

| Hook-ID | Hook | Matcher | Typ | Blockierend | Beschreibung |
|---------|------|---------|-----|:-----------:|-------------|
| H-01 | SessionStart | startup | command | Nein | Kontext aus HippoRAG 2 laden |
| H-02 | SessionStart | compact | command | Nein | Profile neu laden nach Komprimierung |
| H-03 | SessionStart | resume | command | Nein | Letzten Stand aus DB laden |
| H-04 | UserPromptSubmit | — | command | Ja | Eingabe an Berater routen |
| H-05 | PreToolUse | Write\|Edit | agent | Ja | Security-Check vor Code-Aenderung |
| H-06 | PreToolUse | Bash | agent | Ja | Gefaehrliche Befehle blockieren |
| H-07 | PostToolUse | Write\|Edit | command | Nein | Regeln erzwingen + Doc-Tools |
| H-08 | PostToolUse | Bash | command | Nein | Ergebnis pruefen + DB speichern |
| H-09 | PostToolUseFailure | — | command | Nein | Fehler analysieren |
| H-10 | PreCompact | — | command | Nein | Kontext in DB sichern |
| H-11 | Stop | — | agent | Ja | Tasks-Erledigung verifizieren |
| H-12 | SubagentStart | — | command | Nein | Kontext + Profile injizieren |
| H-13 | SubagentStop | — | agent | Ja | Qualitaets-Check |
| H-14 | Notification | — | command | Nein | Slack/WhatsApp senden |
| H-15 | TeammateIdle | — | agent | Ja | Quality-Gate vor Pause |
| H-16 | TaskCompleted | — | agent | Ja | Task-Erledigung verifizieren |
| H-17 | SessionEnd | — | command | Nein | Session-Summary in DB |

### 3.2 Hook-Konfiguration

Alle Hooks werden in `~/.claude/settings.json` konfiguriert. Vollstaendige Konfiguration siehe Anhang C.

### 3.3 Hook-Einstellungen

| Einstellung | Beschreibung | Default |
|------------|-------------|---------|
| `timeout` | Max. Ausfuehrungszeit in ms | 10000 (command), 30000 (agent) |
| `matcher` | Regex-Pattern fuer Filter | Tool-Name oder Event-Typ |
| `type` | Hook-Typ | command, prompt, agent |
| `async` | Asynchron ausfuehren | false |

---

## Seite 30 — Kapitel 4: Gehirn-System (6-Schichten)

Das Gehirn-System besteht aus 6 Schichten, die zusammen ein vollstaendiges Gedaechtnis bilden:

```
┌─────────────────────────────────────────────────────────┐
│ Schicht 1 — Core Memory          (immer im Kontext)     │
│ Schicht 2 — Auto-Recall/Capture  (automatisch injiziert) │
│ Schicht 3 — HippoRAG 2           (Graph + Vektoren)     │
│ Schicht 4 — Agentic RAG          (intelligente Suche)    │
│ Schicht 5 — Learning Graphs      (selbstlernendes Netz)  │
│ Schicht 6 — Recall Memory        (rohe Konversationen)   │
└─────────────────────────────────────────────────────────┘
```

### 4.0 Core Memory (Schicht 1)

**Was es ist:** ~20.000 Zeichen die permanent im Kontextfenster gepinnt sind. Das Core Memory ist das Kurzzeitgedaechtnis des Systems — immer sichtbar, immer verfuegbar, ohne Suche.

**5 Bloecke:**

| Block | Label | Limit | Beschreibung |
|-------|-------|:-----:|-------------|
| 1 | USER | 4.000 Zeichen | Wer ist der Nutzer? Praeferenzen, Stil, Rolle |
| 2 | PROJEKT | 4.000 Zeichen | Aktuelles Projekt, Tech-Stack, Ziele |
| 3 | ENTSCHEIDUNGEN | 4.000 Zeichen | Wichtige Architektur- und Design-Entscheidungen |
| 4 | FEHLER-LOG | 4.000 Zeichen | Bekannte Fehler, Workarounds, Lessons Learned |
| 5 | AKTUELLE-ARBEIT | 4.000 Zeichen | Was wird gerade gemacht? Offene Tasks, Kontext |

**Datenstruktur (core-memory.json):**

```json
{
  "blocks": {
    "USER": {
      "label": "USER",
      "limit": 4000,
      "value": "Name: Max. Rolle: Senior Dev. Praeferenz: TypeScript, kurze Antworten."
    },
    "PROJEKT": {
      "label": "PROJEKT",
      "limit": 4000,
      "value": "E-Commerce App. Stack: Next.js 15, Prisma, PostgreSQL. Ziel: MVP bis Maerz."
    },
    "ENTSCHEIDUNGEN": {
      "label": "ENTSCHEIDUNGEN",
      "limit": 4000,
      "value": "ADR-001: App Router statt Pages Router. ADR-002: Prisma statt Drizzle."
    },
    "FEHLER-LOG": {
      "label": "FEHLER-LOG",
      "limit": 4000,
      "value": "BUG-012: Hydration Mismatch bei dynamischem Import — Workaround: next/dynamic mit ssr:false."
    },
    "AKTUELLE-ARBEIT": {
      "label": "AKTUELLE-ARBEIT",
      "limit": 4000,
      "value": "Feature: Warenkorb. Task: Checkout-Flow implementieren. Blocker: Payment-API Zugang fehlt."
    }
  }
}
```

**So sieht es im Kontextfenster aus:**

```
═══════════════════════════════════════════════════
 CORE MEMORY (gepinnt — immer sichtbar)
═══════════════════════════════════════════════════
[USER] (312/4000 Zeichen)
Name: Max. Rolle: Senior Dev. Praeferenz: TypeScript, kurze Antworten.

[PROJEKT] (487/4000 Zeichen)
E-Commerce App. Stack: Next.js 15, Prisma, PostgreSQL. Ziel: MVP bis Maerz.

[ENTSCHEIDUNGEN] (298/4000 Zeichen)
ADR-001: App Router statt Pages Router. ADR-002: Prisma statt Drizzle.

[FEHLER-LOG] (401/4000 Zeichen)
BUG-012: Hydration Mismatch bei dynamischem Import — Workaround: next/dynamic mit ssr:false.

[AKTUELLE-ARBEIT] (523/4000 Zeichen)
Feature: Warenkorb. Task: Checkout-Flow implementieren. Blocker: Payment-API Zugang fehlt.
═══════════════════════════════════════════════════
```

**Verfuegbare Commands:** `/core-read` (FN-051), `/core-update` (FN-052)

**Agent-Tools:**

| Tool | Beschreibung | Parameter | Rueckgabe |
|------|-------------|-----------|-----------|
| `core_memory_read(block)` | Einen Block lesen | Block-Name (z.B. "USER") | Block-Inhalt als Text |
| `core_memory_update(block, value)` | Einen Block aktualisieren | Block-Name + neuer Inhalt | Bestaetigung + Zeichenzahl |

**Funktions-Registry:**

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-051 | Core Memory lesen | Einen Block aus dem Core Memory lesen | Block-Name | Block-Inhalt |
| FN-052 | Core Memory aktualisieren | Einen Block im Core Memory ueberschreiben | Block-Name + neuer Wert | Bestaetigung |

**Laden:** Der SessionStart-Hook (H-01) laedt `core-memory.json` und injiziert alle 5 Bloecke an den Anfang des Kontextfensters.

**Einstellungen:**

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `max_size_chars` | 20000 | Maximale Gesamtgroesse aller Bloecke |
| `blocks` | 5 Bloecke (siehe oben) | Konfigurierbare Block-Liste mit Labels und Limits |
| `auto_pin` | true | Automatisch an Kontextfenster-Anfang pinnen |
| `persist_path` | `~/.claude/core-memory.json` | Speicherpfad der Core-Memory-Datei |

---

### 4.1 Auto-Recall + Auto-Capture (Schicht 2)

**Was es ist:** Automatisches Erinnern und Lernen — ohne manuelle Suche. Das System erinnert sich proaktiv an relevantes Wissen und speichert automatisch neue Fakten.

**Auto-Recall (Automatisches Erinnern):**

```
Nutzer tippt Nachricht
       │
       ▼
  UserPromptSubmit-Hook (H-04)
       │
       ▼
  Relevante Erinnerungen suchen
  (Embedding-Suche ueber alle gespeicherten Fakten)
       │
       ▼
  Ergebnisse in Kontext injizieren
  (vor der eigentlichen Verarbeitung)
       │
       ▼
  Agent sieht: Nutzerfrage + relevante Erinnerungen
```

- Wird bei jedem `UserPromptSubmit`-Hook automatisch ausgefuehrt
- Sucht in Long-Term Memory (nutzer-uebergreifend, alle Sessions) und Short-Term Memory (session-spezifisch)
- Injiziert gefundene Erinnerungen direkt in den Kontext
- Ueberlebt Komprimierung — wird bei jedem Turn frisch injiziert

**Auto-Capture (Automatisches Speichern):**

```
Agent beendet Antwort
       │
       ▼
  Stop-Hook (H-11)
       │
       ▼
  Neue Fakten aus Konversation extrahieren
  (Entscheidungen, Praeferenzen, Fehler, Loesungen)
       │
       ▼
  In Memory-Datenbank speichern
  (Long-Term oder Short-Term je nach Scope)
```

- Wird bei jedem `Stop`-Hook automatisch ausgefuehrt
- Extrahiert neue Fakten, Entscheidungen, Praeferenzen aus der Konversation
- Speichert in Long-Term (nutzer-spezifisch, alle Sessions) oder Short-Term (nur aktuelle Session)

**Scopes:**

| Scope | Lebensdauer | Sichtbarkeit | Beispiel |
|-------|-------------|-------------|---------|
| Long-Term | Permanent (nutzer-uebergreifend) | Alle Sessions, alle Projekte | "Nutzer bevorzugt TypeScript" |
| Short-Term | Nur aktuelle Session | Nur diese Session | "Arbeiten gerade an der Login-Seite" |

**Verfuegbare Commands:** `/memory-search` (FN-053), `/memory-store` (FN-054), `/memory-list` (FN-055), `/memory-get` (FN-056), `/memory-forget` (FN-057)

**Agent-Tools:**

| Tool | Beschreibung | Parameter | Rueckgabe |
|------|-------------|-----------|-----------|
| `memory_search(query)` | Erinnerungen durchsuchen | Suchbegriff (Text) | Liste relevanter Erinnerungen |
| `memory_store(content, scope)` | Neue Erinnerung speichern | Inhalt + Scope (long/short) | Bestaetigung + Memory-ID |
| `memory_list(scope)` | Alle Erinnerungen auflisten | Scope (long/short/all) | Liste aller Erinnerungen |
| `memory_get(id)` | Einzelne Erinnerung abrufen | Memory-ID | Erinnerungs-Inhalt |
| `memory_forget(id)` | Erinnerung loeschen | Memory-ID | Bestaetigung |

**Funktions-Registry:**

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-053 | Memory durchsuchen | Erinnerungen per Suche finden | Suchbegriff | Ergebnisliste |
| FN-054 | Memory speichern | Neue Erinnerung ablegen | Inhalt + Scope | Memory-ID |
| FN-055 | Memory auflisten | Alle Erinnerungen zeigen | Scope-Filter | Liste |
| FN-056 | Memory abrufen | Einzelne Erinnerung lesen | Memory-ID | Inhalt |
| FN-057 | Memory loeschen | Erinnerung entfernen | Memory-ID | Bestaetigung |

**Einstellungen:**

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `auto_recall` | true | Automatisches Erinnern bei jedem Prompt |
| `auto_capture` | true | Automatisches Speichern nach jeder Antwort |
| `long_term_scope` | user | Scope fuer Long-Term Memory (user = nutzer-spezifisch) |
| `short_term_scope` | session | Scope fuer Short-Term Memory (session = nur aktuelle Session) |
| `max_recall_results` | 5 | Maximale Anzahl injizierter Erinnerungen pro Turn |
| `capture_threshold` | 0.6 | Mindest-Relevanz fuer automatisches Speichern |

---

### 4.2 HippoRAG 2 (Schicht 3)

**Komponenten:** Neo4j (Graph) + Qdrant (Vektoren) + PageRank

**Wie es funktioniert:**
1. Neues Wissen kommt rein (Code, Entscheidungen, Docs)
2. Entity-Extraktion: Entitaeten + Beziehungen erkennen
3. Graph-Update: Neue Knoten + Kanten in Neo4j
4. Embedding: Vektor-Repraesentation in Qdrant
5. Bei Abfrage: PageRank bewertet Relevanz + Graph-Traversierung

**Einstellungen:**

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `embedding_model` | all-MiniLM-L6-v2 | Lokales Embedding-Modell |
| `pagerank_damping` | 0.85 | PageRank Daempfungsfaktor |
| `pagerank_iterations` | 100 | Max. Iterationen |
| `similarity_threshold` | 0.7 | Min. Aehnlichkeit fuer Ergebnisse |
| `max_results` | 10 | Max. Ergebnisse pro Abfrage |

### 4.3 Agentic RAG (Schicht 4)

Steuert die Suchstrategie intelligent:
- Entscheidet ob Suche noetig ist
- Waehlt Suchstrategie (Graph, Vektor, Hybrid)
- Bewertet Ergebnis-Qualitaet
- Korrigiert bei schlechten Ergebnissen

### 4.4 Agentic Learning Graphs (Schicht 5)

Erweitert das Wissensnetz automatisch:
- Jede Interaktion kann neue Knoten/Kanten erzeugen
- Graph waechst mit jeder Session
- Naechste Abfrage profitiert von vorherigem Wissen

---

### 4.5 Recall Memory (Schicht 6)

**Was es ist:** Vollstaendige, rohe Konversationshistorie. Jede Nachricht, jeder Tool-Aufruf, jede Antwort — alles wird mit Zeitstempel gespeichert. Nichts geht jemals verloren.

**Wie es funktioniert:**

```
Session laeuft (Nachrichten, Tool-Calls, Antworten)
       │
       ▼
  Alles wird mitprotokolliert
  (Jede Nachricht + Zeitstempel + Metadaten)
       │
       ▼
  SessionEnd-Hook (H-17)
       │
       ▼
  Komplette Session in Datenbank speichern
  (Strukturiert, durchsuchbar, permanent)
```

- Automatische Speicherung bei jedem `SessionEnd`-Hook (H-17)
- Jede Nachricht enthaelt: Absender, Inhalt, Zeitstempel, Tool-Name (falls Tool-Call), Antwort
- Ermoeglicht rueckwirkende Suche ueber alle vergangenen Konversationen
- Keine manuelle Aktion noetig — laeuft vollstaendig im Hintergrund

**Was gespeichert wird:**

| Feld | Beschreibung | Beispiel |
|------|-------------|---------|
| `session_id` | Eindeutige Session-ID | `sess_2026-02-17_14-30` |
| `timestamp` | Zeitstempel jeder Nachricht | `2026-02-17T14:32:05Z` |
| `role` | Absender (user, assistant, tool) | `user` |
| `content` | Nachrichteninhalt | "Baue eine Login-Seite" |
| `tool_name` | Tool-Name (bei Tool-Calls) | `Write` |
| `tool_input` | Tool-Parameter | `{"file_path": "..."}` |
| `tool_output` | Tool-Ergebnis | `"Datei erstellt"` |

**Verfuegbare Commands:** `/conv-search` (FN-058), `/conv-search-date` (FN-059)

**Agent-Tools:**

| Tool | Beschreibung | Parameter | Rueckgabe |
|------|-------------|-----------|-----------|
| `conversation_search(query)` | Freitext-Suche ueber alle Konversationen | Suchbegriff (Text) | Liste passender Nachrichten mit Kontext |
| `conversation_search_date(from, to)` | Konversationen nach Zeitraum suchen | Startdatum + Enddatum | Alle Nachrichten im Zeitraum |

**Funktions-Registry:**

| FN-ID | Funktion | Beschreibung | Parameter | Rueckgabe |
|-------|----------|-------------|-----------|-----------|
| FN-058 | Konversation suchen | Freitext-Suche in Konversationshistorie | Suchbegriff | Ergebnisliste mit Kontext |
| FN-059 | Konversation nach Datum | Konversationen in Zeitraum finden | Von-Datum + Bis-Datum | Nachrichten im Zeitraum |

**Einstellungen:**

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `auto_store` | true | Automatisch bei SessionEnd speichern |
| `store_tool_calls` | true | Tool-Aufrufe mitspeichern |
| `max_search_results` | 20 | Max. Ergebnisse bei Konversationssuche |
| `retention_days` | 365 | Aufbewahrungsdauer in Tagen (0 = unbegrenzt) |

---

## Seite 44 — Kapitel 5: Profil-System

### 5.1 Wie Profile funktionieren

```
Skill-Datei unter ~/.claude/skills/PROFILNAME/SKILL.md
  → Wird nur geladen wenn aktiviert
  → Hooks erzwingen Regeln ausserhalb des Kontexts
  → Auto-Reload nach Komprimierung
```

### 5.2 Profil verwalten

| Aktion | Command | Beispiel |
|--------|---------|---------|
| Laden | `/profil-laden NAME` | `/profil-laden python-regeln` |
| Auflisten | `/profil` | `/profil` |
| Deaktivieren | `/profil-laden --remove NAME` | `/profil-laden --remove python-regeln` |

### 5.3 Eigenes Profil erstellen

```bash
mkdir -p ~/.claude/skills/mein-profil
cat > ~/.claude/skills/mein-profil/SKILL.md << 'EOF'
---
name: "mein-profil"
description: "Beschreibung"
---
# Regeln
- ...
EOF
```

---

## Seite 46 — Kapitel 6: Fragenkatalog

### 6.1 Fragen-Typen

| Typ | Symbol | Agent stoppt? | Notification? |
|-----|:------:|:------------:|:------------:|
| Blocker | BLOCKER | Ja | Sofort |
| Offen | OFFEN | Nein | Bei Schwelle |
| Beantwortet | ERLEDIGT | — | — |

### 6.2 Fragenkatalog einsehen

| Command | Was |
|---------|-----|
| `/katalog` | Alle offenen Fragen |
| `/katalog blocker` | Nur Blocker |
| `/katalog offen` | Nur offene |
| `/katalog beantwortet` | Archiv |

---

## Seite 48 — Kapitel 7: Multi-Model Routing

| Stufe | Modell | Trigger | Kosten-Faktor |
|-------|--------|---------|:-------------:|
| 1 | Haiku | Einfache Tasks | 5% |
| 2 | Sonnet | Standard-Tasks | 30% |
| 3 | Opus | Komplexe Tasks | 100% |

**Fallback-Kette:** Opus → Sonnet → Haiku (bei Rate-Limit)

**Einstellungen:**

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `default_model` | sonnet | Standard wenn nicht anders zugewiesen |
| `auto_routing` | true | Berater weist automatisch zu |
| `fallback_enabled` | true | Automatischer Fallback bei Rate-Limit |

---

## Seite 49 — Kapitel 8: Kommunikation

### 8.1 Kanael-Einstellungen

| Kanal | Config-Key | Einrichtung |
|-------|-----------|------------|
| Terminal | — | Standard, immer verfuegbar |
| Slack | `slack.webhook_url` | Webhook URL in communication.json |
| WhatsApp | `whatsapp.token` | Meta Business API Token |
| Linear | `linear.api_key` | Linear API Key |

### 8.2 Notification-Einstellungen

| Einstellung | Default | Optionen |
|------------|---------|----------|
| `default_channel` | slack | slack, whatsapp, linear, all |
| `notify_on` | blocker, fertig | blocker, fertig, fehler, meilenstein, frage |
| `quiet_hours` | null | "22:00-07:00" (keine Notifications) |

---

## Seite 51 — Kapitel 9: Connectoren + MCP

### 9.1 Installierte MCP-Server

| Server | Zweck | Port |
|--------|-------|:----:|
| rag-api | Gehirn-System Zugriff | 8100 |
| doc-scanner | Web-Docs scannen | 8101 |
| github | GitHub Integration | — |
| notion | Notion Integration | — |

### 9.2 Neuen Connector hinzufuegen

```bash
# MCP-Server installieren
npm install -g @example/mcp-server-name

# In Claude Code registrieren
claude mcp add name -- npx @example/mcp-server-name

# Pruefen
claude mcp list
```

---

## Seite 53 — Kapitel 10: Web-Scanner

Der Web-Scanner ueberwacht Webseiten (Dokumentationen, APIs, Tutorials) und importiert
Aenderungen automatisch in das Gehirn-System (HippoRAG 2). So bleibt das Wissen aktuell.

### 10.1 URL hinzufuegen — Schritt fuer Schritt

#### Syntax

```bash
/scan-add URL SCOPE [--name "NAME"] [--beschreibung "TEXT"] [--tags TAG1,TAG2]
```

#### Parameter erklaert

| Parameter | Pflicht | Beschreibung |
|-----------|:-------:|-------------|
| `URL` | Ja | Die Webseite die gescannt werden soll |
| `SCOPE` | Ja | `global` = fuer alle Projekte, `projekt` = nur fuer aktuelles Projekt |
| `--name` | Nein | Kurzname fuer die URL (sonst wird Domain verwendet) |
| `--beschreibung` | Nein | Was ist auf dieser Seite? Wofuer brauchen wir sie? |
| `--tags` | Nein | Kategorien, kommagetrennt (z.B. `api,python,auth`) |

#### Global vs Projekt — Unterschied

| | Global | Projekt |
|---|--------|---------|
| **Sichtbar fuer** | Alle Projekte, alle Agenten | Nur das aktuelle Projekt |
| **Gespeichert in** | Allgemeine Wissensdatenbank | Projekt-spezifische Datenbank |
| **Beispiel** | Python-Docs, React-Docs, MDN | Deine eigene API-Doku, Projekt-Wiki |
| **Wann verwenden** | Allgemeines Wissen das ueberall gilt | Projekt-spezifisches Wissen |

#### Beispiele

```bash
# React-Dokumentation — Global, fuer alle Projekte nuetzlich
/scan-add https://react.dev/reference global \
  --name "React Docs" \
  --beschreibung "Offizielle React-Dokumentation. Hooks, Komponenten, APIs." \
  --tags react,frontend,hooks

# Eigene API-Dokumentation — Nur fuer dieses Projekt
/scan-add https://api.mein-projekt.com/docs projekt \
  --name "Mein API" \
  --beschreibung "REST API unseres Backends. Endpoints, Auth, Fehler-Codes." \
  --tags api,backend,rest

# Tailwind CSS — Global
/scan-add https://tailwindcss.com/docs global \
  --name "Tailwind" \
  --beschreibung "CSS-Framework Dokumentation. Klassen, Konfiguration." \
  --tags css,frontend,design

# Internes Wiki — Projekt-spezifisch
/scan-add https://wiki.firma.com/projekt-x projekt \
  --name "Projekt-Wiki" \
  --beschreibung "Interne Anforderungen, Entscheidungen, Architektur-Diagramme." \
  --tags intern,anforderungen
```

### 10.2 URL-Liste anzeigen und verwalten

```bash
# Alle URLs anzeigen
/scan-list

# Nur globale URLs
/scan-list --scope global

# Nur Projekt-URLs
/scan-list --scope projekt

# Nach Tag filtern
/scan-list --tag api
```

**Ausgabe-Beispiel:**

```
┌─────┬──────────────┬────────────────────────────┬─────────┬──────────────┬─────────────┐
│ #   │ Name         │ URL                        │ Scope   │ Letzter Scan │ Status      │
├─────┼──────────────┼────────────────────────────┼─────────┼──────────────┼─────────────┤
│ 1   │ React Docs   │ react.dev/reference        │ Global  │ 2026-02-10   │ Aktuell     │
│ 2   │ Mein API     │ api.mein-projekt.com/docs  │ Projekt │ 2026-02-12   │ Geaendert!  │
│ 3   │ Tailwind     │ tailwindcss.com/docs       │ Global  │ 2026-02-10   │ Aktuell     │
│ 4   │ Projekt-Wiki │ wiki.firma.com/projekt-x   │ Projekt │ 2026-02-14   │ Aktuell     │
└─────┴──────────────┴────────────────────────────┴─────────┴──────────────┴─────────────┘
Tags: react(1), frontend(2), api(2), backend(1), css(1), design(1), intern(1)
```

#### URL entfernen oder bearbeiten

```bash
# URL entfernen (nach Nummer oder Name)
/scan-remove 2
/scan-remove "Mein API"

# URL bearbeiten (Beschreibung aendern)
/scan-edit 1 --beschreibung "Neue Beschreibung hier"

# Scope aendern (von Projekt zu Global)
/scan-edit 3 --scope global
```

### 10.3 Manuell scannen

```bash
# Eine einzelne URL sofort scannen (ohne auf den Zyklus zu warten)
/scan https://react.dev/reference

# Alle URLs sofort scannen
/scan --all
```

**Was passiert beim Scan:**

```
  URL eingeben
       │
       ▼
  ┌─────────────────┐
  │ Seite abrufen    │ ← Cheerio (statisch) oder Puppeteer (JavaScript)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Inhalt parsen    │ ← Text, Code-Bloecke, Tabellen, Links extrahieren
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Mit letztem Scan │ ← Diff-Engine: Was hat sich geaendert?
  │ vergleichen      │
  └────────┬────────┘
           │
     ┌─────┴─────┐
     │            │
  Gleich      Geaendert
     │            │
     ▼            ▼
  Nichts     ┌─────────────────┐
  tun        │ In HippoRAG 2   │ ← Alte Version ersetzen
             │ importieren      │   Neue Entitaeten/Beziehungen
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Notification     │ ← Slack/WhatsApp: "React Docs geaendert!"
             │ senden           │
             └─────────────────┘
```

### 10.4 Aenderungen pruefen (Diff)

```bash
# Diff fuer eine bestimmte URL anzeigen
/scan-diff https://react.dev/reference

# Diff fuer alle geaenderten URLs
/scan-diff --all
```

**Ausgabe-Beispiel:**

```
Diff fuer: React Docs (react.dev/reference)
Letzter Scan: 2026-02-10 → Aktueller Scan: 2026-02-17

+ NEU: useActionState Hook hinzugefuegt
+ NEU: Abschnitt "Server Components" erweitert
~ GEAENDERT: useEffect — Neue Warnungen bei Dependencies
- ENTFERNT: Legacy Context API Beispiele

Importiert: 3 neue Entitaeten, 7 neue Beziehungen in HippoRAG 2
```

### 10.5 KB-Import (lokale Dateien)

Nicht nur Webseiten — auch lokale Dokumente koennen importiert werden:

```bash
# Einzelne Datei importieren
/kb-import ./docs/api-spec.yaml projekt \
  --beschreibung "OpenAPI Spezifikation unserer REST API"

# Ganzen Ordner importieren
/kb-import ./docs/ projekt \
  --beschreibung "Alle Projekt-Dokumentationen"

# PDF importieren
/kb-import ./handbuch.pdf global \
  --beschreibung "Python Best Practices Handbuch"
```

**Unterstuetzte Formate:**

| Format | Endung | Hinweis |
|--------|--------|---------|
| Markdown | `.md` | Empfohlen — beste Erkennung |
| YAML/JSON | `.yaml`, `.json` | Gut fuer API-Specs (OpenAPI, Swagger) |
| Plain Text | `.txt` | Einfacher Text |
| PDF | `.pdf` | Wird automatisch in Text konvertiert |
| HTML | `.html` | Wird geparst wie Webseiten |
| Code | `.py`, `.js`, `.ts`, etc. | Funktionen + Klassen werden extrahiert |

### 10.6 Automatischer Scan-Zyklus

Der Web-Scanner laeuft automatisch im Hintergrund:

| Einstellung | Default | Beschreibung |
|------------|---------|-------------|
| `interval_days` | 7 | Alle X Tage wird jede URL gescannt |
| `auto_import` | true | Aenderungen automatisch in HippoRAG 2 importieren |
| `notify_changes` | true | Bei Aenderungen Notification senden (Slack/WhatsApp) |
| `max_depth` | 3 | Wie tief Links auf der Seite gefolgt wird |
| `js_rendering` | true | JavaScript rendern (noetig fuer SPAs wie React-Docs) |
| `scan_time` | `03:00` | Uhrzeit wann der Cron-Job laeuft |
| `retry_on_fail` | 3 | Wie oft bei Fehler wiederholen |
| `timeout_seconds` | 30 | Max. Wartezeit pro Seite |

**Einstellungen aendern:**

```bash
# Scan-Intervall auf 3 Tage setzen
/scan-config interval_days 3

# JavaScript-Rendering ausschalten (schneller, aber manche Seiten unvollstaendig)
/scan-config js_rendering false

# Scan-Tiefe erhoehen (mehr Unterseiten)
/scan-config max_depth 5
```

### 10.7 Beispiel-Workflow: Neue Doku-Quelle einrichten

**Szenario:** Du willst die Next.js Dokumentation ueberwachen.

```
Schritt 1: URL hinzufuegen
─────────────────────────
/scan-add https://nextjs.org/docs global \
  --name "Next.js Docs" \
  --beschreibung "Next.js Framework. App Router, Server Components, API Routes." \
  --tags nextjs,react,fullstack

Schritt 2: Ersten Scan ausfuehren
──────────────────────────────────
/scan https://nextjs.org/docs
→ "Scan gestartet... 47 Seiten gefunden, 312 Entitaeten extrahiert."

Schritt 3: Pruefen was importiert wurde
────────────────────────────────────────
/scan-diff https://nextjs.org/docs
→ "Erster Scan — alles neu. 312 Entitaeten, 891 Beziehungen importiert."

Schritt 4: Testen ob Wissen verfuegbar ist
──────────────────────────────────────────
/memory "Wie funktioniert der App Router in Next.js?"
→ Agent antwortet mit Wissen aus der gescannten Dokumentation.

Schritt 5: Fertig — Ab jetzt automatisch
─────────────────────────────────────────
Alle 7 Tage wird die Seite automatisch gescannt.
Bei Aenderungen bekommst du eine Notification.
```

---

## Seite 57 — Kapitel 11: Datenbanken

### 11.1 Neo4j Administration

| Aktion | Befehl/URL |
|--------|-----------|
| Dashboard | http://IP:7474 |
| Backup | `docker exec neo4j neo4j-admin database dump neo4j` |
| Restore | `docker exec neo4j neo4j-admin database load neo4j` |
| Logs | `docker logs neo4j` |
| Neustart | `docker restart neo4j` |

### 11.2 Qdrant Administration

| Aktion | Befehl/URL |
|--------|-----------|
| Dashboard | http://IP:6333/dashboard |
| Collections | `curl http://IP:6333/collections` |
| Snapshot | `curl -X POST http://IP:6333/collections/NAME/snapshots` |
| Logs | `docker logs qdrant` |

### 11.3 Redis Administration

| Aktion | Befehl |
|--------|--------|
| Verbinden | `docker exec -it redis redis-cli -a PASSWORT` |
| Alle Keys | `KEYS *` |
| Speicher | `INFO memory` |
| Flush | `FLUSHDB` (VORSICHT!) |
| Backup | Automatisch via appendonly |

### 11.4 PostgreSQL/SQLite (Recall Memory)

**Status pruefen:**
```bash
docker exec -it recall-db pg_isready
```

**Backup erstellen:**
```bash
docker exec recall-db pg_dump -U recall_user recall_memory > backup_recall_$(date +%Y%m%d).sql
```

**Backup wiederherstellen:**
```bash
docker exec -i recall-db psql -U recall_user recall_memory < backup_recall_DATUM.sql
```

**Groesse pruefen:**
```bash
docker exec recall-db psql -U recall_user recall_memory -c "SELECT pg_size_pretty(pg_database_size('recall_memory'));"
```

**Alte Eintraege aufraemen (aelter als 90 Tage):**
```bash
docker exec recall-db psql -U recall_user recall_memory -c "DELETE FROM conversations WHERE started_at < NOW() - INTERVAL '90 days';"
```

**SQLite-Alternative:**
```bash
# Backup
cp ~/.claude/data/recall.db ~/.claude/data/recall_backup_$(date +%Y%m%d).db
# Groesse
ls -lh ~/.claude/data/recall.db
```

---

## Seite 60 — Kapitel 12: Funktions-Registry

Alle Funktionen werden mit eindeutiger ID registriert.

**Format:** FN-XXX (dreistellig, fortlaufend)

| FN-ID | Agent | Funktion | Parameter | Abhaengigkeiten |
|-------|-------|----------|-----------|----------------|
| FN-001 | Berater | Briefing starten | Nutzer-Eingabe | — |
| FN-002 | Berater | Komplexitaet bewerten | Task | — |
| FN-003 | Berater | Task-Queue erstellen | Briefing | FN-001 |
| FN-004 | Berater | Agent zuweisen | Task + Agent | FN-003 |
| FN-005 | Berater | Fortschritt melden | Meilenstein | FN-004 |
| FN-006 | Berater | Fragenkatalog verwalten | Frage | — |
| FN-007 | Berater | Fallback ausfuehren | Fehler | FN-004 |
| FN-008 | Berater | Alle stoppen | — | — |
| FN-009 | Architekt | Design erstellen | Anforderungen | FN-003 |
| FN-010 | Architekt | Veto ausueben | Design | FN-009 |
| FN-011 | Architekt | Abhaengigkeiten mappen | Feature | FN-009 |
| FN-012 | Architekt | ADR schreiben | Entscheidung | FN-009 |
| FN-013 | Coder | Implementieren | Task + Arch. | FN-009 |
| FN-014 | Coder | Refactoren | Feedback | FN-023 |
| FN-015 | Coder | Code pruefen | Anweisung | — |
| FN-016 | Coder | Funktion registrieren | FN-Details | FN-013 |
| FN-017 | Coder | Endpoint registrieren | EP-Details | FN-013 |
| FN-018 | Tester | Tests schreiben | Code | FN-013 |
| FN-019 | Tester | Tests ausfuehren | Test-Pfad | FN-018 |
| FN-020 | Tester | Debuggen | Fehler | FN-019 |
| FN-021 | Tester | Coverage messen | Projekt | FN-019 |
| FN-022 | Tester | Regression testen | Fix | FN-020 |
| FN-023 | Reviewer | Code reviewen | Diff | FN-013 |
| FN-024 | Reviewer | Auto-Fix | Befund | FN-023 |
| FN-025 | Reviewer | Commit + Push | Dateien | FN-023 |
| FN-026 | Reviewer | Changelog erstellen | Commit | FN-025 |
| FN-027 | Reviewer | Repo konfigurieren | URL | — |
| FN-028 | Designer | UI erstellen | Anforderungen | FN-009 |
| FN-029 | Designer | Design-System | Token | — |
| FN-030 | Designer | Responsive Check | Komponente | FN-028 |
| FN-031 | Designer | a11y Check | Komponente | FN-028 |
| FN-032 | Analyst | Repo analysieren | Repo | — |
| FN-033 | Analyst | Repos vergleichen | Repo-A + B | FN-032 |
| FN-034 | Analyst | Merge planen | Repo-A + B | FN-033 |
| FN-035 | Analyst | Dependency Map | Repo | FN-032 |
| FN-036 | Doc-Scanner | URL scannen | URL | — |
| FN-037 | Doc-Scanner | URL-Liste | — | — |
| FN-038 | Doc-Scanner | URL hinzufuegen | URL + Scope | — |
| FN-039 | Doc-Scanner | Diff anzeigen | URL | FN-036 |
| FN-040 | Doc-Scanner | KB importieren | Pfad | — |
| FN-041 | DevOps | Deployen | Target | FN-025 |
| FN-042 | DevOps | Env verwalten | Key + Value | — |
| FN-043 | DevOps | CI/CD verwalten | Config | — |
| FN-044 | DevOps | Health-Check | — | — |
| FN-045 | DevOps | Rollback | — | FN-041 |
| FN-046 | Dokumentierer | Auto-Docs | Pfad | FN-025 |
| FN-047 | Dokumentierer | Docs verfeinern | Pfad | FN-046 |
| FN-048 | Dokumentierer | Registry fuehren | — | FN-016/017 |
| FN-049 | Dokumentierer | Manual erstellen | Rolle | FN-048 |
| FN-050 | Dokumentierer | API-Docs | API-Pfad | FN-017 |
| FN-051 | Gehirn | Core Memory lesen | Block-Name | — |
| FN-052 | Gehirn | Core Memory aktualisieren | Block-Name + Wert | FN-051 |
| FN-053 | Gehirn | Memory durchsuchen | Suchbegriff | — |
| FN-054 | Gehirn | Memory speichern | Inhalt + Scope | — |
| FN-055 | Gehirn | Memory auflisten | Scope-Filter | — |
| FN-056 | Gehirn | Memory abrufen | Memory-ID | FN-053 |
| FN-057 | Gehirn | Memory loeschen | Memory-ID | FN-053 |
| FN-058 | Gehirn | Konversation suchen | Suchbegriff | — |
| FN-059 | Gehirn | Konversation nach Datum | Von + Bis | — |
| FN-060 | Berater | Naechsten Schritt ausfuehren | — | Naechster Task-Schritt |
| FN-061 | Doc-Scanner | URL aus Scan-Liste entfernen | URL/Nummer | Bestaetigung |
| FN-062 | Doc-Scanner | URL-Einstellungen aendern | URL/Nummer + Parameter | Bestaetigung |
| FN-063 | Doc-Scanner | Scanner-Konfiguration anzeigen/aendern | Config-Key + Wert | Bestaetigung |

---

## Seite 64 — Kapitel 13: Endpoint-Registry

**Format:** EP-XXX (dreistellig, fortlaufend)

Die Endpoint-Registry wird vom Coder (FN-017) befuellt und vom Dokumentierer (FN-048) gepflegt.

Beispiel-Struktur:

| EP-ID | Pfad | Methode | Beschreibung | Parameter | Response | Auth | Abhaengigkeiten |
|-------|------|---------|-------------|-----------|----------|:----:|----------------|
| EP-001 | /api/auth/login | POST | User Login | email, password | JWT Token | Nein | — |
| EP-002 | /api/auth/refresh | POST | Token erneuern | refresh_token | Neuer JWT | Ja | EP-001 |
| EP-003 | /api/users | GET | Alle User listen | page, limit | User-Array | Ja | EP-001 |

---

## Seite 67 — Kapitel 14: Einstellungen

### 14.1 Globale Einstellungen

| Einstellung | Pfad | Beschreibung |
|------------|------|-------------|
| Hooks | `~/.claude/settings.json` | Hook-Konfiguration |
| Agenten | `~/.claude/agents/*.md` | Agenten-Profile |
| Skills | `~/.claude/skills/*/SKILL.md` | Profil-Skills |
| MCP | `~/.claude.json` | MCP-Server (maschinenspezifisch) |
| Kommunikation | `~/.claude/config/communication.json` | Slack/WhatsApp/Linear |
| Datenbanken | `~/.claude/config/databases.yaml` | DB-Verbindungen |
| Active Profiles | `~/.claude/active-profiles.json` | Aktuell aktive Profile |

### 14.2 Temperatur-Einstellungen

| Agent | Temperatur | Begruendung |
|-------|:----------:|-------------|
| Berater | 0.3 | Konsistente Orchestrierung |
| Architekt | 0.2 | Praezise Design-Entscheidungen |
| Coder | 0.1 | Minimale Halluzination im Code |
| Tester | 0.1 | Exakte Test-Generierung |
| Reviewer | 0.2 | Konsistente Reviews |
| Designer | 0.5 | Etwas Kreativitaet erlaubt |
| Analyst | 0.1 | Praezise Analyse |
| Doc-Scanner | 0.1 | Exakte Extraktion |
| DevOps | 0.1 | Keine Fehler bei Deployment |
| Dokumentierer | 0.3 | Lesbare Texte |

---

## Seite 72 — Kapitel 15: Administration

### 15.1 System starten/stoppen

```bash
# Alles starten
docker compose up -d

# Alles stoppen
docker compose down

# Einzelnen Service neustarten
docker compose restart SERVICE_NAME

# Logs ansehen
docker compose logs -f SERVICE_NAME
```

### 15.2 Backup + Restore

```bash
# Backup aller Datenbanken
bash scripts/backup.sh

# Restore
bash scripts/restore.sh BACKUP_DATUM
```

### 15.3 Updates

```bash
# Claude Code CLI updaten
npm update -g @anthropic-ai/claude-code

# Docker Images updaten
docker compose pull
docker compose up -d

# Agenten-Profile updaten
bash scripts/sync-setup.sh pull
```

### 15.4 User-Rollen verwalten

| Rolle | Rechte |
|-------|--------|
| Admin | Alles — System, Agenten, DBs, Deployment |
| Supervisor | Agenten steuern, Reviews, Reports — kein DB/Server-Zugang |
| Worker | Eigene Tasks, Code schreiben — kein Admin-Zugang |

---

## Seite 77 — Kapitel 16: Fehlerbehebung

| Problem | Ursache | Loesung |
|---------|---------|---------|
| Agent antwortet nicht | Rate-Limit oder Model-Fehler | Fallback greift, oder `/health` pruefen |
| Hook blockiert | Sicherheits-Check schlaegt an | Hook-Feedback lesen, Code anpassen |
| DB-Verbindung weg | Container gestoppt | `docker compose restart SERVICE` |
| Profil nach Compact weg | Reload-Hook defekt | `cat ~/.claude/active-profiles.json` pruefen |
| Notification kommt nicht | Webhook-URL falsch | `communication.json` pruefen |
| Langsame Antworten | Zu viele parallele Agenten | `max_parallel_agents` reduzieren |
| Wissensgraph leer | HippoRAG 2 nicht verbunden | `databases.yaml` + Neo4j Container pruefen |

---

## Seite 80 — Anhang A: Alle Commands

| Command | Agent | FN-ID | Beschreibung |
|---------|-------|-------|-------------|
| `/briefing` | Berater | FN-001 | Strukturiertes Briefing starten |
| `/plan` | Berater | FN-002 | Aufgabenplan erstellen |
| `/delegate` | Berater | FN-004 | Task an Agent zuweisen |
| `/katalog` | Berater | FN-006 | Fragenkatalog anzeigen |
| `/fortschritt` | Berater | FN-005 | Status aller Agenten |
| `/stop-alle` | Berater | FN-008 | Alle stoppen |
| `/weiter` | Berater | FN-060 | Naechsten Schritt ausfuehren |
| `/design` | Architekt | FN-009 | System-Design erstellen |
| `/veto` | Architekt | FN-010 | Design blockieren |
| `/deps` | Architekt | FN-011 | Abhaengigkeiten zeigen |
| `/adr` | Architekt | FN-012 | Decision Record schreiben |
| `/implement` | Coder | FN-013 | Code implementieren |
| `/refactor` | Coder | FN-014 | Code ueberarbeiten |
| `/check` | Coder | FN-015 | Code pruefen |
| `/register` | Coder | FN-016/017 | Funktion/Endpoint registrieren |
| `/templates` | Coder | — | Templates anzeigen |
| `/test` | Tester | FN-019 | Tests ausfuehren |
| `/debug` | Tester | FN-020 | Fehler analysieren |
| `/coverage` | Tester | FN-021 | Coverage anzeigen |
| `/regression` | Tester | FN-022 | Regressions-Tests |
| `/review` | Reviewer | FN-023 | Code-Review |
| `/commit` | Reviewer | FN-025 | Commit + Push |
| `/repo` | Reviewer | FN-027 | Repo-URL setzen |
| `/changelog` | Reviewer | FN-026 | Changelog erstellen |
| `/design-ui` | Designer | FN-028 | UI-Komponente erstellen |
| `/theme` | Designer | FN-029 | Design-System verwalten |
| `/responsive` | Designer | FN-030 | Responsive-Check |
| `/a11y` | Designer | FN-031 | Accessibility-Check |
| `/analyze` | Analyst | FN-032 | Repo analysieren |
| `/compare` | Analyst | FN-033 | Repos vergleichen |
| `/merge-plan` | Analyst | FN-034 | Merge-Strategie |
| `/deps-map` | Analyst | FN-035 | Dependency-Map |
| `/scan` | Doc-Scanner | FN-036 | URL scannen |
| `/scan-list` | Doc-Scanner | FN-037 | URL-Liste |
| `/scan-add` | Doc-Scanner | FN-038 | URL hinzufuegen |
| `/scan-diff` | Doc-Scanner | FN-039 | Aenderungen zeigen |
| `/kb-import` | Doc-Scanner | FN-040 | KB importieren |
| `/scan-remove` | Doc-Scanner | FN-061 | URL aus Scan-Liste entfernen |
| `/scan-edit` | Doc-Scanner | FN-062 | URL-Einstellungen aendern |
| `/scan-config` | Doc-Scanner | FN-063 | Scanner-Konfiguration anzeigen/aendern |
| `/deploy` | DevOps | FN-041 | Deployment starten |
| `/env` | DevOps | FN-042 | Env-Variablen |
| `/ci` | DevOps | FN-043 | CI/CD Pipeline |
| `/health` | DevOps | FN-044 | Health-Check |
| `/rollback` | DevOps | FN-045 | Rollback |
| `/docs` | Dokumentierer | FN-046 | Auto-Docs generieren |
| `/docs-refine` | Dokumentierer | FN-047 | Docs verfeinern |
| `/registry` | Dokumentierer | FN-048 | Registry anzeigen |
| `/manual` | Dokumentierer | FN-049 | Manual erstellen |
| `/api-docs` | Dokumentierer | FN-050 | API-Docs generieren |
| `/core-read` | Gehirn | FN-051 | Core Memory Block lesen |
| `/core-update` | Gehirn | FN-052 | Core Memory Block aktualisieren |
| `/memory-search` | Gehirn | FN-053 | Erinnerungen durchsuchen |
| `/memory-store` | Gehirn | FN-054 | Neue Erinnerung speichern |
| `/memory-list` | Gehirn | FN-055 | Alle Erinnerungen auflisten |
| `/memory-get` | Gehirn | FN-056 | Einzelne Erinnerung abrufen |
| `/memory-forget` | Gehirn | FN-057 | Erinnerung loeschen |
| `/conv-search` | Gehirn | FN-058 | Konversationshistorie durchsuchen |
| `/conv-search-date` | Gehirn | FN-059 | Konversationen nach Datum suchen |
| `/status` | Alle | System-Command | Agent-Status anzeigen |
| `/memory` | Alle | FN-053 | Alias fuer /memory-search |
| `/save` | Alle | System-Command | Aktuellen Kontext in Datenbank speichern |
| `/fragen` | Alle | System-Command | Offene Fragen anzeigen |
| `/profil` | Alle | System-Command | Aktive Profile anzeigen |
| `/cache` | Alle | System-Command | Smart Cache abfragen oder leeren |
| `/tools` | Alle | System-Command | Verfuegbare Tools und MCP-Server anzeigen |

---

## Seite 83 — Anhang B: Alle Rules

[Vollstaendige Rule-Liste: Siehe Projektplanung Kapitel 3, alle R-XX-XX Rules]

---

## Seite 86 — Anhang C: Alle Hook-Konfigurationen

[Vollstaendige settings.json: Siehe Runbook Schritt 4.2]
