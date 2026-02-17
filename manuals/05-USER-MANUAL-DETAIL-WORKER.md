# USER-MANUAL DETAIL — Worker-Version

## Cloud Code Team 02.26

**Version:** 1.0.0
**Rolle:** Worker (Nur eigene Tasks, kein Admin-/Management-Zugang)
**Stand:** 2026-02-17

---

## INHALTSVERZEICHNIS

| Kapitel | Titel | Seite |
|---------|-------|:-----:|
| 1 | Was ist das Cloud Code Team? | 3 |
| 2 | Einen Auftrag geben | 4 |
| 3 | Fragen beantworten | 6 |
| 4 | Ergebnisse pruefen | 8 |
| 5 | Verfuegbare Commands | 10 |
| 6 | Probleme loesen | 11 |

---

## Seite 3 — Kapitel 1: Was ist das Cloud Code Team?

Ein KI-Team das fuer dich programmiert. Du gibst einen Auftrag und das Team:
- Plant die Umsetzung
- Schreibt den Code
- Testet alles
- Macht Code-Review
- Committed und pusht

Du musst nur Fragen beantworten wenn welche kommen.

Das System merkt sich alles automatisch. Du musst nichts speichern.

---

## Seite 4 — Kapitel 2: Einen Auftrag geben

```
Du: "Baue mir eine Login-Seite"

Berater: "Ich habe ein paar Fragen:
  1. Welche Auth-Methode? (JWT empfohlen)
  2. Social Login noetig? (Google, GitHub)
  3. Passwort-Reset?"

Du: "JWT, nur Google, ja Passwort-Reset"

→ Team arbeitet autonom
→ Du bekommst Notification wenn fertig
```

---

## Seite 6 — Kapitel 3: Fragen beantworten

Manchmal hat das Team Fragen. Du siehst sie:
- Im Terminal: `/katalog`
- Auf Slack/WhatsApp: Als Nachricht

**Rote Fragen (BLOCKER):** Team wartet — bitte schnell antworten!
**Gelbe Fragen (OFFEN):** Team arbeitet weiter — antworten wenn du Zeit hast.

---

## Kapitel 4: Ergebnisse pruefen — Seite 8

### 4.1 Status pruefen

`/status` — Zeigt ob dein Auftrag noch laeuft oder fertig ist.

### 4.2 Ergebnis ansehen

`/fortschritt` — Zeigt was bisher erledigt wurde und was noch aussteht.

### 4.3 Nicht zufrieden?

Wenn das Ergebnis nicht passt:
1. Beschreibe genau, was anders sein soll
2. Nutze `/weiter` um den naechsten Versuch zu starten
3. Bei groesseren Problemen den Supervisor informieren

---

## Seite 10 — Kapitel 5: Verfuegbare Commands (Worker)

| Command | Was |
|---------|-----|
| `/briefing` | Strukturiertes Briefing starten |
| `/fortschritt` | Wie weit ist das Team? |
| `/katalog` | Offene Fragen anzeigen |
| `/weiter` | Naechsten Schritt ausfuehren |
| `/status` | System-Status |
| `/fragen` | Offene Fragen anzeigen |

**Nicht verfuegbar:** Alles andere (Deploy, Admin, Reviews, DB, Server, etc.)

---

## Kapitel 6: Probleme loesen — Seite 11

### 6.1 Haeufige Probleme

| Problem | Was tun |
|---------|---------|
| Agent antwortet nicht | Warten (max. 2 Min.), dann Supervisor fragen |
| Falsches Ergebnis | Genauer beschreiben was du willst |
| Frage vom System | `/fragen` eingeben und beantworten |
| Etwas unklar | Supervisor fragen |

### 6.2 Hilfe holen

Fuer alle Probleme, die du nicht selbst loesen kannst: Supervisor kontaktieren.
