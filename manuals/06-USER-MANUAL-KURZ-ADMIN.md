# Cloud Code Team 02.26 -- Kurzanleitung Admin

> Version: Admin (Vollzugriff) | Stand: Februar 2026
> Einfache Sprache -- fuer alle verstaendlich

> Ausfuehrliche Version: 05-USER-MANUAL-DETAIL-ADMIN.md

---

## 1. Was ist das?

Das Cloud Code Team ist eine Gruppe von **10 KI-Agenten**, die zusammen
Software bauen. Du gibst einen Auftrag -- die Agenten erledigen ihn.

Als **Admin** hast du die volle Kontrolle ueber alles:
Agenten, Datenbanken, Server, Einstellungen und Kosten.

```
  +-----------------------------------------------------------+
  |                    CLOUD CODE TEAM                        |
  +-----------------------------------------------------------+
  |                                                           |
  |   DU (Admin)                                              |
  |    |                                                      |
  |    v                                                      |
  |   Berater/Orchestrator  (verteilt die Arbeit)             |
  |    |                                                      |
  |    +---> Architekt      (plant die Struktur)              |
  |    +---> Coder          (schreibt den Code)               |
  |    +---> Tester         (prueft + findet Fehler)          |
  |    +---> Reviewer       (kontrolliert Qualitaet)          |
  |    +---> Designer       (gestaltet Oberflaechen)          |
  |    +---> Analyst        (analysiert Repos + Code)          |
  |    +---> Doc-Scanner    (liest externe Dokumente)         |
  |    +---> DevOps         (Server + Deployment)             |
  |    +---> Dokumentierer  (schreibt Anleitungen)            |
  |                                                           |
  |   [ Brain: HippoRAG 2 + Agentic RAG + Learning Graphs ]  |
  |   [ Cloud: Neo4j | Qdrant | Redis | PostgreSQL (Shared)] |
  |   [ Lokal: Agent-Core JSON (Agent-Only) ]                |
  |   [ 17 Hooks = automatische Regeln ]                     |
  +-----------------------------------------------------------+
```

**Wichtige Begriffe:**

| Begriff          | Bedeutung                                      |
|------------------|-------------------------------------------------|
| Agent            | Ein KI-Helfer mit einer bestimmten Aufgabe      |
| Hook             | Automatische Regel, die im Hintergrund gilt     |
| Brain/RAG        | Das 6-Schichten-Gedaechtnis (siehe Abschnitt 10) |
| MCP              | Verbindung zu externen Diensten (GitHub etc.)   |
| Fragenkatalog    | Liste aller offenen und beantworteten Fragen    |

---

## 2. Schnellstart

So gibst du deinen ersten Auftrag -- in 5 Schritten:

```
  Schritt 1       Schritt 2       Schritt 3
  +--------+      +--------+      +--------+
  | Profil |----->| Brief- |----->| Plan   |
  | laden  |      | ing    |      | pruefen|
  +--------+      +--------+      +--------+
                                       |
                  Schritt 5       Schritt 4
                  +--------+      +--------+
                  | Ergeb- |<-----| Fort-  |
                  | nisse  |      | schritt|
                  +--------+      +--------+
```

1. **Profil laden** -- Das System kennenlernen
   ```
   /profil
   ```

2. **Briefing geben** -- Beschreibe was du willst
   ```
   /briefing "Baue eine Login-Seite mit E-Mail und Passwort"
   ```

3. **Plan pruefen** -- Der Berater zeigt dir den Plan
   ```
   /plan
   ```
   Lies den Plan. Passt alles? Dann bestaetigen.

4. **Fortschritt beobachten** -- Schau wie es laeuft
   ```
   /fortschritt
   ```

5. **Ergebnisse pruefen** -- Am Ende alles kontrollieren
   ```
   /review
   ```

---

## 3. Die 10 Agenten

Jeder Agent hat eine klare Aufgabe:

| Nr | Agent          | Aufgabe (einfach erklaert)                  |
|----|----------------|---------------------------------------------|
| 1  | Berater        | Nimmt deinen Auftrag an, verteilt Arbeit    |
| 2  | Architekt      | Plant wie alles zusammenpasst               |
| 3  | Coder          | Schreibt den eigentlichen Programmcode      |
| 4  | Tester         | Prueft ob alles funktioniert, findet Fehler |
| 5  | Reviewer       | Kontrolliert die Code-Qualitaet             |
| 6  | Designer       | Gestaltet wie es aussieht (UI/UX)           |
| 7  | Analyst        | Analysiert Repos und vergleicht Code        |
| 8  | Doc-Scanner    | Liest Handbuecher und Dokumentationen       |
| 9  | DevOps         | Kuemmert sich um Server und Deployment      |
| 10 | Dokumentierer  | Schreibt Anleitungen und Erklaerungen       |

**So arbeiten sie zusammen:**

```
  Du ---> Berater <---> Analyst
            |
            +---> Architekt ---> Coder ---> Tester ---+
            |         |                        |      |
            |         v                  Fehler? -----+
            |     Doc-Scanner                  |
            |                                  v
            +---> Designer              Reviewer
            |                                  |
            +---> Dokumentierer <---------------+
                       |
                       v
                    DevOps ---> FERTIG!
```

---

## 4. Einen Auftrag geben

Beispiel-Gespraech:

```
DU:     /briefing "REST-API fuer Benutzerverwaltung.
         Registrieren und einloggen."

SYSTEM: Briefing erhalten. Fragen:
        [BLOCKER] Welche Datenbank?
        [OFFEN]   Passwort-Reset Funktion?

DU:     /fragen
        Frage 1: PostgreSQL
        Frage 2: Ja, mit E-Mail-Link

SYSTEM: Plan wird erstellt...

DU:     /plan

SYSTEM: Phase 1: Schema (Architekt)   Phase 2: API (Coder)
        Phase 3: Tests (Tester)        Phase 4: Review
        Phase 5: Doku                  Zeit: ~45 Min

DU:     Sieht gut aus, bitte starten.
```

---

## 5. Fragen beantworten

Die Agenten stellen manchmal Fragen. Es gibt 3 Typen:

```
  +==========================================+
  |  BLOCKER     = Arbeit ist gestoppt!      |
  |  (rot)         Muss SOFORT beantwortet   |
  |                werden.                   |
  +==========================================+
  |  OFFEN       = Arbeit geht weiter,       |
  |  (gelb)        aber Antwort waere gut.   |
  +------------------------------------------+
  |  BEANTWORTET = Erledigt, nur zur Info.   |
  |  (gruen)                                 |
  +------------------------------------------+
```

**Fragen anzeigen und beantworten:**
```
/katalog              Alle Fragen anzeigen
/fragen               Offene Fragen beantworten
```

**Tipp:** Beantworte BLOCKER-Fragen immer zuerst!

---

## 6. Fortschritt pruefen

So siehst du, wie weit die Arbeit ist:

```
/fortschritt          Gesamtuebersicht
/status               Status aller Agenten
docker compose logs   Detaillierte Protokolle (Shell-Befehl, kein Slash-Command)
```

**Was die Status-Anzeige bedeutet:**

```
  Agent        Status        Fortschritt
  -------      ------        -----------
  Architekt    [FERTIG]      ############ 100%
  Coder        [ARBEITET]    ########---- 67%
  Tester       [WARTET]      ------------ 0%
  Reviewer     [WARTET]      ------------ 0%
```

| Symbol    | Bedeutung                           |
|-----------|-------------------------------------|
| FERTIG    | Aufgabe abgeschlossen               |
| ARBEITET  | Gerade dabei                        |
| WARTET    | Wartet bis Vorgaenger fertig ist     |
| BLOCKIERT | Wartet auf deine Antwort            |
| FEHLER    | Problem aufgetreten                 |

---

## 7. Ergebnisse pruefen

Wenn die Arbeit fertig ist:

1. **Review starten:**
   ```
   /review
   ```
2. **Changelog ansehen** (Was wurde gemacht?):
   ```
   /changelog
   ```
3. **Alles ok?** Dann freigeben oder Aenderungen verlangen.

---

## 8. Einstellungen aendern (nur Admin)

Als Admin kannst du das System anpassen:

**Hooks verwalten** (automatische Regeln, System-Commands):
```
/hooks                Alle 17 Hooks anzeigen
/hooks aktivieren 5   Hook Nr. 5 einschalten
/hooks deaktivieren 3 Hook Nr. 3 ausschalten
```

**Kosten ueberwachen** (System-Command):
```
/kosten               Zeigt Kosten-Uebersicht
```

**Multi-Model Routing** -- Das System waehlt automatisch
das passende KI-Modell:

```
  +----------+   einfache Aufgabe   +--------+
  |          |---------------------->| Haiku  |  (schnell, guenstig)
  |  Berater |   mittlere Aufgabe   +--------+
  |          |---------------------->| Sonnet |  (ausgewogen)
  |          |   schwere Aufgabe     +--------+
  |          |---------------------->| Opus   |  (stark, teurer)
  +----------+                       +--------+
```

**Updates einspielen** (System-Command):
```
/update               System aktualisieren
```

---

## 9. Web-Scanner: Dokumentationen ueberwachen

Der Doc-Scanner liest Webseiten und speichert das Wissen im Gehirn.
So kennt das Team immer die neueste Dokumentation.

**Neue Webseite hinzufuegen:**

```
/scan-add URL SCOPE --name "NAME" --beschreibung "WOFUER?"
```

```
  Beispiel:
  /scan-add https://react.dev/docs global \
    --name "React Docs" \
    --beschreibung "Offizielle React-Doku. Hooks, Komponenten."

  /scan-add https://api.mein-projekt.com projekt \
    --name "Unsere API" \
    --beschreibung "Backend REST API. Endpoints, Auth."
```

**Global vs Projekt — wann was?**

```
  GLOBAL                          PROJEKT
  +---------------------------+   +---------------------------+
  | Fuer ALLE Projekte        |   | Nur fuer EIN Projekt      |
  |                           |   |                           |
  | Beispiele:                |   | Beispiele:                |
  | - Python Docs             |   | - Deine eigene API-Doku   |
  | - React Docs              |   | - Internes Wiki           |
  | - MDN Web Docs            |   | - Projekt-Anforderungen   |
  +---------------------------+   +---------------------------+
```

**So funktioniert der Scanner:**

```
  URL hinzufuegen ──→ Seite lesen ──→ Mit letztem Mal vergleichen
                                              │
                                    ┌─────────┴──────────┐
                                    │                    │
                                 Gleich             Geaendert
                                    │                    │
                                 Nichts              In Gehirn
                                  tun                speichern
                                                        │
                                                  Nachricht an dich
                                                  "React Docs geaendert!"
```

**Alle Scanner-Befehle:**

```
/scan-add URL global|projekt     Neue Webseite hinzufuegen
/scan-list                       Alle ueberwachten Webseiten zeigen
/scan URL                        Webseite jetzt sofort scannen
/scan-diff URL                   Was hat sich geaendert?
/kb-import PFAD global|projekt   Lokale Datei importieren (PDF, MD, YAML)
/scan-remove URL|NUMMER          Ueberwachte Webseite entfernen
/scan-edit URL|NUMMER --PARAM W  Einstellungen einer Webseite aendern
/scan-config KEY WERT            Einstellung aendern
```

**Automatisch:** Alle 7 Tage werden alle URLs automatisch gescannt.

---

## 10. Das Gehirn: 6 Schichten Erinnerung

Dein Team vergisst NIE etwas. Es hat 6 Arten von Gedaechtnis:

```
  IMMER SICHTBAR (im Kontext):
  ┌─────────────────────────────────────────────┐
  │  1. Core Memory                              │
  │     Wichtigste Fakten — immer da             │
  │     Dein Name, Projekt, Entscheidungen       │
  │                                              │
  │  2. Auto-Recall                              │
  │     Passende Erinnerungen werden             │
  │     automatisch bei jeder Frage geladen      │
  └─────────────────────────────────────────────┘

  EXTERN (wird bei Bedarf gesucht):
  ┌─────────────────────────────────────────────┐
  │  3. HippoRAG 2     → Wissensgraph           │
  │  4. Agentic RAG    → Intelligente Suche      │
  │  5. Learning Graphs → Waechst mit der Zeit   │
  │  6. Recall Memory   → Komplette Chat-Historie│
  └─────────────────────────────────────────────┘
```

**Einfach gesagt:** Schicht 1+2 sind immer da (wie dein Kurzzeitgedaechtnis).
Schicht 3-6 werden bei Bedarf geholt (wie Nachschlagen im Buch).

**Shared vs. Agent-Only:**
- Shared (Cloud): Alle 30-40 Agenten teilen Wissen (Redis, Neo4j, Qdrant, PostgreSQL)
- Agent-Only (Lokal): Jeder Agent hat eigene Notizen ([AKTUELLE-ARBEIT], [FEHLER-LOG])

**Das Gehirn lernt und vergisst wie ein Mensch:**
- Konsolidierung: Woechentlich werden Rohdaten zu Wissen verdichtet
- Vergessen: Ungenutzte Erinnerungen verlieren an Relevanz (nach 90 Tagen)
- Gewichtung: Wichtige Erinnerungen (Score 9) werden bevorzugt geladen

**Befehle nach Schicht:**

```
Schicht 1 — Core Memory:
/core-read BLOCK              Core-Memory-Block lesen (z.B. USER, PROJEKT)
/core-update BLOCK "WERT"     Core-Memory-Block aktualisieren

Schicht 2 — Auto-Recall (Mem0):
/memory-search SUCHBEGRIFF    Erinnerungen suchen
/memory-store "FAKT"          Einen Fakt speichern
/memory-list                  Alle Erinnerungen auflisten
/memory-get ID                Einzelne Erinnerung abrufen
/memory-forget ID             Eine Erinnerung loeschen

Schicht 6 — Recall Memory:
/conv-search SUCHBEGRIFF      Konversationshistorie durchsuchen
/conv-search-date VON BIS     Konversationen nach Datum suchen
```

---

## 11. Datenbanken verwalten (nur Admin)

Das System nutzt 4 Cloud-Datenbanken (Shared) + lokale Dateien (Agent-Only):

```
  CLOUD (Shared — alle 30-40 Agenten):
  +------------------+------------------------------------+
  |    Neo4j         |    Wissen + Zusammenhaenge (S3/S5) |
  |    (Graph)       |    "Wer kennt wen?"                |
  +------------------+------------------------------------+
  |    Qdrant        |    Aehnliche Inhalte finden (S2/S3)|
  |    (Vektor)      |    "Was passt zu meiner Frage?"    |
  +------------------+------------------------------------+
  |    Redis         |    Shared Cache + Event-Bus        |
  |    (Cache)       |    Core Memory Shared + Warm-Up    |
  +------------------+------------------------------------+
  |    PostgreSQL    |    Komplette Chat-Historie (S6)    |
  |    (Relational)  |    Connection Pool: 40 Agenten     |
  +------------------+------------------------------------+

  LOKAL (Agent-Only — pro Agent):
  +------------------+------------------------------------+
  |  Agent-Core JSON |    [AKTUELLE-ARBEIT], [FEHLER-LOG] |
  |  (Datei)         |    Nur dieser Agent, 0.04ms        |
  +------------------+------------------------------------+
```

**System-Commands:**
```
/db status            Status aller Datenbanken
/db backup            Sicherung erstellen
/backup               Vollstaendiges System-Backup
```

---

## 12. Server + Deploy (nur Admin)

**Anwendung veroeffentlichen (Deploy):**

```
  Code fertig
       |
       v
  +---------+     +---------+     +---------+
  |  Build  |---->|  Test   |---->| Deploy  |
  | (bauen) |     |(pruefen)|     |(online) |
  +---------+     +---------+     +---------+
                                       |
                       Problem? -------+
                       |               |
                       v               v
                  /rollback        LIVE!
```

**Agent-Commands:**
```
/deploy               Anwendung veroeffentlichen
/ci                   Build-Pipeline anzeigen
/rollback             Letzte Version wiederherstellen
/health               System-Gesundheit pruefen
/env                  Umgebungsvariablen verwalten
```

**System-Commands:**
```
/server               Server-Status anzeigen (Admin Shell-Befehl)
```

---

## 13. Alle Commands (Admin)

**Agent-Commands (Slash-Commands):**

| Command            | Was passiert                              |
|--------------------|-------------------------------------------|
| `/briefing`        | Strukturiertes Briefing starten           |
| `/plan`            | Aufgabenplan erstellen                    |
| `/fortschritt`     | Wie weit ist die Arbeit?                  |
| `/katalog`         | Alle Fragen anzeigen                      |
| `/fragen`          | Offene Fragen anzeigen                    |
| `/status`          | Status aller Agenten                      |
| `/profil`          | Agenten-Profile anzeigen                  |
| `/weiter`          | Naechsten Schritt ausfuehren              |
| `/stop-alle`       | ALLE Agenten sofort stoppen               |
| `/review`          | Ergebnisse pruefen                        |
| `/changelog`       | Was wurde geaendert?                      |
| `/deploy`          | Anwendung veroeffentlichen                |
| `/ci`              | Build-Pipeline anzeigen                   |
| `/rollback`        | Letzte Version wiederherstellen           |
| `/env`             | Umgebungsvariablen verwalten              |
| `/health`          | System-Gesundheit pruefen                 |
| `/core-read`       | Core-Memory-Block lesen                   |
| `/core-update`     | Core-Memory-Block aktualisieren           |
| `/memory-search`   | Erinnerungen suchen                       |
| `/memory-store`    | Einen Fakt speichern                      |
| `/memory-list`     | Alle Erinnerungen auflisten               |
| `/memory-get`      | Einzelne Erinnerung abrufen               |
| `/memory-forget`   | Eine Erinnerung loeschen                  |
| `/conv-search`     | Konversationshistorie durchsuchen         |
| `/conv-search-date`| Konversationen nach Datum suchen          |
| `/scan-add`        | URL zur Ueberwachung hinzufuegen          |
| `/scan-list`       | Alle ueberwachten URLs anzeigen           |
| `/scan`            | URL sofort scannen                        |
| `/scan-diff`       | Aenderungen seit letztem Scan zeigen      |
| `/kb-import`       | Lokale Dateien in KB importieren          |
| `/scan-remove`     | Ueberwachte URL entfernen                 |
| `/scan-edit`       | Einstellungen einer URL aendern           |
| `/scan-config`     | Scanner-Konfiguration anzeigen/aendern    |

**Admin Shell-Befehle (System-Commands, keine Agent-Commands):**

| Befehl             | Was passiert                              |
|--------------------|-------------------------------------------|
| `docker compose logs` | Detaillierte Protokolle anzeigen       |
| `/server`          | Server-Status anzeigen                    |
| `/backup`          | Sicherung erstellen                       |
| `/db`              | Datenbanken verwalten                     |
| `/hooks`           | Automatische Regeln verwalten             |
| `/kosten`          | Kosten-Uebersicht                         |
| `/update`          | System aktualisieren                      |

---

## 14. Probleme loesen

| Problem                          | Loesung                          |
|----------------------------------|----------------------------------|
| Agenten antworten nicht          | `/status` dann `/stop-alle`      |
|                                  | dann `/weiter`                   |
| Agent hat Fehler                 | `docker compose logs` und `/health` pruefen |
| Kosten zu hoch                   | `/kosten` -- Haiku spart auto.   |
| Aenderung rueckgaengig machen   | `/rollback`                      |
| Datenbank antwortet nicht        | `/db status` und `/health`       |
| Sicherung noetig                 | `/backup`                        |

**Notfall:** `/stop-alle` stoppt sofort alles.
Danach mit `/weiter` neu starten.

---

> **Hilfe noetig?** Schreib in den Slack-Kanal `#cloud-code-team`
> oder sende eine WhatsApp an den Admin-Support.
