# Rushmore Marketing System — Design Spec

**Date:** 2026-04-05
**Status:** Approved
**Scope:** Post-launch marketing automation within the Rushmore project

---

## Overview

Two-component marketing system built after go-live:

1. **Promo Video** — a 15-second Clean & Premium Remotion video (9:16) for X, Instagram, TikTok
2. **Daily Top 5 Script** — a Python script that generates a shareable card with the day's top NBA performers including that day's stats

---

## Component 1: Promo Video (Remotion)

### Specs
- **Format:** 1080 × 1920 (9:16 vertical)
- **Length:** ~15 seconds
- **Style:** Clean & Premium — slow camera moves, smooth transitions, text fades
- **Music:** Cinematic, no vocals (user sources track separately)
- **Output:** MP4, works on all three platforms without re-encoding
- **Location:** `remotion/` subdirectory within the Rushmore project

### Storyboard

| Time | Scene |
|------|-------|
| 0–3s | Black screen → "Who's your Mt. Rushmore?" fades in (white, centered, serif weight) |
| 3–7s | Builder UI: a player chip is dragged into a slot in slow motion |
| 7–12s | Three finished cards in quick cuts — player card, team card, bracket card |
| 12–15s | Rushmore logo + URL + "Build yours." fade in, hold |

### Remotion Structure
```
remotion/
  src/
    compositions/
      PromoVideo.tsx      ← main composition (1080×1920, 15s @ 30fps = 450 frames)
      scenes/
        Intro.tsx         ← 0–3s: text fade-in
        BuilderScene.tsx  ← 3–7s: UI mockup with drag animation
        CardMontage.tsx   ← 7–12s: three card images cycling
        Outro.tsx         ← 12–15s: logo + CTA
    Root.tsx              ← registers composition
  package.json
  remotion.config.ts
```

### Assets needed
- Screenshots of 3 finished cards (player, team, bracket) → captured from the live app
- Rushmore logo PNG (already in `assets/`)
- Background: solid dark `#07080f` with subtle gold accents

---

## Component 2: Daily Top 5 Script

### File
`tools/daily_top5.py`

### What it does
1. Fetches the previous day's top 5 scorers from the NBA API (via existing `live_data.py` patterns)
2. Collects that day's stats per player: PTS, REB, AST, STL, BLK
3. Generates a 1080×1080 PNG card using PIL (extends `generate_card.py` patterns)
4. Saves PNG to `~/Desktop/rushmore-top5-YYYY-MM-DD.png`
5. Prints a ready-to-paste caption to the terminal

### Card Design
- **Title:** "TOP PERFORMERS · [Date]" (auto-generated)
- **Subtitle:** "▲ RUSHMORE"
- **Per player row:** Headshot · Name · Team logo
- **Stats row:** Replaces the career-stats line → shows that day's PTS / REB / AST / STL / BLK
- **Background:** Same trophy/court backgrounds as existing cards (`card_backgrounds/`)

### Output folder structure
```
~/Desktop/rushmore/
  2026-04-04/
    card.png          ← shareable card image
    caption.txt       ← ready-to-paste caption
```

### Caption file (caption.txt)
```
🏀 Top Performers · April 4, 2026

1. N. Jokić — 38 PTS / 14 REB / 9 AST
2. S. Curry — 31 PTS / 4 REB / 7 AST
3. G. Antetokounmpo — 34 PTS / 11 REB / 5 AST
4. L. James — 28 PTS / 8 REB / 10 AST
5. T. Young — 42 PTS / 3 REB / 12 AST

Build your Rushmore 👉 rushmore.app
#NBA #Basketball #Rushmore
```

### User workflow (semi-auto)
1. `python3 tools/daily_top5.py` (run each morning)
2. Ordner `~/Desktop/rushmore/DATUM/` öffnen
3. `card.png` posten + `caption.txt` copy-pasten

### Future upgrade path
- Add `--post` flag that calls social media APIs automatically
- Scheduler via cron or Railway cron job

---

## Project Structure

```
rushmore/
  tools/
    live_data.py          ← existing (NBA API, stats fetching)
    generate_card.py      ← existing (PIL card generation)
    daily_top5.py         ← NEW
  remotion/               ← NEW
    src/
      compositions/...
    package.json
  assets/
    card_backgrounds/     ← reused
    team_logos/           ← reused
```

---

## Out of Scope

- Automatic social media posting (later upgrade)
- TTS narration in the promo video
- Platform-specific video variants (one 9:16 MP4 for all three)
- Pre-launch marketing / teaser content

---

## Dependencies

| Tool | Purpose | Status |
|------|---------|--------|
| Remotion | Video rendering from React | New install in `remotion/` |
| PIL (Pillow) | Card image generation | Already installed |
| NBA API | Daily player stats | Already used in `live_data.py` |
| Node.js | Remotion render | Required for `remotion/` |
