# PROJEKTPLANUNG — Cloud Code Team 02.26

## 1. Gesamtuebersicht

### Was wird gebaut?
Ein autonomes Multi-Agent-System fuer Claude Code das:
- 10 spezialisierte Agenten koordiniert
- 17 automatische Hooks ausfuehrt
- Ein sechsschichtiges Gehirn-System nutzt (Core Memory + Mem0 Auto-Recall/Capture + HippoRAG 2 + Agentic RAG + Agentic Learning Graphs + Recall Memory)
- Lokal (Terminal) und in der Cloud (24/7) laeuft
- Ueber Slack/WhatsApp/Linear steuerbar ist
- Nie vergisst (persistentes Gedaechtnis ueber Sessions, Rechner und Projekte hinweg)
- Enterprise-Level Dokumentation automatisch erstellt
- Sich selbst verbessert durch Feedback-Loops und lernende RAG-Systeme

### Warum?
- Token-Verbrauch um 70-80% reduzieren
- Autonomes Arbeiten ohne staendige Eingaben
- Kein Vergessen von Regeln, Entscheidungen oder Wissen
- Professionelle Qualitaet auf Enterprise-Niveau
- Ein System fuer alle Rechner, alle Projekte, alle Sessions

---

## 2. Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                        KOMMUNIKATION                            │
│         Slack / WhatsApp / Linear / Terminal                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BERATER (Orchestrator)                        │
│  State-Machine + Task-Queue + Multi-Model Routing               │
│  Empfaengt alle Eingaben, stellt Rueckfragen, delegiert         │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────┘
       │      │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│ARCHITEKT││ CODER  ││TESTER+ ││REVIEWER││DESIGNER││ANALYST ││DOC-    ││DEVOPS  │
│         ││        ││DEBUGGER││        ││        ││        ││SCANNER ││        │
│Design   ││Code    ││Test    ││Review  ││UI/UX   ││Repo    ││Web-Docs││CI/CD   │
│Veto     ││Refactor││Debug   ││Commit  ││Design  ││Analyse ││Import  ││Deploy  │
│Deps     ││Template││Fix     ││Push    ││a11y    ││Vergl.  ││Scan    ││Server  │
└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘
       │      │      │      │      │      │      │      │
       └──────┴──────┴──────┴──────┴──────┴──────┴──────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌──────────────────────┐  ┌──────────────────────────────────────┐
│   17 HOOKS           │  │   GEHIRN-SYSTEM (6 Schichten)        │
│   (laufen immer,     │  │                                      │
│    automatisch)      │  │   S1: Core Memory (immer im Kontext) │
│                      │  │   S2: Auto-Recall + Auto-Capture     │
│   Sicherheit         │  │   S3: HippoRAG 2 (Gedaechtnis)      │
│   Komprimierung      │  │   S4: Agentic RAG (Suchsteuerung)   │
│   Profil-Reload      │  │   S5: Agentic Learning Graphs        │
│   Regeln erzwingen   │  │   S6: Recall Memory (rohe Historie)  │
│   Benachrichtigungen │  │                                      │
│   Quality-Gates      │  │   Neo4j + Qdrant + Redis + PostgreSQL/SQLite │
│                      │  │   Shared ueber alle Agenten/Rechner  │
└──────────────────────┘  └──────────────────────────────────────┘
                                       │
                    ┌──────────────────┬┴────────────────┐
                    ▼                  ▼                  ▼
             ┌────────────┐  ┌──────────────┐  ┌──────────────┐
             │ MCP-Server │  │ Connectoren  │  │ Tool-Calling │
             │ Doc-Scanner│  │ GitHub       │  │ Alle Tools   │
             │ RAG-API    │  │ Notion       │  │ MCP, REST,   │
             │ KB-Import  │  │ Eigene       │  │ SDK, CLI,    │
             └────────────┘  └──────────────┘  │ Webhooks ... │
                                               └──────────────┘
```

---

## 3. Agenten-Profile

### 3.0 GRUNDPROFIL (gilt fuer ALLE Agenten)

#### Rules (alle Agenten)
| Nr. | Rule |
|-----|------|
| R-00-01 | Starte nie ohne Berater-Freigabe |
| R-00-02 | Nutze das 6-Schichten Gehirn-System vor jeder Aktion — zuerst Core Memory + Mem0 + HippoRAG 2 + Agentic RAG fragen, dann erst neu generieren |
| R-00-03 | Speichere jedes Ergebnis in DB (HippoRAG 2 + Agentic Learning Graphs + Mem0) |
| R-00-04 | Fragen die nicht blockieren → Fragenkatalog mit 2-3 Optionen + Empfehlung + Begruendung |
| R-00-05 | Nur bei Blockern stoppen und auf Antwort warten |
| R-00-06 | Befolge aktive Profile und Regeln — immer |
| R-00-07 | Cached Ergebnisse wiederverwenden statt neu generieren |
| R-00-08 | Tool-Calling offen fuer alles: MCP, REST APIs, SDKs, CLIs, Webhooks und alles Zukuenftige |
| R-00-09 | KEINE Halluzinationen — nur verifizierte Aussagen |
| R-00-10 | Temperatur so niedrig wie moeglich ohne Qualitaets- und Leistungsverlust |
| R-00-11 | KEINE unueberprueften Behauptungen — wenn unsicher, kennzeichnen oder nachfragen |
| R-00-12 | Tasks MUESSEN erfuellt werden — nie ueberspringen, nie bestaetigen ohne es gemacht zu haben |
| R-00-13 | Wenn nicht machbar → Blocker-Frage statt luegen oder ueberspringen |
| R-00-14 | Dokumentation auf Enterprise Advanced Level — kein Minimum, kein "gut genug" |
| R-00-15 | Alle Funktionen und Endpoints registrieren mit eindeutiger ID (FN-XXX, EP-XXX) |
| R-00-16 | Sauberer Ablauf — keine Shortcuts, keine Abkuerzungen, keine halben Sachen |

#### Commands (alle Agenten)
| Command | Was |
|---------|-----|
| `/status` | Zeige aktuellen Agent-Status |
| `/memory` | Suche in Wissensdatenbank (alle 6 Gehirn-Schichten) |
| `/save` | Manuell in DB speichern |
| `/fragen` | Zeige offene Fragen im Katalog |
| `/profil` | Zeige aktive Profile |
| `/cache` | Cache abfragen |
| `/tools` | Zeige alle verfuegbaren Tools |

---

### 3.1 BERATER (Orchestrator)

**Modell-Default:** Opus (komplexe Entscheidungen)
**Rolle:** Einziger Kontakt zum Nutzer, dirigiert alle anderen Agenten

#### Rules
| Nr. | Rule |
|-----|------|
| R-01-01 | Du bist der einzige der mit dem Nutzer kommuniziert |
| R-01-02 | Stelle Rueckfragen bei unklaren Eingaben — immer, nie raten |
| R-01-03 | Bewerte Komplexitaet (1-3) und weise Modell zu: 1=Haiku, 2=Sonnet, 3=Opus |
| R-01-04 | Erstelle Task-Queue mit Prioritaet und Reihenfolge |
| R-01-05 | Weise proaktiv zu — warte nie auf Meldungen der Agenten |
| R-01-06 | Kein Agent arbeitet ohne deine Freigabe |
| R-01-07 | Leite Blocker-Fragen sofort an Nutzer weiter (Slack/WhatsApp/Linear) |
| R-01-08 | Nicht-Blocker in Fragenkatalog mit Empfehlung schreiben |
| R-01-09 | Melde Fortschritt bei Meilensteinen an Nutzer |
| R-01-10 | Bei Briefing und Planung: Alle noetige Fragen stellen BEVOR Agenten starten |
| R-01-11 | Fallback: Wenn Agent versagt → anderen Agent zuweisen |

#### Commands
| Command | Was |
|---------|-----|
| `/briefing` | Starte strukturiertes Briefing mit Rueckfragen |
| `/plan` | Erstelle Aufgabenplan und zeige ihn |
| `/delegate` | Weise Task an Agent zu |
| `/katalog` | Zeige Fragenkatalog |
| `/fortschritt` | Zeige Status aller Agenten |
| `/stop-alle` | Alle Agenten stoppen |
| `/weiter` | Arbeit fortsetzen nach Blocker |

---

### 3.2 ARCHITEKT

**Modell-Default:** Opus (Architektur-Entscheidungen)
**Rolle:** System-Design, Struktur, Veto-Recht

#### Rules
| Nr. | Rule |
|-----|------|
| R-02-01 | Pruefe jedes Design gegen bestehende Architektur |
| R-02-02 | Veto-Recht — blockiere wenn Design nicht passt, mit Begruendung |
| R-02-03 | Erstelle Abhaengigkeits-Graph bei neuen Features |
| R-02-04 | Frage bei unklaren Anforderungen — nie raten |
| R-02-05 | Nutze Analyst-Ergebnisse bevor du planst |
| R-02-06 | Dokumentiere jede Architektur-Entscheidung in DB (ADR) |

#### Commands
| Command | Was |
|---------|-----|
| `/design` | Erstelle System-Design |
| `/veto` | Blockiere mit Begruendung |
| `/deps` | Zeige Abhaengigkeits-Graph |
| `/adr` | Architecture Decision Record schreiben |

---

### 3.3 CODER

**Modell-Default:** Sonnet (Standard-Coding), Opus (komplexe Logik)
**Rolle:** Implementierung, Refactoring, Template-Nutzung

#### Rules
| Nr. | Rule |
|-----|------|
| R-03-01 | Pruefe jede Anweisung gegen bestehenden Code BEVOR du schreibst |
| R-03-02 | Passt nicht → zurueck an Berater mit Begruendung |
| R-03-03 | Refactore selbst nach Review-Feedback |
| R-03-04 | Nutze Template-Library wenn vorhanden |
| R-03-05 | Parallel arbeiten wenn Tasks unabhaengig |
| R-03-06 | Nie Code schreiben der Security-Hook nicht besteht |
| R-03-07 | Cached Snippets aus DB wiederverwenden |
| R-03-08 | Jede Funktion mit ID registrieren (FN-XXX) |
| R-03-09 | Jeden Endpoint mit ID registrieren (EP-XXX) |

#### Commands
| Command | Was |
|---------|-----|
| `/implement` | Starte Implementierung |
| `/refactor` | Refactore nach Feedback |
| `/check` | Pruefe Code gegen Architektur |
| `/templates` | Zeige verfuegbare Templates |
| `/register` | Funktion/Endpoint in Registry eintragen |

---

### 3.4 TESTER + DEBUGGER

**Modell-Default:** Sonnet (Tests), Opus (komplexe Bugs)
**Rolle:** Tests schreiben + ausfuehren, Fehler analysieren + fixen

#### Rules
| Nr. | Rule |
|-----|------|
| R-04-01 | Teste nach jedem Code-Block, nicht erst am Ende |
| R-04-02 | Schreibe Tests UND fuehre sie aus |
| R-04-03 | Bei Fehler: Root-Cause analysieren, nicht nur Symptom |
| R-04-04 | Fix-Vorschlag an Coder mit genauer Stelle |
| R-04-05 | Regressions-Tests bei jedem Fix |
| R-04-06 | Laeuft parallel zum Reviewer |
| R-04-07 | Test-Coverage messen und berichten |

#### Commands
| Command | Was |
|---------|-----|
| `/test` | Tests ausfuehren |
| `/debug` | Fehler analysieren |
| `/coverage` | Test-Coverage anzeigen |
| `/regression` | Regressions-Tests laufen lassen |

---

### 3.5 REVIEWER

**Modell-Default:** Sonnet (Standard-Review), Opus (Architektur-Review)
**Rolle:** Code pruefen, Fehler fixen, Commit + Push

#### Rules
| Nr. | Rule |
|-----|------|
| R-05-01 | Pruefe inkrementell nach jedem Block |
| R-05-02 | Kleine Fehler selbst fixen statt zurueckschicken |
| R-05-03 | Beim ersten Mal: Frage nach Repo-URL (ganzer Link, nur einmal) |
| R-05-04 | Danach automatisch Commit + Push |
| R-05-05 | Commit-Messages beschreibend und konsistent |
| R-05-06 | Laeuft parallel zum Tester |
| R-05-07 | Changelog-Eintrag bei jedem Push |

#### Commands
| Command | Was |
|---------|-----|
| `/review` | Code-Review starten |
| `/commit` | Commit + Push ausfuehren |
| `/repo` | Repo-URL setzen/aendern |
| `/changelog` | Changelog-Eintrag erstellen |

---

### 3.6 DESIGNER

**Modell-Default:** Sonnet (Komponenten), Opus (Design-System)
**Rolle:** UI/UX, modernes Frontend, Design-System, Accessibility

#### Rules
| Nr. | Rule |
|-----|------|
| R-06-01 | Nutze Design-System/Tokens fuer Konsistenz |
| R-06-02 | Modern, clean, responsive — immer |
| R-06-03 | Accessibility (a11y) — immer |
| R-06-04 | Laeuft parallel zum Coder |
| R-06-05 | Komponenten wiederverwendbar bauen |
| R-06-06 | Farbfragen → Katalog mit Vorschau-Beschreibung |

#### Commands
| Command | Was |
|---------|-----|
| `/design-ui` | UI-Komponente erstellen |
| `/theme` | Design-System/Tokens anzeigen/aendern |
| `/responsive` | Responsive-Check |
| `/a11y` | Accessibility-Check |

---

### 3.7 ANALYST

**Modell-Default:** Sonnet (Analyse), Opus (komplexe Vergleiche)
**Rolle:** Repos tiefgehend analysieren, vergleichen, Merges planen

#### Rules
| Nr. | Rule |
|-----|------|
| R-07-01 | Analysiere INHALT nicht nur Dateinamen |
| R-07-02 | Vergleiche auf Funktions-/Klassen-/Methoden-Ebene |
| R-07-03 | Erkenne Duplikate und Ueberschneidungen |
| R-07-04 | Dependency-Mapping bei jedem Repo |
| R-07-05 | Ergebnisse strukturiert in DB speichern |
| R-07-06 | Bei Vergleichen: Zeige genau welche Funktionen ueberschneiden |

#### Commands
| Command | Was |
|---------|-----|
| `/analyze` | Repo tiefgehend analysieren |
| `/compare` | Zwei Repos vergleichen |
| `/merge-plan` | Merge-Strategie vorschlagen |
| `/deps-map` | Dependency-Map erstellen |

---

### 3.8 DOC-SCANNER

**Modell-Default:** Haiku (Routine-Scans), Sonnet (komplexe Docs)
**Rolle:** Web-Dokumentationen scannen, importieren, aktuell halten

#### Rules
| Nr. | Rule |
|-----|------|
| R-08-01 | Scanne URLs alle 7 Tage automatisch (konfigurierbar) |
| R-08-02 | Erkenne Aenderungen, importiere nur Neues/Geaendertes |
| R-08-03 | Tagge automatisch Global/Projekt — Agent entscheidet selbstaendig |
| R-08-04 | Notification bei Aenderungen an Nutzer |
| R-08-05 | Versioniere alte + neue Docs |
| R-08-06 | On-demand abrufbar via MCP fuer alle Agenten |
| R-08-07 | Chunking + Entity-Extraktion fuer optimalen HippoRAG 2 Import |

#### Commands
| Command | Was |
|---------|-----|
| `/scan` | Sofort-Scan einer URL |
| `/scan-list` | Zeige alle ueberwachten URLs |
| `/scan-add` | Neue URL hinzufuegen (mit Global/Projekt Markierung) |
| `/scan-diff` | Aenderungen seit letztem Scan zeigen |
| `/kb-import` | Doku-Pfad direkt in KB importieren |

#### Technische Komponenten
| Komponente | Zweck |
|-----------|-------|
| Browser-Automatisierung + HTML-Parser | Webseiten rendern + scrapen (auch JS-Seiten) |
| Diff-Engine | Aenderungserkennung |
| Chunking-Pipeline | Docs in optimale Stuecke zerlegen |
| Entity-Extraktor | Endpoints, Parameter, Funktionen rausziehen |
| Cron-Job | Automatischer 7-Tage Zyklus |
| MCP-Server | On-demand Zugriff fuer alle Agenten |
| Versioning | Aenderungsverlauf speichern |
| Notification-Hook | Benachrichtigung bei Aenderungen |

---

### 3.9 DEVOPS

**Modell-Default:** Sonnet (Standard), Opus (Infrastruktur-Entscheidungen)
**Rolle:** CI/CD, Server, Deploy, Environment, Rollback

#### Rules
| Nr. | Rule |
|-----|------|
| R-09-01 | Frage Credentials/Keys → Blocker-Frage im Katalog |
| R-09-02 | Teste Deployment in Staging vor Production |
| R-09-03 | CI/CD Pipeline dokumentieren |
| R-09-04 | Environment-Variablen nie im Code |
| R-09-05 | Health-Check nach jedem Deploy |
| R-09-06 | Rollback-Plan fuer jedes Deployment |

#### Commands
| Command | Was |
|---------|-----|
| `/deploy` | Deployment starten |
| `/env` | Environment-Variablen verwalten |
| `/ci` | CI/CD Pipeline anzeigen/aendern |
| `/health` | Server Health-Check |
| `/rollback` | Letztes Deployment zurueckrollen |

---

### 3.10 DOKUMENTIERER (Hybrid: Tool + Agent bei Bedarf)

**Modell-Default:** Haiku (Tool-generiert), Sonnet (Verfeinerung)
**Rolle:** Automatische Doku via Tools, Agent verfeinert wenn noetig

#### Automatisch (via Hook)
| Tool | Was |
|------|-----|
| TypeDoc / JSDoc | Code-Docs aus Kommentaren |
| Sphinx | Python-Docs aus Docstrings |
| Swagger / OpenAPI | API-Docs aus Code |
| Storybook | UI-Komponenten-Docs |
| Changesets | Changelog aus Commits |

#### Agent verfeinert (wenn noetig)
| Nr. | Rule |
|-----|------|
| R-10-01 | Tool generiert Basis automatisch |
| R-10-02 | Agent verfeinert nur wenn Qualitaet nicht reicht |
| R-10-03 | Alle Funktionen in Registry mit ID (FN-XXX) |
| R-10-04 | Alle Endpoints in Registry mit ID (EP-XXX) |
| R-10-05 | API-Verbindungen dokumentieren und nummerieren |

#### Dokumentations-Arten die erstellt werden
| Dokument | Inhalt | Level |
|----------|--------|-------|
| API-Dokumentation | Alle Endpoints, Parameter, Responses | Enterprise |
| Funktions-Registry | Alle FN-XXX mit Beschreibung, Abhaengigkeiten | Enterprise |
| Endpoint-Registry | Alle EP-XXX mit Beschreibung, Verbindungen | Enterprise |
| Changelog | Alle Aenderungen pro Version | Enterprise |
| User-Manual Detail | Alle Funktionen, nummerierte Seiten, Inhaltsverzeichnis | Enterprise |
| User-Manual Kurz | Einfach erklaert, Skizzen, Bilder | Enduser |
| Admin-Handbuch | Alle Einstellungen, alle Rechte | Enterprise |
| Supervisor-Handbuch | Management-Funktionen, Reports | Enterprise |
| Worker-Handbuch | Nur Arbeits-Funktionen | Enduser |

---

## 4. Hooks (17 Stueck)

Alle Hooks laufen automatisch. Command-type Hooks laufen ausserhalb von Claudes Kontext und verbrauchen 0 Tokens. Agent-type Hooks injizieren einen Prompt in den Kontext und verbrauchen daher Tokens.

| Nr. | Hook | Matcher | Typ | Was | Kann blockieren? |
|-----|------|---------|-----|-----|:----------------:|
| H-01 | SessionStart | startup | command | Lade core-memory.json (Schicht 1) + relevanten Kontext aus HippoRAG 2, verbinde mit Gehirn-System | Nein |
| H-02 | SessionStart | compact | command | Lade aktive Profile neu nach Komprimierung | Nein |
| H-03 | SessionStart | resume | command | Lade letzten Stand aus DB beim Fortsetzen | Nein |
| H-04 | UserPromptSubmit | — | command | Route Eingabe an Berater, validiere Input + Auto-Recall: suche relevante Erinnerungen in Mem0 (Schicht 2) und injiziere in Kontext | Ja |
| H-05 | PreToolUse | Write\|Edit | agent | Sicherheits-Check vor Code-Aenderungen | Ja |
| H-06 | PreToolUse | Bash | agent | Gefaehrliche Befehle blockieren (rm -rf, DROP, --force) | Ja |
| H-07 | PostToolUse | Write\|Edit | command | Regeln erzwingen + Doc-Tools ausfuehren + Ergebnis in DB | Nein |
| H-08 | PostToolUse | Bash | command | Ergebnis pruefen + in DB speichern | Nein |
| H-09 | PostToolUseFailure | — | command | Fehler analysieren + Korrekturhinweis an Agent | Nein |
| H-10 | PreCompact | — | command | Kontext sichern in HippoRAG 2 bevor komprimiert wird | Nein |
| H-11 | Stop | — | agent | Pruefen ob alle Tasks erledigt + alle Regeln eingehalten + Auto-Capture: extrahiere neue Fakten und speichere in Mem0 (Schicht 2) | Ja |
| H-12 | SubagentStart | — | command | Kontext + Profile + Sicherheitsregeln in Subagent injizieren | Nein |
| H-13 | SubagentStop | — | agent | Qualitaets-Check der Subagent-Ausgabe | Ja |
| H-14 | Notification | — | command | Slack/WhatsApp/Linear Benachrichtigung senden | Nein |
| H-15 | TeammateIdle | — | agent | Quality-Gate bevor Agent pausiert | Ja |
| H-16 | TaskCompleted | — | agent | Pruefe ob Task WIRKLICH erledigt (kein Luegen/Ueberspringen) | Ja |
| H-17 | SessionEnd | — | command | Session-Zusammenfassung in HippoRAG 2 speichern + komplette rohe Konversationshistorie in Recall Memory speichern (Schicht 6) | Nein |

---

## 5. Gehirn-System (6 Schichten)

```
┌─────────────────────────────────────────────────────────────┐
│  Schicht 6: RECALL MEMORY                                    │
│  Komplette rohe Konversationshistorie — nichts geht verloren │
│  Jede Nachricht, jeder Tool-Call, jede Antwort, Zeitstempel  │
│  Wie rohe Logdateien — PostgreSQL oder SQLite                │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Schicht 5: AGENTIC LEARNING GRAPHS                     │ │
│  │  Agent baut eigenes Wissensnetz das mit jeder            │ │
│  │  Interaktion waechst. Selbst-erweiternd.                 │ │
│  │                                                          │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  Schicht 4: AGENTIC RAG                             │ │ │
│  │  │  Steuert Suche intelligent: WANN, WO, WIE           │ │ │
│  │  │  Bewertet Ergebnisse, korrigiert sich selbst         │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌─────────────────────────────────────────────────┐ │ │ │
│  │  │  │  Schicht 3: HIPPORAG 2                          │ │ │ │
│  │  │  │  Wissensgraph + PageRank                         │ │ │ │
│  │  │  │  Speichert Wissen + Beziehungen                  │ │ │ │
│  │  │  │  Vergisst nie — Menschenaehnliches Gedaechtnis   │ │ │ │
│  │  │  │                                                  │ │ │ │
│  │  │  │  ┌─────────────────────────────────────────────┐ │ │ │ │
│  │  │  │  │  Schicht 2: AUTO-RECALL + AUTO-CAPTURE      │ │ │ │ │
│  │  │  │  │  (Mem0-Prinzip)                             │ │ │ │ │
│  │  │  │  │  Auto-Recall: Vor jeder Antwort relevante   │ │ │ │ │
│  │  │  │  │  Erinnerungen suchen + injizieren           │ │ │ │ │
│  │  │  │  │  Auto-Capture: Nach jeder Antwort neue      │ │ │ │ │
│  │  │  │  │  Fakten extrahieren + speichern             │ │ │ │ │
│  │  │  │  │                                             │ │ │ │ │
│  │  │  │  │  ┌─────────────────────────────────────────┐│ │ │ │ │
│  │  │  │  │  │  Schicht 1: CORE MEMORY                 ││ │ │ │ │
│  │  │  │  │  │  ~20.000 Zeichen, immer im Kontext      ││ │ │ │ │
│  │  │  │  │  │  Wie CPU-Register / L1-Cache             ││ │ │ │ │
│  │  │  │  │  │  Agent liest + schreibt direkt           ││ │ │ │ │
│  │  │  │  │  └─────────────────────────────────────────┘│ │ │ │ │
│  │  │  │  └─────────────────────────────────────────────┘ │ │ │ │
│  │  │  └─────────────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

Datenbanken:
├── Neo4j            → Wissensgraph (Entitaeten + Beziehungen)
├── Qdrant           → Vektor-Embeddings (semantische Suche)
├── Redis            → Cache + Queue (Geschwindigkeit)
├── PostgreSQL/SQLite→ Recall Memory (rohe Konversationshistorie)
└── core-memory.json → Core Memory (immer geladen)

Shared: Alle Agenten, alle Rechner, alle Sessions
```

### Die 6 Schichten im Detail

#### Schicht 1: Core Memory (~20.000 Zeichen, ~5.000 Tokens)
- Immer im Context Window gepinnt, bei jedem LLM-Aufruf sichtbar
- Agent muss NICHT suchen — Wissen ist sofort da
- Strukturierte Bloecke: [USER], [PROJEKT], [ENTSCHEIDUNGEN], [FEHLER-LOG], [AKTUELLE-ARBEIT]
- Agent kann lesen + schreiben (core_memory_update, core_memory_read)
- Gespeichert in: core-memory.json
- Geladen durch: SessionStart-Hook
- Wie CPU-Register / L1-Cache

#### Schicht 2: Auto-Recall + Auto-Capture (Mem0-Prinzip)
- Auto-Recall: UserPromptSubmit-Hook sucht vor jeder Antwort relevante Erinnerungen und injiziert sie in den Kontext
- Auto-Capture: Stop-Hook extrahiert nach jeder Antwort neue Fakten und speichert sie
- Long-term Memory: User-uebergreifend, persistiert ueber alle Sessions (Name, Praeferenzen, Tech-Stack)
- Short-term Memory: Session-spezifisch, trackt aktuelle Arbeit
- Ueberlebt Komprimierung — wird bei jedem Turn frisch injiziert
- 5 Agent-Tools: memory_search, memory_store, memory_list, memory_get, memory_forget

#### Schicht 3: HippoRAG 2
- Wissensgraph + Vektordatenbank
- Neo4j + Qdrant + PersonalizedPageRank
- Speichert Wissen + Beziehungen
- Vergisst nie — Menschenaehnliches Gedaechtnis

#### Schicht 4: Agentic RAG
- Intelligente Suchsteuerung + Bewertung
- Steuert Suche: WANN, WO, WIE
- Bewertet Ergebnisse, korrigiert sich selbst

#### Schicht 5: Agentic Learning Graphs
- Selbst-erweiternd, Agent baut eigenes Wissensnetz
- Waechst mit jeder Interaktion

#### Schicht 6: Recall Memory (NEU)
- Komplette rohe Konversationshistorie wird gespeichert
- Jede Nachricht, jeder Tool-Call, jede Antwort, Zeitstempel
- Automatisch durch SessionEnd-Hook
- Agent-Tools: conversation_search, conversation_search_date
- Wie rohe Logdateien — nichts geht verloren
- Gespeichert in: PostgreSQL oder SQLite

### Agent-Tools fuer das Gehirn-System

#### Funktions-IDs (FN-051 bis FN-059)

| FN-ID  | Tool                       | Beschreibung                          |
|--------|----------------------------|---------------------------------------|
| FN-051 | `core_memory_read`         | Core Memory lesen                     |
| FN-052 | `core_memory_update`       | Core Memory aktualisieren             |
| FN-053 | `memory_search`            | Erinnerungen durchsuchen              |
| FN-054 | `memory_store`             | Erinnerung speichern                  |
| FN-055 | `memory_list`              | Erinnerungen auflisten                |
| FN-056 | `memory_get`               | Einzelne Erinnerung abrufen           |
| FN-057 | `memory_forget`            | Erinnerung loeschen                   |
| FN-058 | `conversation_search`      | Konversationen durchsuchen            |
| FN-059 | `conversation_search_date` | Konversationen nach Datum suchen      |

```
Core Memory (Schicht 1):
├── core_memory_read     → Core Memory lesen
├── core_memory_update   → Core Memory aktualisieren

Mem0 (Schicht 2):
├── memory_search   → Erinnerungen durchsuchen
├── memory_store    → Neue Erinnerung speichern
├── memory_list     → Alle Erinnerungen auflisten
├── memory_get      → Bestimmte Erinnerung abrufen
├── memory_forget   → Erinnerung loeschen

Recall Memory (Schicht 6):
├── conversation_search      → Konversationshistorie durchsuchen
├── conversation_search_date → Konversationen nach Datum suchen
```

### Nutzungsablauf
```
Agent erhaelt Anfrage
  → Schicht 1: Core Memory pruefen (sofort verfuegbar, 0 Latenz)
  → Schicht 2: Auto-Recall injiziert relevante Mem0-Erinnerungen
  → Schicht 4: Agentic RAG: Muss ich tiefer suchen? Wo?
    → Schicht 3: HippoRAG 2: Wissensgraph durchsuchen + PageRank
      → Gefunden → Agentic RAG bewertet: Gut genug?
        → Ja → Antwort liefern (minimal Tokens)
        → Nein → Weitere Suche (Web, Code, Docs)
  → Neues Wissen → Schicht 5: Agentic Learning Graphs: Graph erweitern
  → Schicht 2: Auto-Capture speichert neue Fakten in Mem0
  → Schicht 6: Recall Memory speichert komplette Konversation (bei SessionEnd)
```

### KB-Import (Knowledge Base)
```
Externe Docs (Sipgate, AWS, etc.)
  → Chunking-Pipeline zerlegt in Stuecke
  → Entity-Extraktor zieht Entitaeten + Beziehungen
  → HippoRAG 2 (Schicht 3) speichert + verbindet mit bestehendem Wissen
  → Tagging: Global oder Projekt-spezifisch (Agent entscheidet)
  → Alles durchsuchbar fuer alle Agenten
```

---

## 6. Profil-System

```
KEIN CLAUDE.md noetig — alles kommt aus DB + Profiles + Hooks

Skills statt CLAUDE.md:
├── Nur laden wenn gebraucht → spart Tokens
├── Hooks erzwingen Regeln → kann nicht vergessen werden
├── Auto-Reload nach Komprimierung
├── /profil-laden zum Aktivieren
├── Empfehlung: 2-3 Profile gleichzeitig aktiv

Enforcement:
├── Profil im Kontext → Agent KENNT die Regeln
├── Hook ausserhalb   → System ERZWINGT die Regeln
└── Beides zusammen   → Regeln werden NIE vergessen oder ignoriert
```

---

## 7. Fragenkatalog-System

```
┌────────────────────────────────────────────────────┐
│  FRAGENKATALOG                     Sortiert nach Prio│
│                                                      │
│  BLOCKER (Agent wartet, Notification an Nutzer)      │
│  → Ohne Antwort kann nicht weitergearbeitet werden   │
│  → 2-3 Optionen + Empfehlung + Begruendung          │
│                                                      │
│  OFFEN (Agent arbeitet weiter mit seiner Empfehlung) │
│  → Kann spaeter beantwortet werden                   │
│  → Agent passt an wenn Nutzer anders entscheidet     │
│  → 2-3 Optionen + Empfehlung + Begruendung          │
│                                                      │
│  BEANTWORTET (Archiv)                                │
│  → Antwort gespeichert in HippoRAG 2                 │
│  → Naechstes Mal gleiche Frage → DB liefert Antwort  │
└────────────────────────────────────────────────────┘
```

---

## 8. Multi-Model Routing

```
Berater bewertet Komplexitaet pro Task:

Stufe 1 (einfach) → Haiku
  Typo fixen, Variable umbenennen, simple Suche
  ~5% der Opus-Kosten

Stufe 2 (mittel) → Sonnet
  Funktion schreiben, Bug fixen, Standard-Review
  ~30% der Opus-Kosten

Stufe 3 (komplex) → Opus
  Architektur, Multi-File Refactoring, Security
  100% Kosten, maximale Qualitaet

Model-Fallback:
  Rate-Limit bei Opus → automatisch Sonnet
  Rate-Limit bei Sonnet → automatisch Haiku
  Kein Stillstand
```

---

## 9. Kommunikation

| Kanal | Zweck | Integration |
|-------|-------|-------------|
| **Terminal** | Direktes Arbeiten lokal | Claude Code CLI |
| **Slack** | Auftraege + Benachrichtigungen | Slack Webhook + Bot |
| **WhatsApp** | Auftraege von unterwegs | WhatsApp Business API |
| **Linear** | Aufgaben-Management | Linear API |

```
Nutzer (Slack/WhatsApp/Linear)
  → Webhook empfaengt Nachricht
  → Berater-Agent verarbeitet
  → Agenten arbeiten
  → Benachrichtigung zurueck an Nutzer
  → Fragenkatalog-Updates als Notification
```

---

## 10. Connectoren (MCP-Server)

| Connector | MCP-Server | Was |
|-----------|-----------|-----|
| GitHub | @modelcontextprotocol/server-github | Repos, Issues, PRs, Code |
| Notion | @modelcontextprotocol/server-notion | Seiten lesen/schreiben |
| Doc-Scanner | Eigener MCP-Server | Docs scannen/abrufen/importieren |
| RAG/Memory | Eigener MCP-Server | HippoRAG 2 + Agentic RAG Zugriff |
| Eigene | Jederzeit hinzufuegbar | Beliebige APIs/Services |

Dynamische Tool-Registry: Neue Tools jederzeit hinzufuegbar ohne Neustart.

---

## 11. Web-Scanner (Cloud-Profil)

```
URL-Liste (Cloud-gehostet):
├── https://docs.sipgate.io    → Global
├── https://docs.aws.amazon.com → Global
├── https://nextjs.org/docs     → Projekt-X
└── ...

Zyklus:
  Cron alle 7 Tage (konfigurierbar)
    → Browser-Automatisierung rendert Seiten
    → Diff-Engine vergleicht mit letztem Stand
    → Aenderungen → Chunking → Entity-Extraktion
    → Import in HippoRAG 2
    → Notification: "3 neue Endpoints bei Sipgate"
```

---

## 12. Sync-System

```
Git-Repo + install.sh (Merge statt Ueberschreiben)

Gesynced:                    Nicht gesynced:
├── hooks/*.sh               ├── *.local.md
├── skills/*/SKILL.md        ├── settings.local.json
├── settings.json            ├── active-profiles.json
├── agents/*.md              ├── .credentials.json
└── config/                  └── Maschinenspezifisches

Push: bash sync-setup.sh push
Pull: bash sync-setup.sh pull
```

---

## 13. Zusaetzliche Optimierungen

| Feature | Was | Effekt |
|---------|-----|--------|
| **Smart Cache** | Haeufige Abfragen/Tabellen/Ergebnisse cachen | ~95% Token-Ersparnis bei Wiederholungen |
| **Feedback-Loop** | Nutzer bewertet Ergebnisse, Agenten lernen | Qualitaet steigt ueber Zeit |
| **Batch-Processing** | Viele kleine Tasks buendeln | Weniger Overhead |
| **Auto-Approval Stufen** | Routine ohne Bestaetigung, nur Neues/Riskantes fragt | Schneller, autonomer |
| **Model-Fallback** | Bei Rate-Limit automatisch anderes Modell | Kein Stillstand |
| **Fallback-Kette** | Agent versagt → anderer uebernimmt | Kein Stillstand |
| **Health-Check Hook** | SessionStart prueft ob alles funktioniert | Keine boesen Ueberraschungen |
| **Template-Library** | Fertige Code-Patterns zum Wiederverwenden | Schneller + konsistenter |
| **Kosten-Tracking** | Token-Verbrauch pro Agent messen | Verschwender erkennen |

---

## 14. Workflow (optimaler Ablauf)

```
BRIEFING-PHASE:
  Nutzer gibt Auftrag (Terminal/Slack/WhatsApp/Linear)
    → Berater empfaengt
    → Berater stellt alle noetigen Fragen
    → Nutzer beantwortet
    → Berater erstellt Plan + Task-Queue

PLANUNGS-PHASE:
  Berater → Architekt: Design pruefen
    → Architekt: OK oder VETO
    → Bei Veto: Zurueck an Berater → Anpassung → nochmal
    → Analyst: Bestehenden Code analysieren (wenn noetig)

BAU-PHASE (parallel wo moeglich):
  [Coder + Designer] gleichzeitig
    → Sicherheits-Hook (Pre) prueft VOR jedem Write
    → Code/UI wird geschrieben
    → Sicherheits-Hook (Post) prueft NACH jedem Write
    → Doc-Tools laufen automatisch

TEST-PHASE (parallel):
  [Tester + Reviewer] gleichzeitig
    → Tester: Tests + Debug
    → Reviewer: Code-Qualitaet
    → Fehler? → Coder fixt → nochmal pruefen

ABSCHLUSS-PHASE (parallel):
  Reviewer → Commit + Push
  [Doc-Tools + DevOps] gleichzeitig
    → Dokumentation finalisieren
    → CI/CD + Deploy

MELDUNG:
  Berater → Nutzer: "Fertig. Zusammenfassung: ..."
```

---

## 15. Terminal vs. Cloud

| Aspekt | Terminal | Cloud |
|--------|---------|-------|
| Wo | Lokal auf deinem Rechner | VPS/AWS/Railway Server |
| Wann | Wenn du am Rechner sitzt | 24/7, auch wenn Rechner aus |
| Steuerung | Claude Code CLI direkt | Slack/WhatsApp/Linear |
| Agenten | Laufen lokal | Laufen auf Server |
| DB-Zugriff | Ueber Cloud-DB oder lokal | Direkt auf Server |
| Vorteil | Schnell, kein Server noetig | Immer verfuegbar |
| Setup | Claude Code installiert | Docker + Server |

---

## Verwandte Dokumente

- 02-RUNBOOK.md — Bau-Reihenfolge und technische Befehle
- 03-SETUP-ANLEITUNG.md — Detaillierte Einrichtung aller Komponenten
- 04-INSTALLATIONS-GUIDE.md — Schritt-fuer-Schritt Installation (Terminal + Cloud)
- 05-USER-MANUAL-DETAIL-ADMIN.md — Vollstaendiges Benutzerhandbuch (Admin)
- 06-USER-MANUAL-KURZ-ADMIN.md — Kurzanleitung (Admin)
