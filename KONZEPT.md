# Rushmore — Konzept & Projektstart

> "Who are your five greatest of all time?"

NBA-Fans debattieren täglich über GOATs — auf Twitter, TikTok, in Podcasts. Rushmore macht diese Debatten visuell, teilbar und interaktiv. Kein Tool macht das heute gut. TierMaker ist der nächste Vergleich, aber generisch, ohne NBA-Branding, ohne Share-Flow, ohne Stats.

---

## Die Idee

User erstellt eine persönliche NBA-Liste (Top 5, Starting 5 etc.), bekommt eine schöne 9:16 Karte zum Teilen — und kann die Listen anderer kommentieren und debattieren.

**Sprachen:** Deutsch + Englisch
**Zielgruppe:** Casual NBA-Fans bis Hardcore-Statistik-Nerds
**Differenzierung:** Informierte Listen (mit Stats), starkes Share-Format, Debate-Mechanik

---

## Die zwei Welten

### 🐐 Legends (zeitlos, evergreen)
- Top 5 All-Time (frei wählbar)
- Best Starting 5 eines Teams (z.B. Bulls All-Time)
- Top 5 nach Position (bester PG / SG / SF / PF / C aller Zeiten)
- Top 5 einer Ära (90s / 2000s / 2010s / heute)

### 🔥 Current Season (wöchentlich relevant, Repeat-Visits)
- Dein MVP-Kandidat
- Dein All-NBA First Team
- Aktuelle Top 10 Spieler
- Rookie of the Year

---

## Core Features

### 1. Listen-Builder
- Format wählen → Spieler suchen / browsen → fertig
- Populärste Spieler sofort als Kacheln sichtbar (Jordan, LeBron, Kobe...)
- Filter nach Position / Team / Ära (für Experts, nicht aufdringlich)
- Casual: in 30 Sekunden fertig. Expert: geht so tief wie er will.

### 2. Spielerkarte (pro Spieler)
- Career-Highlights: PPG / RPG / APG
- Auszeichnungen: Ringe 🏆 | MVPs 🏅 | All-Star-Appearances ⭐
- Silhouette in ikonischer Pose + Teamfarben (rechtlich sauber, kein Foto)
- Current Players: aktuelle Saison-Stats daneben

### 3. Share-Output (das Herzstück)
- 9:16 Karte für TikTok / Instagram / Stories
- 1:1 Karte für Twitter / Feed
- Rushmore-Logo + optionaler Username drauf
- Download oder Direkt-Share

### 4. Debate-Mechanik (macht es sticky)
- Jede Liste hat öffentlichen Link
- "Ich würde das ändern" → eigene Antwort-Liste erstellen
- Community-Upvotes pro Spieler auf einem Platz
- Debatte läuft direkt auf der Seite — beide teilen den Link

---

## Design-Prinzipien

- **Minimal aber stark:** Teamfarben + Silhouette + Name + Stats — kein Clutter
- **Mobile first:** 9:16 ist die primäre Ausgabe
- **Dark Mode:** NBA ist Abend-Entertainment, passt besser
- **Keine echten Spielerfotos** — Lizenzproblem. Stattdessen:

### Silhouetten-Strategie
**Phase 1 (0 Aufwand):** Jersey + Nummer + Teamfarbe als Fallback für alle Spieler
**Phase 2 (~$20, einmalig):** Automatisch generierte Silhouetten via Gemini API

Pipeline für Silhouetten-Generierung:
1. Spielerfoto holen (Wikipedia API — kostenlos, lizenzfrei)
2. Hintergrund entfernen (`rembg` Python-Library, lokal, kostenlos)
3. Silhouette generieren (Gemini Imagen API, ~$0.03–0.04 pro Bild)
4. PNG speichern in `assets/silhouettes/player_id.png`

Kosten: ~$8 für 200 Spieler, ~$20 für 500 Spieler — einmalig, danach lokal verfügbar.

---

## Datenstrategie

| Daten | Quelle | Kosten |
|---|---|---|
| Historische Stats (Career) | `basketball-reference-web-scraper` (Python, GitHub) | Kostenlos |
| Aktuelle Saison-Stats | balldontlie API (Free Tier) | Kostenlos |
| Standings / Playoff-Daten | ESPN public API (undokumentiert, weit verbreitet) | Kostenlos |
| Auszeichnungen (MVPs, All-NBA) | Einmalig scrapen → eigene Datenbank | Einmalig |
| Spielerfotos (für Silhouetten) | Wikipedia API (lizenzfrei) | Kostenlos |
| Silhouetten generieren | Gemini Imagen API | ~$20 einmalig |

**Strategie:** Einmalig alle historischen Daten + Silhouetten aufbauen. Täglich nur Current-Season-Daten aktualisieren. Kein monatlicher API-Abo.

---

## Tech Stack

| Bereich | Tool |
|---|---|
| Frontend | Next.js (React) — SEO-freundlich, i18n eingebaut |
| Backend / API | FastAPI (Python) |
| Datenbank | PostgreSQL (Spielerdaten) + Redis (Cache) |
| Bild-Generierung | Playwright oder Canvas API |
| Silhouetten | Gemini Imagen API (einmalig) |
| Hosting | Vercel (Frontend) + Railway oder Render (Backend) |
| Sprachen | DE + EN via next-i18next |

---

## Datenquellen (Links)

- Basketball Reference: https://www.basketball-reference.com
- basketball-reference-web-scraper API Docs: https://jaebradley.github.io/basketball_reference_web_scraper/api/
- Sportradar (Backup, kostenpflichtig): https://developer.sportradar.com
- SportsLogos.net (Team-Logos): https://www.sportslogos.net/teams/list_by_league/6/
- Gemini Image Generation: https://gemini.google/de/overview/image-generation/

---

## Roadmap

### MVP (4–6 Wochen)
- [ ] Spielerdatenbank aufbauen (Top 200 All-Time)
- [ ] Silhouetten-Pipeline (Gemini API)
- [ ] Listen-Builder: "All-Time Top 5 frei"
- [ ] Spielerkarte mit Career-Stats
- [ ] 9:16 Bild-Export + Download
- [ ] DE + EN

### V1 (+4 Wochen)
- [ ] Alle Formate (nach Position, Team, Ära)
- [ ] Current Season Section (MVP, All-NBA)
- [ ] Öffentliche Listen-Links
- [ ] Debate-Feature

### V2 (+6 Wochen)
- [ ] User-Accounts + Profile
- [ ] Community-Feed
- [ ] Reveal-Video Export
- [ ] Direkt-Share zu TikTok / Instagram

### Phase 3+
- [ ] n8n / Automation
- [ ] Mehrere Sportarten
- [ ] Website-Launch (Roadmap Phase 4)

---

## Offene Entscheidungen

1. **Domain:** rushmore.app / rushmore.gg / tryrushmore.com?
2. **Launch-Kanal:** Eigenständig oder über bestehende NBA-Audience?
3. **Monetarisierung:** Wann und wie? (Werbung / Premium-Export / Sponsoring)
4. **Silhouetten:** Top 10 ikonische Posen priorisieren (Jordan Jumpman, Kareem Skyhook etc.)

---

## Projektstruktur (WAT-Framework)

```
KONZEPT.md    ← dieses Dokument
CLAUDE.md     ← Agent-Anweisungen
tools/        ← Python-Scripts (Datenabruf, Bild-Generierung, Silhouetten)
workflows/    ← SOPs pro Aufgabe
assets/       ← Silhouetten, Logos, Design-Assets
.tmp/         ← Zwischendateien (nicht committen)
.env          ← API Keys (NIEMALS committen)
```
