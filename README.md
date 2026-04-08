# Rushmore — Build Your NBA Legacy

> "Who are your five greatest of all time?"

Rushmore ist eine Web-Plattform auf der NBA-Fans ihre persönlichen All-Time-Listen erstellen, teilen und debattieren können — von casual bis expert, von All-Time GOATs bis zum aktuellen MVP-Race.

**Sprachen:** Deutsch + Englisch
**Zielgruppe:** NBA-Fans aller Art — Casual Fans, Podcast-Hörer, Basketball-Nerds
**Kern-Differenzierung:** Shareable Visuals + Debate-Mechanik + informierte Spielerkarten (mit Stats)

---

## Das Konzept

Rushmore löst ein simples Problem: NBA-Debatten passieren täglich auf Social Media — in Kommentaren, Voice Memos, Podcasts. Aber es gibt kein dediziertes Tool das diese Debatten visuell macht und einfach teilbar macht.

TierMaker existiert, aber ist generisch, kein NBA-Branding, kein Share-to-Social, keine Stats-Kontext.

Rushmore macht das besser.

---

## Die zwei Welten

### 🐐 Legends (zeitlos)
- Top 5 All-Time (frei)
- Best Starting 5 eines Teams (z.B. Bulls All-Time)
- Top 5 nach Position (bester PG/SG/SF/PF/C aller Zeiten)
- Top 5 einer Ära (90s / 2000s / 2010s / heute)

### 🔥 Current Season (wöchentlich relevant)
- Dein MVP-Kandidat
- Dein All-NBA First Team
- Aktuelle Top 10 Spieler
- Rookie of the Year Pick

---

## Core Features

### 1. Listen-Builder
- Einfacher Einstieg: Format wählen → Spieler suchen/browsen → Liste fertig
- Populärste Spieler sofort sichtbar als Bildkacheln
- Filter nach Position / Team / Ära (für Experts, nicht aufdringlich)

### 2. Spielerkarten
- Pro Spieler: Career-Highlights auf einen Blick (PPG / RPG / APG)
- Auszeichnungen: Ringe 🏆 | MVPs 🏅 | All-Star-Appearances ⭐
- Ikonische Pose als Silhouette im Teamfarbton (keine Lizenzprobleme)
- Current Players: aktuelle Saison-Stats daneben

### 3. Share-Output (das Herzstück)
- 9:16 Karte für TikTok / Instagram / Stories
- 1:1 Karte für Twitter / Feed-Posts
- Rushmore-Logo + optionaler Username drauf
- Download oder Direkt-Share

### 4. Debate-Mechanik
- Jede Liste hat einen öffentlichen Link
- "Ich würde das ändern" → eigene Antwort-Liste erstellen
- Community-Upvotes pro Spieler auf einem Platz
- Macht aus einem Tool eine Community

---

## Design-Prinzipien

- **Minimal aber stark:** Teamfarben + Silhouette + Name + Stats — kein Clutter
- **Mobile first:** 9:16 ist die primäre Ausgabe
- **Ikonische Silhouetten:** Spieler in ihrer signature pose (Jumpman, Skyhook, Chalk Toss) — erkennbar, rechtlich sauber. Fallback: Jersey + Nummer im Teamfarbton.
- **Dark Mode:** NBA ist Abend-Entertainment, Dark UI passt besser

---

## Datenstrategie

| Daten | Quelle | Kosten |
|---|---|---|
| Historische Stats (Career) | `basketball-reference-web-scraper` (GitHub) | Kostenlos |
| Aktuelle Saison-Stats | balldontlie API (Free Tier) | Kostenlos |
| Standings / Playoff-Daten | ESPN public API | Kostenlos |
| Auszeichnungen (MVPs etc.) | Einmalig gescrapt → eigene DB | Einmalig |
| Spielerfotos | ❌ Nicht genutzt — Silhouetten statt Fotos | — |

**Strategie:** Einmalig alle historischen Daten laden und in eigener Datenbank speichern. Täglich nur aktuelle Saison-Daten updaten. Kein monatlicher API-Abo.

---

## Tech Stack (Vorschlag)

| Bereich | Tool |
|---|---|
| Frontend | Next.js (React) — schnell, SEO-friendly, i18n eingebaut |
| Backend / API | FastAPI (Python) — passt zu bestehenden Tools |
| Datenbank | PostgreSQL (Spielerdaten) + Redis (Cache) |
| Bild-Generierung | Playwright oder Canvas API (wie Korbleger-Slides) |
| Hosting | Vercel (Frontend) + Railway oder Render (Backend) |
| Sprachen | DE + EN via next-i18next |

---

## Roadmap

### MVP (4–6 Wochen)
- [ ] Spielerdatenbank aufbauen (Top 200 Spieler All-Time)
- [ ] Listen-Builder: "All-Time Top 5 frei"
- [ ] Spielerkarte mit Career-Stats
- [ ] 9:16 Bild-Export
- [ ] Share-Button (Download)
- [ ] DE + EN

### V1 (+ 4 Wochen)
- [ ] Alle Formate (nach Position, Team, Ära)
- [ ] Current Season Section (MVP, All-NBA)
- [ ] Öffentliche Listen mit URL
- [ ] Debate-Feature ("Ich würde das ändern")

### V2 (+ 6 Wochen)
- [ ] User-Accounts + Profile
- [ ] Community-Feed
- [ ] Reveal-Video Export (nicht nur Bild)
- [ ] Direkter Share zu TikTok / Instagram

---

## Projektstruktur (WAT-Framework)

```
tools/        ← Python-Scripts: Datenabruf, Bild-Generierung
workflows/    ← SOPs: Was passiert in welcher Reihenfolge
assets/       ← Logos, Silhouetten, Design-Assets
.tmp/         ← Zwischendateien (nicht committen)
.env          ← API Keys (NIEMALS committen)
CLAUDE.md     ← Agent-Anweisungen (WAT-Framework)
```

---

## Setup (folgt)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Keys eintragen
```

---

## Offene Fragen / Nächste Entscheidungen

1. **Domain:** rushmore.app / rushmore.gg / tryrushmore.com ?
2. **Silhouetten:** selbst erstellen oder Fiverr/Upwork für Top-50-Spieler?
3. **Launch-Kanal:** zuerst über Korbleger-Audience oder eigenständig?
4. **Monetarisierung:** Wann und wie? (Werbung / Premium-Export / Sponsoring)
