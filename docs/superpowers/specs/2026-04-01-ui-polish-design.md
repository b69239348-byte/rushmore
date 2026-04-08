# UI Polish — Sticky Panel, Spielerliste & Team-Logos

**Datum:** 2026-04-01

---

## Übersicht

Drei UX/Design-Verbesserungen:

1. **CardBuilderPanel klebt beim Scrollen** — Panel verschwindet wenn man in der Spielerliste runterscrollt
2. **Spielerliste zu lang** — rechte Spalte hat leeren Platz unter dem Panel
3. **Team-Logos** — visuell einarbeiten um die Karte attraktiver und teilenswerter zu machen

---

## Fix 1+2: Layout-Sticky

**Root Cause:** `layout.tsx` nutzt `min-h-screen` (nicht `h-screen`). Dadurch scrollt die ganze Seite statt die inneren Spalten. `h-full` in `SplitCategoryPage` löst sich auf Content-Höhe auf, nicht Viewport-Höhe.

**Fix:**

`SplitCategoryPage.tsx` — aside erhält `sticky top-0 self-start max-h-screen overflow-y-auto`:

```tsx
// Vorher:
<aside className="hidden w-80 shrink-0 overflow-y-auto border-l border-border-subtle p-4 md:block">
  <div className="sticky top-4">
    <CardBuilderPanel ... />
  </div>
</aside>

// Nachher:
<aside className="hidden w-80 shrink-0 border-l border-border-subtle p-4 md:block sticky top-0 self-start max-h-screen overflow-y-auto">
  <CardBuilderPanel ... />
</aside>
```

- `sticky top-0` — klebt am Viewport beim Scrollen
- `self-start` — Höhe = Content-Höhe (kein leerer Kasten darunter)
- `max-h-screen overflow-y-auto` — falls Panel mal höher als Viewport wird

**Betroffene Dateien:** `web/src/components/categories/SplitCategoryPage.tsx`

---

## Fix 3: Team-Logos

### Design-Entscheid

**Watermark-Logo** (Option B) — großes Team-Logo als sehr dezentes Hintergrundbild rechts in jeder Row. Gibt der Karte Tiefe und Persönlichkeit ohne zu überladen. Opacity: ~6-8%.

**Gilt für:** Spielerliste (Web) + generierte Karte (PNG). Beide.

**All-Time-Spieler:** `teams[0]` = Hauptteam (Draft-Team — Jordan→CHI, Kobe→LAL, Bird→BOS etc.)  
**Aktuell-Spieler:** `team` Feld (direkter String aus live_data)

### Umsetzungsschritte

#### A) Logo-Assets herunterladen

- Script: `tools/download_team_logos.py`
- Quelle: NBA CDN (`https://cdn.nba.com/logos/nba/{TEAM_ID}/primary/L/logo.png`)
- Team-ID-Mapping via `nba_api.stats.static.teams`
- Ziel: `assets/team_logos/{ABBREVIATION}.png` (30 Dateien)
- Fallback wenn nicht verfügbar: farbiger Text-Badge

#### B) Frontend — PlayerList

`web/src/components/categories/PlayerList.tsx`:
- Spielerkarte bekommt `position: relative; overflow: hidden`
- Team-Logo als `<img>` absolut positioniert: rechts zentriert, `width: 80px; height: 80px; opacity: 0.06; object-fit: contain`
- Quelle: direkt NBA CDN `https://cdn.nba.com/logos/nba/{TEAM_ID}/global/L/logo.svg`
- Braucht Team-ID-Mapping (Abbr → NBA-ID) als Konstante im Frontend
- Fallback: kein Logo (stilles `display:none` wenn Bild nicht lädt)
- Nur rendern wenn `player.team` oder `player.teams[0]` vorhanden

#### C) Backend — generate_card.py

`tools/generate_card.py`:
- Neue Funktion `_load_team_logo(team_abbr, size)` — lädt PNG aus `assets/team_logos/`, gibt RGBA-Image zurück
- In der Row-Render-Schleife: Logo rechts zentriert in der Row als Hintergrund compositen
  - Größe: ~80% der Row-Höhe
  - Position: `x = WIDTH - PAD - logo_size`, `y = row_y + (ROW_H - logo_size) // 2`
  - Opacity: ~15-20 (von 255) — sehr dezent, wirkt als Textur
  - Wird gezeichnet **nach** dem Row-Hintergrund, **vor** allen Text/Headshot-Elementen
- Team-Abbr ermitteln: `player.get("team") or (player.get("teams") or [""])[0]`
- Graceful fallback: wenn Logo-Datei fehlt, Row wird normal ohne Watermark gerendert

### Datenfluss

```
players.json / live_data → team abbreviation (z.B. "CHI")
→ assets/team_logos/CHI.png
→ generate_card.py: composite als Badge auf Headshot
→ PlayerList.tsx: <img src="/api/team-logo/CHI"> oder direkt NBA CDN
```

Für das Frontend können die Logos direkt vom NBA CDN geladen werden (keine lokale Kopie nötig), um den Build einfach zu halten. Für PIL (generate_card.py) müssen sie lokal als Asset liegen.

---

## Nicht in Scope

- Kein Redesign der Karten-Proportionen
- Kein neues Farbschema
- Keine Änderung der Spieler-Stats-Anzeige

---

## Erfolgskriterien

- CardBuilderPanel ist immer sichtbar beim Scrollen durch die Spielerliste (Desktop)
- Rechte Spalte hat keinen leeren Raum unter dem Panel
- Team-Logo als Badge erkennbar auf jeder Spielerkarte in der Spielerliste
- Team-Logo als Badge auf der generierten PNG-Karte (rechts unten am Headshot)
- Fallback auf farbigen Text-Badge wenn Bild nicht verfügbar
