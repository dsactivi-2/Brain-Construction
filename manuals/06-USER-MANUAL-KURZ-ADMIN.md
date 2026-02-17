# Cloud Code Team 02.26 -- Kurzanleitung Admin

> Version: Admin (Vollzugriff) | Stand: Februar 2026
> Einfache Sprache -- fuer alle verstaendlich

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
  |    +---> Analyst        (analysiert Anforderungen)        |
  |    +---> Doc-Scanner    (liest externe Dokumente)         |
  |    +---> DevOps         (Server + Deployment)             |
  |    +---> Dokumentierer  (schreibt Anleitungen)            |
  |                                                           |
  |   [ Brain: HippoRAG 2 + Wissensgraphen ]                 |
  |   [ Datenbanken: Neo4j | Qdrant | Redis ]                |
  |   [ 17 Hooks = automatische Regeln ]                     |
  +-----------------------------------------------------------+
```

**Wichtige Begriffe:**

| Begriff          | Bedeutung                                      |
|------------------|-------------------------------------------------|
| Agent            | Ein KI-Helfer mit einer bestimmten Aufgabe      |
| Hook             | Automatische Regel, die im Hintergrund gilt     |
| Brain/RAG        | Das Gedaechtnis des Systems                     |
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
| 7  | Analyst        | Versteht was der Kunde wirklich braucht     |
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
/logs                 Detaillierte Protokolle
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

**Hooks verwalten** (automatische Regeln):
```
/hooks                Alle 17 Hooks anzeigen
/hooks aktivieren 5   Hook Nr. 5 einschalten
/hooks deaktivieren 3 Hook Nr. 3 ausschalten
```

**Kosten ueberwachen:**
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

**Updates einspielen:**
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
/scan-config KEY WERT            Einstellung aendern
```

**Automatisch:** Alle 7 Tage werden alle URLs automatisch gescannt.

---

## 10. Datenbanken verwalten (nur Admin)

Das System nutzt 3 Datenbanken:

```
  +------------------+------------------------------------+
  |    Datenbank     |    Wofuer?                         |
  +------------------+------------------------------------+
  |    Neo4j         |    Wissen + Zusammenhaenge         |
  |    (Graph)       |    "Wer kennt wen?"                |
  +------------------+------------------------------------+
  |    Qdrant        |    Aehnliche Inhalte finden        |
  |    (Vektor)      |    "Was passt zu meiner Frage?"    |
  +------------------+------------------------------------+
  |    Redis         |    Schneller Zwischenspeicher      |
  |    (Cache)       |    "Was wurde gerade benutzt?"     |
  +------------------+------------------------------------+
```

**Befehle:**
```
/db status            Status aller Datenbanken
/db backup            Sicherung erstellen
/backup               Vollstaendiges System-Backup
```

---

## 11. Server + Deploy (nur Admin)

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

**Befehle:**
```
/deploy               Anwendung veroeffentlichen
/ci                   Build-Pipeline anzeigen
/rollback             Letzte Version wiederherstellen
/server               Server-Status anzeigen
/health               System-Gesundheit pruefen
/env                  Umgebungsvariablen verwalten
```

---

## 12. Alle Commands (Admin)

| Command        | Was passiert                              |
|----------------|-------------------------------------------|
| `/briefing`    | Neuen Auftrag geben                       |
| `/plan`        | Plan anzeigen / genehmigen                |
| `/fortschritt` | Wie weit ist die Arbeit?                  |
| `/katalog`     | Alle Fragen anzeigen                      |
| `/fragen`      | Offene Fragen beantworten                 |
| `/status`      | Status aller Agenten                      |
| `/profil`      | Agenten-Profile anzeigen                  |
| `/review`      | Ergebnisse pruefen                        |
| `/changelog`   | Was wurde geaendert?                      |
| `/stop-alle`   | ALLE Agenten sofort stoppen               |
| `/weiter`      | Gestoppte Agenten weitermachen lassen     |
| `/deploy`      | Anwendung veroeffentlichen                |
| `/ci`          | Build-Pipeline anzeigen                   |
| `/rollback`    | Letzte Version wiederherstellen           |
| `/env`         | Umgebungsvariablen verwalten              |
| `/server`      | Server-Status anzeigen                    |
| `/health`      | System-Gesundheit pruefen                 |
| `/backup`      | Sicherung erstellen                       |
| `/db`          | Datenbanken verwalten                     |
| `/hooks`       | Automatische Regeln verwalten             |
| `/logs`        | Protokolle anzeigen                       |
| `/kosten`      | Kosten-Uebersicht                         |
| `/update`      | System aktualisieren                      |

---

## 13. Probleme loesen

| Problem                          | Loesung                          |
|----------------------------------|----------------------------------|
| Agenten antworten nicht          | `/status` dann `/stop-alle`      |
|                                  | dann `/weiter`                   |
| Agent hat Fehler                 | `/logs` und `/health` pruefen    |
| Kosten zu hoch                   | `/kosten` -- Haiku spart auto.   |
| Aenderung rueckgaengig machen   | `/rollback`                      |
| Datenbank antwortet nicht        | `/db status` und `/health`       |
| Sicherung noetig                 | `/backup`                        |

**Notfall:** `/stop-alle` stoppt sofort alles.
Danach mit `/weiter` neu starten.

---

> **Hilfe noetig?** Schreib in den Slack-Kanal `#cloud-code-team`
> oder sende eine WhatsApp an den Admin-Support.
