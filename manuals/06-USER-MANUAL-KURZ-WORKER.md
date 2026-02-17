# KURZANLEITUNG — Worker

## Cloud Code Team 02.26

**Rolle:** Worker | **Stand:** 2026-02-17

---

## 1. Was ist das?

Ein KI-Team programmiert fuer dich. Du sagst was du brauchst.
Das Team plant, baut, testet und liefert. Du beantwortest nur Fragen.

```
  +-------+    Auftrag     +----------+    Code    +----------+
  |  DU   | ------------->  |  KI-TEAM | ---------> | ERGEBNIS |
  +-------+                 +----------+            +----------+
      ^                          |
      |     Rueckfragen          |
      +--------------------------+
```

---

## 2. So gibst du einen Auftrag

Starte mit `/briefing` und beschreibe was du brauchst.

```
Du:       /briefing
Du:       Baue eine Login-Seite mit Google-Login

Berater:  Fragen:
          1. Braucht es Passwort-Reset?
          2. Welches Design-Framework?

Du:       Ja Passwort-Reset. Tailwind CSS.

          --> Team arbeitet jetzt autonom
          --> Du bekommst Bescheid wenn fertig
```

---

## 3. Fragen beantworten

Das Team stellt manchmal Fragen. Schau mit `/katalog` nach.

```
  FRAGEN-AMPEL:

  [!!!] ROT    = BLOCKER  --> Team wartet! Schnell antworten!
  [...] GELB   = OFFEN    --> Antworten wenn du Zeit hast.
```

ROT: Das Team kann nicht weiter ohne deine Antwort.
GELB: Das Team arbeitet weiter. Kein Stress.

Nach einer Blocker-Antwort: `/weiter` eingeben.

---

## 4. Fortschritt pruefen

Jederzeit `/fortschritt` eingeben. Du siehst:

```
  Auftrag: Login-Seite
  +--[####------]-- 40%
  |
  +-- Planung ......... OK
  +-- Backend .......... LAEUFT
  +-- Frontend ......... WARTET
  +-- Tests ............ WARTET
```

---

## 5. Deine Commands

| Command        | Was passiert                     |
|----------------|----------------------------------|
| `/briefing`    | Neuen Auftrag starten            |
| `/fortschritt` | Wie weit ist das Team?           |
| `/katalog`     | Offene Fragen anzeigen           |
| `/weiter`      | Nach Blocker-Antwort weitermachen|
| `/status`      | System-Status anzeigen           |
| `/fragen`      | Alle Fragen auflisten            |

**Das ist alles.** Andere Commands gibt es fuer dich nicht.

Kein Zugriff auf: Agenten-Verwaltung, Einstellungen, Deploy,
Datenbanken, Code-Reviews, Agenten stoppen.

---

## 6. Hilfe bei Problemen

**Problem: Team antwortet nicht.**
--> `/status` eingeben. Laeuft das System?

**Problem: Frage ist rot aber ich weiss die Antwort nicht.**
--> Schreib was du weisst. "Bin nicht sicher, mach einen Vorschlag."

**Problem: Ergebnis ist falsch.**
--> Neuen `/briefing` starten. Beschreibe was anders sein soll.

**Problem: Ich sehe keine Fragen aber Team wartet.**
--> `/katalog` eingeben. Vielleicht neue Fragen.

---

*Kurzanleitung v1.0 — Cloud Code Team 02.26 — Nur fuer Worker-Rolle*
