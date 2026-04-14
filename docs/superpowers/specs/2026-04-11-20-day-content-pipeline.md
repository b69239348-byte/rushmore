# Rushmore — 20-Day NBA Content Pipeline
**Date:** 2026-04-11  
**Phase:** NBA Playoffs Push (Regular Season End → Playoffs Round 1)  
**Goal:** 90% automated daily content pipeline across TikTok, Instagram, X with minimal daily effort

---

## Context

Rushmore is a web app (rushmore.cards) that lets users build shareable NBA Top-5 cards. Soft-launched 2026-04-10. TikTok performing best (~500 views, ~40 likes per post). The NBA enters its highest-engagement window: Play-In (Apr 14–17) → Playoffs R1 (Apr 18+).

**Brand Voice:** Analytisch fundiert + Haltung + Humor. Stats first, opinion second, always in English.

**Social accounts:**
- TikTok: @rushmore.card
- Instagram: @rushmore.cards
- X: @rushmorecard

---

## Architecture

### Orchestrator
`tools/daily_pipeline.py` — runs daily at 06:00 UTC via GitHub Actions.

Responsibilities:
1. Read `content/calendar.yaml` — what's planned today
2. Check for yesterday's NBA games → generate Daily Top 5 if games played
3. Check if playoffs active → generate Playoff Matchup Card
4. Check for award-day flag in YAML → generate Award Card
5. Generate captions per platform (template system)
6. Write all outputs to `output/YYYY-MM-DD/`
7. Send Telegram notification with previews

### File Structure

```
tools/
├── daily_pipeline.py          # NEW: Orchestrator
├── generate_mvp_race_card.py  # NEW
├── generate_award_card.py     # NEW (generic: ROTY, MIP, All-NBA)
├── generate_playoff_card.py   # NEW (matchup + series stats)
├── generate_debate_card.py    # NEW (renders YAML content)
├── generate_dpoy_card.py      # existing
├── daily_top5.py              # existing
└── live_data.py               # existing + extended

content/
└── calendar.yaml              # NEW: 20-day debate/funny/historical content

output/
└── YYYY-MM-DD/
    ├── top5_feed.png
    ├── top5_story.png
    ├── [type]_feed.png
    ├── [type]_story.png
    └── captions/
        ├── tiktok.txt
        ├── instagram.txt
        └── x.txt

.github/workflows/
└── daily_cards.yml            # NEW: Cron trigger
```

---

## Card Types

### 1. Daily Top 5 (existing, automated)
- Data: `live_data.py` → yesterday's top performers by points
- Output: feed (1080x1080) + story (1080x1920)
- Always runs when NBA games occurred

### 2. MVP Race Card (new, automated)
- Data: `live_data.py` extended → PTS/G, Win Shares, PER for top 5 candidates
- Layout: reuses DPOY card pattern (shield → crown icon)
- Output: feed + story

### 3. Award Card (new, automated/semi-auto)
- Generic template for: ROTY, MIP, All-NBA, Scoring Title
- Data-driven where possible; YAML-defined for announced awards
- Icon system: trophy, star, crown — per award type

### 4. Playoff Matchup Card (new, automated)
- Data: NBA API playoffs bracket + series record
- Shows: Team A vs Team B, seeds, series score (e.g. "OKC leads 2-1"), key stat leaders
- Runs automatically once playoffs bracket is set

### 5. Debate / Funny / Historical Card (new, YAML-driven)
- Content pre-written in `content/calendar.yaml`
- `generate_debate_card.py` renders any list of 5 players/items with title + subtitle
- No live data required — pure design render

---

## Design Rules (all new generators)

All new card generators inherit constants from `generate_card.py`:
- `WIDTH=1080`, `HEIGHT=1920` (story), feed scale = `canvas_h/HEIGHT`
- `PAD=48` — minimum padding on all sides
- Team logos: max 80px on feed cards, max 100px on story cards
- Text: always use `draw.textbbox()` to measure before placing; truncate at 90% of available width
- After building any generator: render with real data, visually inspect before marking done
- Never let text elements overlap; maintain minimum 8px gap between elements

---

## Caption System

Template-based, per platform:

**TikTok:** Hook (first 2 sec) + stat highlight + question to audience + 4-5 hashtags  
**Instagram:** Slightly longer, context sentence + CTA to rushmore.cards + hashtags  
**X:** Stat-first, max 2 hashtags, opinionated framing

Captions written per card type in `daily_pipeline.py` using f-string templates populated with live data.

---

## 20-Day Content Calendar

| Day | Date | Phase | Auto Card | Planned Card |
|-----|------|-------|-----------|--------------|
| 1 | Apr 11 | Regular Season | Top 5 Last Night | MVP Race Card |
| 2 | Apr 12 | Regular Season | Top 5 Last Night | Scoring Title Race |
| 3 | Apr 13 | Last Day | Top 5 Last Night | ROTY Race Card |
| 4 | Apr 14 | Play-In Hype | — | Playoff Bracket Debate Card |
| 5 | Apr 15 | Play-In | Top 5 Play-In | Funny: "Most Likely to Disappear in the Playoffs" |
| 6 | Apr 16 | Play-In | Top 5 Play-In | All-NBA Team Card |
| 7 | Apr 17 | Play-In | Top 5 Play-In | Hot Take: "Top 5 Regular Season Frauds" |
| 8 | Apr 18 | Pre-Playoffs | — | Playoff Preview: "Top 5 Series I can't miss" |
| 9 | Apr 19 | Playoffs R1 | Top 5 Playoffs | Matchup Card: Best Series of Round 1 |
| 10 | Apr 20 | Playoffs R1 | Top 5 Playoffs | Historical: "Top 5 Playoff Performers of All Time" |
| 11 | Apr 21 | Playoffs R1 | Top 5 Playoffs | Funny: "Who Would Win a 1v1 Tournament?" |
| 12 | Apr 22 | Playoffs R1 | Top 5 Playoffs | Matchup Card: Second featured series |
| 13 | Apr 23 | Playoffs R1 | Top 5 Playoffs | Debate: "Wemby 2026 Finals vs LeBron 2016 — who wins?" |
| 14 | Apr 24 | Playoffs R1 | Top 5 Playoffs | MIP + DPOY Award Reaction Card (award announcement window) |
| 15 | Apr 25 | Playoffs R1 | Top 5 Playoffs | Funny: "Top 5 Coaches I'd Hire for a Street Team" |
| 16 | Apr 26 | Playoffs R1 | Top 5 Playoffs | MVP Award Reaction Card (award announcement window) |
| 17 | Apr 27 | Playoffs R1 | Top 5 Playoffs | "Top 5 Franchises I'd Build Around" |
| 18 | Apr 28 | Playoffs R1 | Top 5 Playoffs | All-Rookie Team Card |
| 19 | Apr 29 | Playoffs R1 | Top 5 Playoffs | Hot Take: "5 Players Who Are Overrated" |
| 20 | Apr 30 | Playoffs R1 | Top 5 Playoffs | "Build Your Own Playoff Bracket" — CTA to rushmore.cards |

**Award-day slots (14, 16) are flexible** — if NBA announces awards earlier or later, swap with adjacent planned content.

---

## Telegram Notification

Daily message format:
```
📅 YYYY-MM-DD — N cards ready:

1. [Card Type] — [short description]
2. [Card Type] — [short description]

✅ Approve  |  ⏭ Skip today
```

Assets attached as images in the message for visual preview.

---

## GitHub Actions Cron

`.github/workflows/daily_cards.yml`:
- Schedule: `0 6 * * *` (06:00 UTC = 08:00 CET)
- Runs: `python3 tools/daily_pipeline.py`
- Requires secrets: `NBA_API_KEY` (if needed), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

---

## Out of Scope (deliberately)

- Auto-posting to social platforms (Phase 2, after system is stable)
- AI-generated captions (templates are more consistent for brand voice)
- Web scraping for trending topics (too brittle, not worth the maintenance)
- German-language content (NBA audience is global/English)

---

## Success Metrics (20 days)

- TikTok: grow from current baseline, target 2x average views per post
- Posting consistency: 2 posts/day, every day
- Zero missed days due to manual effort
- User time investment: < 5 min/day (Telegram approve tap only)
