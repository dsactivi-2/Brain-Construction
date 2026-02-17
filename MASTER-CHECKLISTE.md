# MASTER-CHECKLISTE — Claude Agent Team

Jeder Punkt muss abgehakt werden bevor das Projekt als fertig gilt.

---

## Phase 0: Grundlage
- [x] Git-Repo erstellt
- [x] Ordnerstruktur erstellt
- [x] Master-Checkliste erstellt
- [x] Task-Liste erstellt (8 Tasks mit Abhaengigkeiten)
- [ ] Phase 0 gepusht

## Phase 1: Projektplanung
- [ ] Gesamtuebersicht (Was wird gebaut)
- [ ] Architektur-Diagramm (Wie haengt alles zusammen)
- [ ] 10 Agenten-Profile definiert
  - [ ] Berater (Orchestrator)
  - [ ] Architekt (Design + Veto)
  - [ ] Coder (Implementierung + Refactoring)
  - [ ] Tester + Debugger (Tests + Fehleranalyse)
  - [ ] Reviewer (Review + Commit + Push)
  - [ ] Designer (UI/UX + Design-System)
  - [ ] Analyst (Repo-Analyse + Vergleich)
  - [ ] Doc-Scanner (Web-Docs scannen + importieren)
  - [ ] DevOps (CI/CD + Server + Deploy)
  - [ ] Dokumentierer (Docs + API-Registry) — als Hook + Agent bei Bedarf
- [ ] 17 Hooks definiert
  - [ ] SessionStart (startup)
  - [ ] SessionStart (compact)
  - [ ] SessionStart (resume)
  - [ ] UserPromptSubmit
  - [ ] PreToolUse (Write|Edit)
  - [ ] PreToolUse (Bash)
  - [ ] PostToolUse (Write|Edit)
  - [ ] PostToolUse (Bash)
  - [ ] PostToolUseFailure
  - [ ] PreCompact
  - [ ] Stop
  - [ ] SubagentStart
  - [ ] SubagentStop
  - [ ] Notification
  - [ ] TeammateIdle
  - [ ] TaskCompleted
  - [ ] SessionEnd
- [ ] Gehirn-System definiert
  - [ ] HippoRAG 2 (Wissensgraph + Gedaechtnis)
  - [ ] Agentic RAG (Suchsteuerung + Bewertung)
  - [ ] Agentic Learning Graphs (Selbst-erweiternd)
- [ ] Profil-System definiert
  - [ ] Grundprofil (alle Agenten)
  - [ ] Rules pro Agent
  - [ ] Commands pro Agent
- [ ] Fragenkatalog-System definiert
  - [ ] Blocker-Fragen
  - [ ] Offene Fragen (nicht blockierend)
  - [ ] Beantwortete Fragen
- [ ] Multi-Model Routing definiert
  - [ ] Haiku (einfach)
  - [ ] Sonnet (mittel)
  - [ ] Opus (komplex)
- [ ] Kommunikation definiert
  - [ ] Slack-Integration
  - [ ] WhatsApp-Integration
  - [ ] Linear-Integration
- [ ] Connectoren definiert
  - [ ] GitHub MCP
  - [ ] Notion MCP
  - [ ] Eigene Connectoren (erweiterbar)
- [ ] Web-Scanner definiert
  - [ ] URL-Liste mit Markierung (Global/Projekt)
  - [ ] 7-Tage Scan-Zyklus
  - [ ] Aenderungserkennung
  - [ ] Auto-Import in HippoRAG 2
- [ ] Sync-System definiert
  - [ ] Git-basiert
  - [ ] install.sh (Merge statt Ueberschreiben)
  - [ ] LOCAL.md fuer lokale Anpassungen
- [ ] Smart Cache definiert
- [ ] Feedback-Loop definiert
- [ ] Batch-Processing definiert
- [ ] Auto-Approval Stufen definiert
- [ ] Model-Fallback definiert
- [ ] Fallback-Kette (Agent versagt) definiert
- [ ] Health-Check Hook definiert
- [ ] Template-Library definiert
- [ ] Kosten-Tracking Hook definiert
- [ ] Phase 1 gepusht + geprueft

## Phase 2: Runbook
- [ ] Bau-Reihenfolge definiert
- [ ] Befehle pro Schritt
- [ ] Abhaengigkeiten zwischen Schritten
- [ ] Fehlerbehandlung pro Schritt
- [ ] Rollback-Plan pro Schritt
- [ ] Phase 2 gepusht + geprueft

## Phase 3: Setup-Anleitung
- [ ] Server-Anforderungen (Light/Standard/Heavy)
- [ ] Datenbank-Setup
  - [ ] Neo4j (Graph-DB) — Anbieter + Einrichtung + Verbindung
  - [ ] Vektor-DB (Qdrant/ChromaDB) — Anbieter + Einrichtung + Verbindung
  - [ ] Redis (Cache) — Anbieter + Einrichtung + Verbindung
- [ ] Docker + Docker Compose Setup
- [ ] MCP-Server Einrichtung
- [ ] Claude API Einrichtung
- [ ] Slack/WhatsApp/Linear Webhook Setup
- [ ] GitHub Repo + CI/CD Setup
- [ ] DNS + SSL (wenn Cloud)
- [ ] Empfehlungen: Welcher Anbieter fuer was
- [ ] Phase 3 gepusht + geprueft

## Phase 4: Installations-Guide
- [ ] Terminal-Version (Schritt fuer Schritt)
  - [ ] Windows
  - [ ] Mac
- [ ] Cloud-Version (Schritt fuer Schritt)
  - [ ] Server aufsetzen
  - [ ] Docker deployen
  - [ ] Services verbinden
  - [ ] Testen
- [ ] Phase 4 gepusht + geprueft

## Phase 5: User-Manual Detail
- [ ] Inhaltsverzeichnis mit Seitennummern
- [ ] Alle Funktionen dokumentiert
- [ ] Alle Einstellungen dokumentiert
- [ ] Funktions- und Endpoint-Registry (IDs: FN-001, EP-001)
- [ ] Version: Admin
- [ ] Version: Supervisor
- [ ] Version: Worker
- [ ] Phase 5 gepusht + geprueft

## Phase 6: User-Manual Kurz
- [ ] Einfache Sprache
- [ ] Skizzen und Diagramme
- [ ] Schritt-fuer-Schritt Anleitungen
- [ ] Version: Admin
- [ ] Version: Supervisor
- [ ] Version: Worker
- [ ] Phase 6 gepusht + geprueft

## Phase 7: Finaler Review
- [ ] Alle Phasen geprueft
- [ ] Alle Tasks erledigt
- [ ] Keine offenen Punkte
- [ ] Alles auf Desktop
- [ ] Finaler Push
- [ ] Bereit zum Bauen
