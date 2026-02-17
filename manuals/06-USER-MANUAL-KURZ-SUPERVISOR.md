# Kurzanleitung: Supervisor -- Cloud Code Team 02.26

> Version: Supervisor (Management-Zugriff, kein System-/DB-Zugang)

---

## 1. Was ist das?

Du bist der **Supervisor**. Du gibst Auftraege, beantwortest Fragen
und pruefst Ergebnisse. Du fasst die Technik nicht an.

```
+-----------------------------------------------------+
|                   CLOUD CODE TEAM                    |
|                                                      |
|   +-------------+                                    |
|   |     DU      |  Supervisor                        |
|   | (Auftraege, |                                    |
|   |  Kontrolle) |                                    |
|   +------+------+                                    |
|          |                                           |
|          | gibst Auftraege, pruefst Ergebnisse        |
|          v                                           |
|   +------+------+     +-------------+                |
|   |   Agenten   |<--->| Fragenkatalog|               |
|   | (arbeiten)  |     | (Fragen an  |                |
|   +------+------+     |  dich)      |                |
|          |             +-------------+                |
|          v                                           |
|   +------+------+                                    |
|   |   System    |  <-- Hier hast du KEINEN Zugriff   |
|   | (Server,DB) |                                    |
|   +-------------+                                    |
+-----------------------------------------------------+
```

---

### Das Gedaechtnis

Das System hat ein 6-Schichten-Gedaechtnis:
- Es merkt sich ALLES aus frueheren Sessions
- Wichtiges ist sofort verfuegbar (Core Memory)
- Der Rest wird bei Bedarf automatisch abgerufen
Du musst nichts manuell speichern oder erinnern.

---

## 2. Schnellstart in 3 Schritten

```
Schritt 1          Schritt 2          Schritt 3
+-----------+      +-----------+      +-----------+
| /briefing |----->| /plan     |----->| /status   |
| Briefing  |      | Aufgaben- |      | Wie weit  |
| starten   |      | plan      |      | sind sie? |
+-----------+      +-----------+      +-----------+
```

1. **`/briefing`** eintippen -- Strukturiertes Briefing starten. Beschreibe deinen Auftrag.
2. **`/plan`** eintippen -- Aufgabenplan erstellen.
3. **`/status`** eintippen -- Du schaust, wie weit die Agenten sind.

Das war's. Du bist startklar.

---

## 3. Auftrag geben (Beispiel-Gespraech)

```
DU:    /briefing
SYSTEM: Strukturiertes Briefing gestartet. Was soll gemacht werden?
DU:    Bitte die Login-Seite ueberarbeiten. Neues Design nach Vorlage X.
SYSTEM: Briefing erfasst. Erstelle Aufgabenplan...
DU:    /plan
SYSTEM: Aufgabenplan erstellt. Agent B arbeitet daran.
DU:    /status
SYSTEM: Agent B: Login-Seite -- 30% fertig, keine Blocker.
```

**Tipps:**
- Schreib klar, was du willst.
- Ein Auftrag = eine Aufgabe. Nicht alles auf einmal.
- Mit `/fortschritt` siehst du Details zum Fortschritt.

---

## 4. Fragen beantworten

Agenten stellen dir Fragen. Es gibt zwei Arten:

```
  DRINGEND (Blocker)            KANN WARTEN (Offen)
  +-----------------------+     +-----------------------+
  |  !!  ROT  !!          |     |     GELB              |
  |  Agent wartet!        |     |     Agent arbeitet     |
  |  Sofort antworten!    |     |     weiter.            |
  +-----------------------+     +-----------------------+
  Beispiel:                     Beispiel:
  "Welche Datenbank              "Soll der Button blau
   sollen wir nutzen?"            oder gruen sein?"
```

**So beantwortest du Fragen:**
1. `/katalog` eintippen -- Du siehst alle offenen Fragen.
2. Rote Fragen (Blocker) zuerst beantworten.
3. Gelbe Fragen, wenn du Zeit hast.

---

## 5. Fortschritt pruefen

| Befehl          | Was du siehst                        |
|-----------------|--------------------------------------|
| `/status`       | Kurzer Ueberblick: wer macht was     |
| `/fortschritt`  | Details: Prozent, Blocker, Zeitplan  |
| `/briefing`     | Strukturiertes Briefing starten      |

**Taeglich empfohlen:** Morgens `/status`, bei neuem Auftrag `/briefing`.

---

## 6. Reviews pruefen und freigeben

Wenn ein Agent fertig ist, bekommst du ein Review.

1. `/review` eintippen -- Du siehst alle fertigen Arbeiten.
2. Lies dir die Zusammenfassung durch.
3. **Freigeben** = Arbeit ist gut, kann weiter.
4. **Ablehnen** = Agent muss nachbessern. Schreib dazu, was fehlt.

---

## 7. Alle deine Commands

| Command         | Was es tut                                |
|-----------------|-------------------------------------------|
| `/briefing`     | Strukturiertes Briefing starten           |
| `/plan`         | Aufgabenplan erstellen                    |
| `/fortschritt`  | Detaillierten Fortschritt anzeigen        |
| `/katalog`      | Fragenkatalog oeffnen (Fragen beantworten)|
| `/stop-alle`    | Alle Agenten anhalten                     |
| `/weiter`       | Angehaltene Agenten weiterlaufen lassen   |
| `/review`       | Reviews anzeigen und freigeben            |
| `/changelog`    | Aenderungsprotokoll anzeigen              |
| `/status`       | Kurzer Status aller Agenten               |
| `/profil`       | Dein Profil anzeigen                      |
| `/fragen`       | Offene Fragen anzeigen                    |

---

## 8. Was du NICHT kannst

Diese Befehle sind **gesperrt** fuer dich:

| Gesperrt        | Warum                                     |
|-----------------|-------------------------------------------|
| `/deploy`       | Nur Admins duerfen deployen               |
| `/env`          | Umgebungsvariablen sind Systemsache       |
| `/ci`           | CI/CD Pipeline ist Adminsache             |
| `/rollback`     | Nur Admins duerfen zurueckrollen          |
| `/health`       | Server-Monitoring ist Adminsache          |
| `/backup`       | Backups verwaltet der Admin               |
| `/db`           | Datenbank-Zugriff nur fuer Admins         |
| `/server`       | Server-Verwaltung nur fuer Admins         |
| `/hooks`        | Hook-Konfiguration nur fuer Admins        |
| `/logs`         | System-Logs nur fuer Admins               |
| `/kosten`       | Kostendetails nur fuer Admins             |
| `/update`       | System-Updates nur fuer Admins            |

**Wenn du etwas davon brauchst:** Frag den Admin.

---

## 9. Probleme loesen (FAQ)

**F: Ein Agent antwortet nicht mehr.**
A: `/status` pruefen. Dann `/stop-alle` und `/weiter` versuchen.
   Hilft das nicht? Den Admin fragen.

**F: Ich sehe keine Fragen im Katalog.**
A: `/katalog` nochmal ausfuehren. Keine Fragen = alles laeuft gut.

**F: Ein Review sieht falsch aus.**
A: Ablehnen und genau beschreiben, was falsch ist. Der Agent
   bekommt dein Feedback und arbeitet nach.

**F: Ich will etwas deployen.**
A: Das kannst du nicht. Schreib dem Admin eine Nachricht.

**F: Die Kosten sind zu hoch.**
A: `/status` zeigt dir den groben Stand. Fuer Details brauchst du
   den Admin (der hat `/kosten`).

**F: Ich hab aus Versehen `/stop-alle` gedrueckt.**
A: Kein Problem. `/weiter` bringt alle Agenten zurueck.

---

*Kurzanleitung Supervisor -- Cloud Code Team 02.26*
