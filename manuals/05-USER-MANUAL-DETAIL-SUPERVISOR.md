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
| 2 | Agenten steuern | 5 |
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

---

## Seite 5 — Kapitel 2: Agenten steuern

### 2.1 Auftrag geben

```
/briefing
→ Berater stellt Rueckfragen
→ Du beantwortest
→ Agenten arbeiten autonom
```

### 2.2 Fortschritt pruefen

```
/fortschritt
→ Zeigt Status aller Agenten
→ Welcher Task bei welchem Agent
→ Geschaetzte Fertigstellung
```

### 2.3 Fragenkatalog beantworten

```
/katalog
→ Zeigt alle offenen Fragen
→ Blocker zuerst (Agenten warten!)
→ Beantworte und Agenten arbeiten weiter
```

### 2.4 Alles stoppen

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

## Seite 14 — Kapitel 5: Reviews pruefen

```
/review
→ Zeigt letztes Review-Ergebnis
→ Reviewer hat bereits geprueft
→ Du kannst zusaetzlich freigeben oder ablehnen
```

---

## Seite 22 — Kapitel 9: Verfuegbare Commands (Supervisor)

| Command | Was |
|---------|-----|
| `/briefing` | Neuen Auftrag starten |
| `/plan` | Aufgabenplan anzeigen |
| `/fortschritt` | Status aller Agenten |
| `/katalog` | Fragenkatalog |
| `/stop-alle` | Alle stoppen |
| `/weiter` | Nach Blocker fortsetzen |
| `/review` | Review einsehen |
| `/changelog` | Aenderungen anzeigen |
| `/status` | System-Status |
| `/profil` | Aktive Profile |
| `/fragen` | Offene Fragen |

**Nicht verfuegbar:** `/deploy`, `/env`, `/ci`, `/rollback`, `/health`, DB-Admin, Hook-Konfiguration
