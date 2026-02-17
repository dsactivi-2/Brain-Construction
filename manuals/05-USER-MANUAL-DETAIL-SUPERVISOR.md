# USER-MANUAL DETAIL — Supervisor-Version

## Cloud Code Team 02.26

**Version:** 1.0.0
**Rolle:** Supervisor (Management-Zugriff, kein System-/DB-Zugang)
**Stand:** 2026-02-17

---

## INHALTSVERZEICHNIS

| Kapitel | Titel | Seite |
|---------|-------|:-----:|
| 1 | Systemuebersicht | 3 |
| 2 | Agenten steuern | 6 |
| 3 | Fragenkatalog verwalten | 10 |
| 4 | Fortschritt ueberwachen | 12 |
| 5 | Reviews pruefen | 14 |
| 6 | Reports + Statistiken | 16 |
| 7 | Kommunikation | 18 |
| 8 | Profil-Verwaltung | 20 |
| 9 | Verfuegbare Commands | 22 |
| 10 | Fehlerbehebung | 24 |

---

## Seite 3 — Kapitel 1: Systemuebersicht

Das Cloud Code Team ist ein Multi-Agent-System mit 10 Agenten. Als Supervisor kannst du:
- Agenten Auftraege geben und ueberwachen
- Fragenkatalog verwalten
- Reviews einsehen und freigeben
- Fortschritt und Kosten ueberwachen

Du kannst NICHT:
- System-Einstellungen aendern
- Datenbanken administrieren
- Server/Docker verwalten
- Hook-Konfiguration aendern

### 1.1 Die 10 Agenten

| # | Agent | Rolle |
|---|-------|-------|
| 1 | Berater | Orchestrator — nimmt Auftraege entgegen, stellt Rueckfragen, koordiniert das Team |
| 2 | Architekt | Design + Veto — entwirft die technische Architektur |
| 3 | Coder | Implementierung + Refactoring — schreibt den Code |
| 4 | Tester+Debugger | Tests + Fehleranalyse — testet und debuggt |
| 5 | Reviewer | Review + Commit + Push — prueft Code-Qualitaet |
| 6 | Designer | UI/UX + Design-System — gestaltet Oberflaechen |
| 7 | Analyst | Repo-Analyse + Vergleich — analysiert Codebasen |
| 8 | Doc-Scanner | Web-Docs scannen + importieren — haelt Wissen aktuell |
| 9 | DevOps | CI/CD + Server + Deploy — betreibt die Infrastruktur |
| 10 | Dokumentierer | Docs + API-Registry — dokumentiert alles |

### 1.2 Das Gedaechtnis (6-Schichten-Gehirn)

Das System verfuegt ueber ein 6-Schichten-Gedaechtnis. Es merkt sich automatisch alles aus frueheren Sessions. Du musst nichts manuell speichern. Wenn du sagst "mach weiter wie gestern", weiss das System was gemeint ist.

### 1.3 Automatische Qualitaetssicherung (Hooks)

Im Hintergrund laufen 17 automatische Regeln (Hooks H-01 bis H-17), die Qualitaet sichern. Diese sind vom Admin konfiguriert und nicht aenderbar.

---

## Seite 6 — Kapitel 2: Agenten steuern

### 2.1 Auftrag geben

```
/briefing
→ Strukturiertes Briefing starten
→ Berater stellt Rueckfragen
→ Du beantwortest
→ Agenten arbeiten autonom
```

### 2.2 Aufgabenplan erstellen

```
/plan
→ Aufgabenplan erstellen
→ Zeigt geplante Schritte und Zustaendigkeiten
→ Geschaetzte Fertigstellung
```

### 2.3 Fortschritt pruefen

```
/fortschritt
→ Zeigt Status aller Agenten
→ Welcher Task bei welchem Agent
→ Geschaetzte Fertigstellung
```

### 2.4 Fragenkatalog beantworten

```
/katalog
→ Zeigt alle offenen Fragen
→ Blocker zuerst (Agenten warten!)
→ Beantworte und Agenten arbeiten weiter
```

### 2.5 Alles stoppen

```
/stop-alle
→ Stoppt sofort alle Agenten
→ Nur im Notfall verwenden
```

---

## Seite 10 — Kapitel 3: Fragenkatalog

| Typ | Was tun |
|-----|---------|
| BLOCKER | Sofort beantworten — Agent wartet! |
| OFFEN | Wenn Zeit ist — Agent arbeitet mit Empfehlung weiter |
| BEANTWORTET | Nichts — Archiv |

---

## Kapitel 4: Fortschritt ueberwachen — Seite 12

### 4.1 Echtzeit-Status

Der `/status`-Command zeigt den aktuellen Stand aller Agenten:

| Status | Bedeutung |
|--------|-----------|
| Aktiv | Agent arbeitet gerade |
| Wartend | Agent wartet auf Eingabe oder Abhaengigkeit |
| Fertig | Aufgabe abgeschlossen |
| Fehler | Problem aufgetreten — Eingriff noetig |

### 4.2 Fortschritts-Tracking

- `/fortschritt` — Prozentuale Fertigstellung pro Agent
- `/changelog` — Liste aller Aenderungen seit letztem Check

### 4.3 Wann eingreifen?

- Agent steht auf "Fehler" laenger als 5 Minuten → `/stop-alle` und neu starten
- Agent laeuft im Kreis → `/review` anfordern
- Abhaengigkeit blockiert → `/weiter` erzwingen oder blockierten Agent pruefen

---

## Seite 14 — Kapitel 5: Reviews pruefen

```
/review
→ Zeigt letztes Review-Ergebnis
→ Reviewer hat bereits geprueft
→ Du kannst zusaetzlich freigeben oder ablehnen
```

---

## Kapitel 6: Reports + Statistiken — Seite 16

### 6.1 Verfuegbare Reports

| Command | Was es zeigt |
|---------|-------------|
| `/status` | Aktueller Stand aller Agenten |
| `/fortschritt` | Fertigstellung pro Aufgabe |
| `/changelog` | Aenderungshistorie |

### 6.2 Reports lesen

Reports zeigen: Was wurde gemacht, von welchem Agent, wann, und was steht noch aus. Bei Problemen den Admin informieren.

---

## Kapitel 7: Kommunikation — Seite 18

### 7.1 Benachrichtigungen

Das System sendet automatisch Benachrichtigungen bei:
- Aufgabe fertig
- Fehler aufgetreten
- Review noetig
- Blocker-Frage gestellt

### 7.2 Kanaele

Benachrichtigungen kommen ueber die vom Admin konfigurierten Kanaele (Slack, WhatsApp oder Linear). Als Supervisor siehst du alle Team-Benachrichtigungen.

---

## Kapitel 8: Profil-Verwaltung — Seite 20

### 8.1 Eigenes Profil

`/profil` — Zeigt dein aktuelles Profil (Supervisor-Rolle, verfuegbare Commands).

### 8.2 Profil-Einschraenkungen

Als Supervisor kannst du dein Profil einsehen, aber NICHT aendern. Profilaenderungen sind Admin-only.

---

## Seite 22 — Kapitel 9: Verfuegbare Commands (Supervisor)

| Command | Was |
|---------|-----|
| `/briefing` | Strukturiertes Briefing starten |
| `/plan` | Aufgabenplan erstellen |
| `/fortschritt` | Status aller Agenten |
| `/katalog` | Fragenkatalog |
| `/stop-alle` | Alle stoppen |
| `/weiter` | Naechsten Schritt ausfuehren |
| `/review` | Review einsehen |
| `/changelog` | Aenderungen anzeigen |
| `/status` | System-Status |
| `/profil` | Aktive Profile |
| `/fragen` | Offene Fragen anzeigen |

**Nicht verfuegbar:** `/deploy`, `/env`, `/ci`, `/rollback`, `/health`, `/backup`, `/db`, `/server`, `/hooks`, `/logs`, `/kosten`, `/update`, `/delegate`, `/scan-*`, `/core-*`, `/memory-*`, `/conv-*`, DB-Admin, Hook-Konfiguration

---

## Kapitel 10: Fehlerbehebung — Seite 24

### 10.1 Haeufige Probleme

| Problem | Loesung |
|---------|---------|
| Agent antwortet nicht | `/status` pruefen, dann `/stop-alle` und neu starten |
| Aufgabe haengt fest | `/review` anfordern, Ergebnis pruefen |
| Falsches Ergebnis | `/fragen` pruefen ob Blocker-Fragen offen sind |
| Benachrichtigung fehlt | Admin kontaktieren (Webhook-Problem) |

### 10.2 Eskalation

Wenn ein Problem nicht in 10 Minuten loesbar ist → Admin kontaktieren mit:
1. Was passiert ist
2. Welcher Agent betroffen ist
3. Screenshot oder Fehlertext
