# MASTER-CHECKLISTE — Claude Agent Team

Jeder Punkt muss abgehakt werden bevor das Projekt als fertig gilt.

---

## Phase 0: Grundlage
- [x] Git-Repo erstellt
- [x] Ordnerstruktur erstellt
- [x] Master-Checkliste erstellt
- [x] Task-Liste erstellt (8 Tasks mit Abhaengigkeiten)
- [x] Phase 0 committed

## Phase 1: Projektplanung
- [x] Gesamtuebersicht (Was wird gebaut) — 2026-02-17 22:41
- [x] Architektur-Diagramm (Wie haengt alles zusammen) — 2026-02-17 22:41
- [x] 10 Agenten-Profile definiert — 2026-02-17 22:42
  - [x] Berater (Orchestrator) — 2026-02-17 22:42
  - [x] Architekt (Design + Veto) — 2026-02-17 22:42
  - [x] Coder (Implementierung + Refactoring) — 2026-02-17 22:42
  - [x] Tester + Debugger (Tests + Fehleranalyse) — 2026-02-17 22:42
  - [x] Reviewer (Review + Commit + Push) — 2026-02-17 22:42
  - [x] Designer (UI/UX + Design-System) — 2026-02-17 22:42
  - [x] Analyst (Repo-Analyse + Vergleich) — 2026-02-17 22:42
  - [x] Doc-Scanner (Web-Docs scannen + importieren) — 2026-02-17 22:42
  - [x] DevOps (CI/CD + Server + Deploy) — 2026-02-17 22:42
  - [x] Dokumentierer (Docs + API-Registry) — als Hook + Agent bei Bedarf — 2026-02-17 22:42
- [x] 17 Hooks definiert — 2026-02-17 22:43
  - [x] SessionStart (startup) — 2026-02-17 22:43
  - [x] SessionStart (compact) — 2026-02-17 22:43
  - [x] SessionStart (resume) — 2026-02-17 22:43
  - [x] UserPromptSubmit — 2026-02-17 22:43
  - [x] PreToolUse (Write|Edit) — 2026-02-17 22:43
  - [x] PreToolUse (Bash) — 2026-02-17 22:43
  - [x] PostToolUse (Write|Edit) — 2026-02-17 22:43
  - [x] PostToolUse (Bash) — 2026-02-17 22:43
  - [x] PostToolUseFailure — 2026-02-17 22:43
  - [x] PreCompact — 2026-02-17 22:43
  - [x] Stop — 2026-02-17 22:43
  - [x] SubagentStart — 2026-02-17 22:43
  - [x] SubagentStop — 2026-02-17 22:43
  - [x] Notification — 2026-02-17 22:43
  - [x] TeammateIdle — 2026-02-17 22:43
  - [x] TaskCompleted — 2026-02-17 22:43
  - [x] SessionEnd — 2026-02-17 22:43
- [x] Gehirn-System definiert — 2026-02-17 22:44
  - [x] HippoRAG 2 (Wissensgraph + Gedaechtnis) — 2026-02-17 22:44
  - [x] Agentic RAG (Suchsteuerung + Bewertung) — 2026-02-17 22:44
  - [x] Agentic Learning Graphs (Selbst-erweiternd) — 2026-02-17 22:44
- [x] Profil-System definiert — 2026-02-17 22:44
  - [x] Grundprofil (alle Agenten) — 2026-02-17 22:44
  - [x] Rules pro Agent — 2026-02-17 22:44
  - [x] Commands pro Agent — 2026-02-17 22:44
- [x] Fragenkatalog-System definiert — 2026-02-17 22:44
  - [x] Blocker-Fragen — 2026-02-17 22:44
  - [x] Offene Fragen (nicht blockierend) — 2026-02-17 22:44
  - [x] Beantwortete Fragen — 2026-02-17 22:44
- [x] Multi-Model Routing definiert — 2026-02-17 22:45
  - [x] Haiku (einfach) — 2026-02-17 22:45
  - [x] Sonnet (mittel) — 2026-02-17 22:45
  - [x] Opus (komplex) — 2026-02-17 22:45
- [x] Kommunikation definiert — 2026-02-17 22:45
  - [x] Slack-Integration — 2026-02-17 22:45
  - [x] WhatsApp-Integration — 2026-02-17 22:45
  - [x] Linear-Integration — 2026-02-17 22:45
- [x] Connectoren definiert — 2026-02-17 22:45
  - [x] GitHub MCP — 2026-02-17 22:45
  - [x] Notion MCP — 2026-02-17 22:45
  - [x] Eigene Connectoren (erweiterbar) — 2026-02-17 22:45
- [x] Web-Scanner definiert — 2026-02-17 22:45
  - [x] URL-Liste mit Markierung (Global/Projekt) — 2026-02-17 22:45
  - [x] 7-Tage Scan-Zyklus — 2026-02-17 22:45
  - [x] Aenderungserkennung — 2026-02-17 22:45
  - [x] Auto-Import in HippoRAG 2 — 2026-02-17 22:45
- [x] Sync-System definiert — 2026-02-17 22:45
  - [x] Git-basiert — 2026-02-17 22:45
  - [x] install.sh (Merge statt Ueberschreiben) — 2026-02-17 22:45
  - [x] LOCAL.md fuer lokale Anpassungen — 2026-02-17 22:45
- [x] Smart Cache definiert — 2026-02-17 22:46
- [x] Feedback-Loop definiert — 2026-02-17 22:46
- [x] Batch-Processing definiert — 2026-02-17 22:46
- [x] Auto-Approval Stufen definiert — 2026-02-17 22:46
- [x] Model-Fallback definiert — 2026-02-17 22:46
- [x] Fallback-Kette (Agent versagt) definiert — 2026-02-17 22:46
- [x] Health-Check Hook definiert — 2026-02-17 22:46
- [x] Template-Library definiert — 2026-02-17 22:46
- [x] Kosten-Tracking Hook definiert — 2026-02-17 22:46
- [x] Phase 1 gepusht — 2026-02-17 22:47

## Phase 2: Runbook
- [x] Bau-Reihenfolge definiert (12 Schritte) — 2026-02-17 22:50
- [x] Befehle pro Schritt — 2026-02-17 22:50
- [x] Abhaengigkeiten zwischen Schritten — 2026-02-17 22:50
- [x] Fehlerbehandlung pro Schritt — 2026-02-17 22:51
- [x] Rollback-Plan pro Schritt — 2026-02-17 22:51
- [x] Phase 2 gepusht — 2026-02-17 22:51

## Phase 3: Setup-Anleitung
- [x] Server-Anforderungen (Light/Standard/Heavy + 3 Varianten) — 2026-02-17 22:53
- [x] Datenbank-Setup — 2026-02-17 22:54
  - [x] Neo4j (Graph-DB) — Self-Hosted + Managed + Einstellungen erklaert + Verbindung — 2026-02-17 22:54
  - [x] Vektor-DB (Qdrant) — Self-Hosted + Managed + Einstellungen erklaert + Verbindung — 2026-02-17 22:54
  - [x] Redis (Cache) — Self-Hosted + Managed + Einstellungen erklaert + Verbindung — 2026-02-17 22:54
- [x] Docker + Docker Compose Setup (Mac/Windows/Linux) — 2026-02-17 22:55
- [x] MCP-Server Einrichtung (RAG-API, Doc-Scanner, GitHub, Notion) — 2026-02-17 22:55
- [x] Claude API Einrichtung — 2026-02-17 22:55
- [x] Slack/WhatsApp/Linear Webhook Setup — 2026-02-17 22:55
- [x] GitHub Repo + CI/CD Setup — 2026-02-17 22:56
- [x] DNS + SSL (Caddy Reverse Proxy) — 2026-02-17 22:56
- [x] Empfehlungen: Welcher Anbieter fuer was — 2026-02-17 22:56
- [x] Phase 3 gepusht — 2026-02-17 22:56

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
