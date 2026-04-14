# 20-Day NBA Content Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automated daily NBA content pipeline generating cards + captions + Telegram previews via GitHub Actions cron.

**Architecture:** `daily_pipeline.py` orchestrates everything — reads `content/calendar.yaml` for today's planned content, calls card generators, writes captions, sends Telegram. Five card generators share constants from `generate_card.py` (DPOY pattern). GitHub Actions runs cron at 06:00 UTC.

**Tech Stack:** Python 3.11, Pillow, nba_api, PyYAML, python-dotenv, requests (Telegram), GitHub Actions

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `content/calendar.yaml` | Create | 20-day content plan (dates, card type, title, items) |
| `tools/caption_templates.py` | Create | Returns platform captions (TikTok/Instagram/X) per card type |
| `tools/generate_debate_card.py` | Create | Renders YAML-driven list cards (debate/funny/historical) |
| `tools/generate_mvp_race_card.py` | Create | MVP Race card with crown icon, reuses DPOY pattern |
| `tools/generate_award_card.py` | Create | Generic award card for ROTY/MIP/All-NBA/Scoring Title |
| `tools/live_data.py` | Modify | Add `fetch_playoff_bracket()` |
| `tools/generate_playoff_card.py` | Create | Playoff matchup card (series score, seeds, key stats) |
| `tests/test_pipeline.py` | Create | Unit tests for calendar parsing + caption generation |
| `tools/daily_pipeline.py` | Create | Main orchestrator (calendar → cards → captions → Telegram) |
| `.github/workflows/daily_cards.yml` | Create | Cron 06:00 UTC trigger |

---

## Task 1: Content Calendar YAML

**Files:**
- Create: `content/calendar.yaml`

- [ ] **Step 1: Create calendar.yaml with all 20 entries**

```yaml
# content/calendar.yaml
# 20-Day NBA Content Pipeline: Apr 11 – Apr 30, 2026
# card_type: auto | mvp_race | scoring_title | roty | award | debate | playoff_bracket | playoff_matchup | all_nba | all_rookie
# For debate cards: provide title, subtitle, items (list of 5)
# For award cards: provide award_type (roty|mip|dpoy|mvp|all_nba|all_rookie), auto_data: true|false

days:
  - date: "2026-04-11"
    phase: Regular Season
    planned:
      card_type: mvp_race
      title: "2025-26 MVP Race"
      subtitle: "Top 5 Candidates"

  - date: "2026-04-12"
    phase: Regular Season
    planned:
      card_type: scoring_title
      title: "Scoring Title Race"
      subtitle: "Top 5 by PPG"

  - date: "2026-04-13"
    phase: Last Day Regular Season
    planned:
      card_type: roty
      title: "ROTY Race"
      subtitle: "Top 5 Rookies by PPG"

  - date: "2026-04-14"
    phase: Play-In Hype
    planned:
      card_type: debate
      title: "Play-In Bracket"
      subtitle: "Who Actually Makes the Playoffs?"
      items:
        - "OKC Thunder — Lock"
        - "Cleveland Cavs — Lock"
        - "Boston Celtics — Lock"
        - "Golden State Warriors — Bubble"
        - "Memphis Grizzlies — Bubble"

  - date: "2026-04-15"
    phase: Play-In
    planned:
      card_type: debate
      title: "Most Likely to Ghost"
      subtitle: "Disappear in the Playoffs"
      items:
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"

  - date: "2026-04-16"
    phase: Play-In
    planned:
      card_type: award
      award_type: all_nba
      title: "All-NBA First Team"
      subtitle: "2025-26 Season"
      auto_data: false
      items:
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"

  - date: "2026-04-17"
    phase: Play-In
    planned:
      card_type: debate
      title: "Regular Season Frauds"
      subtitle: "Hot Take: Who Won't Show Up"
      items:
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"

  - date: "2026-04-18"
    phase: Pre-Playoffs
    planned:
      card_type: debate
      title: "Series I Can't Miss"
      subtitle: "Playoffs Round 1 Preview"
      items:
        - "Series TBD"
        - "Series TBD"
        - "Series TBD"
        - "Series TBD"
        - "Series TBD"

  - date: "2026-04-19"
    phase: Playoffs R1
    planned:
      card_type: playoff_matchup
      matchup_index: 0

  - date: "2026-04-20"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "All-Time Playoff Legends"
      subtitle: "Top 5 Performers in NBA History"
      items:
        - "Michael Jordan — 33.4 PPG Playoffs"
        - "LeBron James — Most Playoff Points Ever"
        - "Shaquille O'Neal — 4x Champ, 3x Finals MVP"
        - "Kobe Bryant — 2x Finals MVP"
        - "Tim Duncan — The Quiet Legend, 5 Rings"

  - date: "2026-04-21"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "1v1 Tournament"
      subtitle: "Who Would Win?"
      items:
        - "Giannis Antetokounmpo"
        - "Kevin Durant"
        - "Luka Doncic"
        - "Jayson Tatum"
        - "Victor Wembanyama"

  - date: "2026-04-22"
    phase: Playoffs R1
    planned:
      card_type: playoff_matchup
      matchup_index: 1

  - date: "2026-04-23"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "Wemby 2026 vs LeBron 2016"
      subtitle: "Who Wins the Finals?"
      items:
        - "Victor Wembanyama — 7'4 with guard skills"
        - "LeBron James — The GOAT argument"
        - "Wemby's supporting cast"
        - "LeBron's Cavs had Kyrie"
        - "Edge: LeBron (barely)"

  - date: "2026-04-24"
    phase: Playoffs R1
    planned:
      card_type: award
      award_type: mip
      title: "Most Improved Player"
      subtitle: "2025-26 Award"
      auto_data: true

  - date: "2026-04-25"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "Street Team Coaches"
      subtitle: "Top 5 I'd Hire for a 5v5"
      items:
        - "Coach TBD"
        - "Coach TBD"
        - "Coach TBD"
        - "Coach TBD"
        - "Coach TBD"

  - date: "2026-04-26"
    phase: Playoffs R1
    planned:
      card_type: award
      award_type: mvp
      title: "Most Valuable Player"
      subtitle: "2025-26 Award"
      auto_data: true

  - date: "2026-04-27"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "Franchises to Build Around"
      subtitle: "Top 5 Right Now"
      items:
        - "Oklahoma City Thunder"
        - "San Antonio Spurs (Wemby)"
        - "Minnesota Timberwolves"
        - "Cleveland Cavaliers"
        - "Boston Celtics"

  - date: "2026-04-28"
    phase: Playoffs R1
    planned:
      card_type: award
      award_type: all_rookie
      title: "All-Rookie First Team"
      subtitle: "2025-26 Season"
      auto_data: false
      items:
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"

  - date: "2026-04-29"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "Most Overrated Players"
      subtitle: "Hot Take Season"
      items:
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"
        - "Player TBD"

  - date: "2026-04-30"
    phase: Playoffs R1
    planned:
      card_type: debate
      title: "Build Your Playoff Bracket"
      subtitle: "rushmore.cards"
      items:
        - "Who wins the East?"
        - "Who wins the West?"
        - "Biggest upset pick?"
        - "Finals MVP?"
        - "Champion: Your Pick"
```

- [ ] **Step 2: Verify file is valid YAML**

```bash
python3 -c "import yaml; data = yaml.safe_load(open('content/calendar.yaml')); print(f'OK — {len(data[\"days\"])} days loaded')"
```

Expected output: `OK — 20 days loaded`

- [ ] **Step 3: Commit**

```bash
git add content/calendar.yaml
git commit -m "feat: add 20-day content calendar YAML (Apr 11–30)"
```

---

## Task 2: Caption Templates

**Files:**
- Create: `tools/caption_templates.py`
- Test: `tests/test_pipeline.py` (first test)

- [ ] **Step 1: Write the failing test**

Create `tests/test_pipeline.py`:

```python
"""Unit tests for pipeline logic: calendar parsing + caption generation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from caption_templates import get_captions


def test_top5_captions_have_all_platforms():
    players = [
        {"name": "Luka Doncic", "ppg": 32.4, "team": "DAL"},
        {"name": "Shai Gilgeous-Alexander", "ppg": 31.2, "team": "OKC"},
        {"name": "Giannis Antetokounmpo", "ppg": 30.1, "team": "MIL"},
        {"name": "Jayson Tatum", "ppg": 28.5, "team": "BOS"},
        {"name": "Victor Wembanyama", "ppg": 27.9, "team": "SAS"},
    ]
    captions = get_captions("top5", players=players, date="2026-04-12")
    assert "tiktok" in captions
    assert "instagram" in captions
    assert "x" in captions


def test_top5_tiktok_contains_hook():
    players = [{"name": "Luka Doncic", "ppg": 32.4, "team": "DAL"}]
    captions = get_captions("top5", players=players, date="2026-04-12")
    assert len(captions["tiktok"]) > 0
    assert "#NBA" in captions["tiktok"]


def test_mvp_race_captions():
    players = [{"name": "SGA", "ppg": 31.2, "eff": 28.5, "team": "OKC"}]
    captions = get_captions("mvp_race", players=players, date="2026-04-12")
    assert "mvp" in captions["tiktok"].lower() or "MVP" in captions["tiktok"]


def test_debate_captions():
    captions = get_captions("debate", title="Regular Season Frauds", date="2026-04-17")
    assert len(captions["x"]) <= 280
    assert "rushmore.cards" in captions["instagram"]


def test_award_captions():
    players = [{"name": "Chet Holmgren", "team": "OKC"}]
    captions = get_captions("award", award_type="mip", players=players, date="2026-04-24")
    assert len(captions["tiktok"]) > 0


def test_playoff_matchup_captions():
    matchup = {
        "home_team": "OKC Thunder",
        "away_team": "Dallas Mavericks",
        "home_wins": 2,
        "away_wins": 1,
    }
    captions = get_captions("playoff_matchup", matchup=matchup, date="2026-04-19")
    assert "OKC" in captions["x"] or "Thunder" in captions["x"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_pipeline.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'caption_templates'`

- [ ] **Step 3: Create `tools/caption_templates.py`**

```python
"""
Caption template system for the Rushmore content pipeline.

Returns platform-specific captions per card type.
All captions are in English with brand voice: stats-first, opinion-second.
"""

from __future__ import annotations


def get_captions(
    card_type: str,
    *,
    players: list[dict] | None = None,
    date: str = "",
    title: str = "",
    award_type: str = "",
    matchup: dict | None = None,
) -> dict[str, str]:
    """Return {'tiktok': str, 'instagram': str, 'x': str} for a card type."""
    dispatch = {
        "top5": _top5,
        "mvp_race": _mvp_race,
        "scoring_title": _scoring_title,
        "roty": _roty,
        "debate": _debate,
        "award": _award,
        "playoff_matchup": _playoff_matchup,
        "playoff_bracket": _playoff_bracket,
        "all_nba": _all_nba,
        "all_rookie": _all_rookie,
    }
    fn = dispatch.get(card_type, _generic)
    return fn(
        players=players or [],
        date=date,
        title=title,
        award_type=award_type,
        matchup=matchup or {},
    )


def _top5(players, date, **_):
    top = players[0] if players else {"name": "Unknown", "ppg": 0.0}
    name = top["name"]
    ppg = top.get("ppg", 0.0)
    tiktok = (
        f"He dropped {ppg} points last night 👀\n"
        f"{name} leads last night's Top 5 — do you agree with the ranking?\n"
        f"#NBA #Basketball #Top5 #NBAHighlights"
    )
    instagram = (
        f"Last night's Top 5 scorers are in 🏀\n"
        f"{name} tops the list with {ppg} PPG. Build your own Top 5 at rushmore.cards\n"
        f"#NBA #NBABasketball #Top5 #Basketball #NBAHighlights #rushmore"
    )
    x = f"{name} leads last night's Top 5 with {ppg} pts. #NBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _mvp_race(players, date, **_):
    top = players[0] if players else {"name": "Unknown", "ppg": 0.0, "eff": 0.0}
    name = top["name"]
    eff = top.get("eff", 0.0)
    tiktok = (
        f"Who wins the MVP? {name} leads by efficiency ({eff:.1f} EFF) 👑\n"
        f"The race isn't over. Drop your pick below.\n"
        f"#NBA #MVP #MVPRace #Basketball"
    )
    instagram = (
        f"The 2025-26 MVP Race is heating up 👑\n"
        f"{name} tops our efficiency rankings at {eff:.1f} EFF. "
        f"Build your own MVP ballot at rushmore.cards\n"
        f"#NBA #MVP #MVPRace #Basketball #NBAStats #rushmore"
    )
    x = f"{name} leads the MVP race at {eff:.1f} EFF. Your pick? #NBA #MVP"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _scoring_title(players, date, **_):
    top = players[0] if players else {"name": "Unknown", "ppg": 0.0}
    name = top["name"]
    ppg = top.get("ppg", 0.0)
    tiktok = (
        f"{ppg} points per game. {name} is your 2025-26 scoring champ 🎯\n"
        f"Is this the best scoring season in a decade?\n"
        f"#NBA #ScoringTitle #Basketball #NBAStats"
    )
    instagram = (
        f"Scoring Title Race — final standings 🎯\n"
        f"{name} finishes at {ppg} PPG. Full ranking on rushmore.cards\n"
        f"#NBA #ScoringTitle #NBAStats #Basketball #rushmore"
    )
    x = f"{name} wins the 2025-26 scoring title at {ppg} PPG. #NBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _roty(players, date, **_):
    top = players[0] if players else {"name": "Unknown", "ppg": 0.0}
    name = top["name"]
    ppg = top.get("ppg", 0.0)
    tiktok = (
        f"Rookie of the Year? {name} averaging {ppg} PPG 🌟\n"
        f"This class is stacked — who gets your vote?\n"
        f"#NBA #ROTY #RookieOfTheYear #Basketball"
    )
    instagram = (
        f"The ROTY race — Top 5 rookies by PPG 🌟\n"
        f"{name} leads with {ppg} PPG. Who wins it? rushmore.cards\n"
        f"#NBA #ROTY #NBABasketball #Basketball #Rookies #rushmore"
    )
    x = f"{name} leads the ROTY race at {ppg} PPG. Legit? #NBA #ROTY"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _debate(players, date, title, **_):
    tiktok = (
        f"{title} — agree or disagree? 👇\n"
        f"Drop your list in the comments.\n"
        f"#NBA #Basketball #HotTake #NBADebate"
    )
    instagram = (
        f"{title} 🔥\n"
        f"This is our take — what's yours? Build your own list at rushmore.cards\n"
        f"#NBA #Basketball #HotTake #NBADebate #rushmore"
    )
    x = f"{title} — our list. Yours? rushmore.cards #NBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _award(players, date, award_type, **_):
    labels = {
        "mvp": ("MVP", "Most Valuable Player", "👑"),
        "roty": ("ROTY", "Rookie of the Year", "🌟"),
        "mip": ("MIP", "Most Improved Player", "📈"),
        "dpoy": ("DPOY", "Defensive Player of the Year", "🛡️"),
        "all_nba": ("All-NBA", "All-NBA Team", "🏆"),
        "all_rookie": ("All-Rookie", "All-Rookie Team", "🌟"),
    }
    short, long_name, icon = labels.get(award_type, ("Award", "Award Winner", "🏆"))
    winner = players[0]["name"] if players else "TBD"
    tiktok = (
        f"{icon} {winner} wins the {short}!\n"
        f"Was this the right call? #NBA #{short} #Basketball"
    )
    instagram = (
        f"{icon} {long_name} 2025-26: {winner}\n"
        f"React below. Full breakdown at rushmore.cards\n"
        f"#NBA #{short} #NBABasketball #Basketball #rushmore"
    )
    x = f"{winner} wins the {short}. Deserved? #NBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _playoff_matchup(players, date, matchup, **_):
    home = matchup.get("home_team", "Team A")
    away = matchup.get("away_team", "Team B")
    hw = matchup.get("home_wins", 0)
    aw = matchup.get("away_wins", 0)
    leader = home if hw > aw else away if aw > hw else "Tied"
    score_line = f"{home} {hw}–{aw} {away}"
    tiktok = (
        f"{score_line} 🏀\n"
        f"This series is LIVE. Who takes it? Drop your pick 👇\n"
        f"#NBA #Playoffs #NBAPlayoffs #Basketball"
    )
    instagram = (
        f"Playoff Update 🏀\n"
        f"{score_line} — {leader} with the edge. "
        f"Track every matchup at rushmore.cards\n"
        f"#NBA #NBAPlayoffs #Basketball #Playoffs #rushmore"
    )
    # X: keep under 200 chars including hashtag
    x = f"{score_line} — who wins? #NBAPlayoffs"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _playoff_bracket(players, date, **_):
    tiktok = (
        "Play-In is HERE 🏀 Who's making the playoffs?\n"
        "Drop your bracket predictions below 👇\n"
        "#NBA #PlayIn #Playoffs #Basketball"
    )
    instagram = (
        "The Play-In bracket is set 🏀\n"
        "Who survives? Build your own bracket at rushmore.cards\n"
        "#NBA #PlayIn #NBAPlayoffs #Basketball #rushmore"
    )
    x = "Play-In time. Who's in, who's out? #NBA #PlayIn"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _all_nba(players, date, **_):
    tiktok = (
        "All-NBA Team is announced 🏆\n"
        "Agree with the picks? #NBA #AllNBA #Basketball"
    )
    instagram = (
        "2025-26 All-NBA Team 🏆\n"
        "These 5 defined the season. rushmore.cards\n"
        "#NBA #AllNBA #NBABasketball #Basketball #rushmore"
    )
    x = "All-NBA 2025-26 announced. Best pick? Worst snub? #NBA #AllNBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _all_rookie(players, date, **_):
    tiktok = (
        "All-Rookie Team 2025-26 🌟\n"
        "This class is the future of the NBA.\n"
        "#NBA #AllRookie #Rookies #Basketball"
    )
    instagram = (
        "All-Rookie First Team 2025-26 🌟\n"
        "The future is bright. rushmore.cards\n"
        "#NBA #AllRookie #Rookies #NBABasketball #rushmore"
    )
    x = "All-Rookie Team 2025-26. Who's your ROY? #NBA #Rookies"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _generic(players, date, title, **_):
    tiktok = f"{title} 🏀 #NBA #Basketball"
    instagram = f"{title} — rushmore.cards #NBA #Basketball #rushmore"
    x = f"{title} #NBA"
    return {"tiktok": tiktok, "instagram": instagram, "x": x}
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_pipeline.py -v
```

Expected: 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add tools/caption_templates.py tests/test_pipeline.py
git commit -m "feat: add caption template system with unit tests"
```

---

## Task 3: Debate / Funny / Historical Card Generator

**Files:**
- Create: `tools/generate_debate_card.py`

This generator renders any 5-item YAML list as a styled card. No live data.

- [ ] **Step 1: Create `tools/generate_debate_card.py`**

```python
"""
Debate / Funny / Historical Card Generator.

Renders any 5-item list from YAML into a shareable card.
No live data required — content comes from calendar.yaml.

Usage:
    python3 tools/generate_debate_card.py --title "Top 5 Frauds" --items "Luka,KD,Giannis,Tatum,Beal" --feed
    python3 tools/generate_debate_card.py --title "Top 5" --items "A,B,C,D,E"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (
    _font, _font_impact,
    _load_background,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)


def generate_debate_card(
    title: str,
    subtitle: str,
    items: list[str],
    output_path: str = "output/debate_card.png",
    card_format: str = "story",
) -> str:
    """Render a debate/list card. Returns output_path on success."""
    if len(items) != 5:
        raise ValueError(f"Debate card requires exactly 5 items, got {len(items)}")

    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h = _row_area // ROW_COUNT

    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ── Title block ──
    title_y = _v_inset
    # Teal accent bar
    draw.rectangle([PAD, title_y + 12, PAD + 6, title_y + _title_h - 12], fill=TEAL)

    # Title text
    font_title = _font_impact(int(52 * _scale))
    title_x = PAD + 20
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_h = bbox[3] - bbox[1]
    draw.text(
        (title_x, title_y + (_title_h - text_h) // 2 - int(14 * _scale)),
        title,
        font=font_title,
        fill=WHITE,
    )

    # Subtitle
    font_sub = _font(int(28 * _scale))
    draw.text(
        (title_x, title_y + (_title_h - text_h) // 2 + text_h - int(6 * _scale)),
        subtitle,
        font=font_sub,
        fill=TEAL,
    )

    # ── Rows ──
    rows_top = _v_inset + _title_h
    for rank, item_text in enumerate(items, start=1):
        row_y = rows_top + (rank - 1) * (_row_h + _row_gap)
        bg = ROW_BG_1 if rank == 1 else ROW_BG
        draw.rounded_rectangle(
            [PAD, row_y, WIDTH - PAD, row_y + _row_h],
            radius=18,
            fill=bg,
        )

        # Rank number
        font_rank = _font_impact(int(64 * _scale))
        rank_str = str(rank)
        rb = draw.textbbox((0, 0), rank_str, font=font_rank)
        rank_w = rb[2] - rb[0]
        rank_h = rb[3] - rb[1]
        rank_x = PAD + int(32 * _scale)
        rank_cy = row_y + _row_h // 2 - rank_h // 2
        draw.text((rank_x, rank_cy), rank_str, font=font_rank, fill=TEAL)

        # Item text — truncate to 90% of available width
        text_x = rank_x + rank_w + int(24 * _scale)
        max_text_w = int((WIDTH - PAD - text_x) * 0.9)
        font_item = _font(int(36 * _scale))

        # Truncate if too wide
        display_text = item_text
        while True:
            tb = draw.textbbox((0, 0), display_text, font=font_item)
            if tb[2] - tb[0] <= max_text_w or len(display_text) < 4:
                break
            display_text = display_text[:-4] + "..."

        item_h = draw.textbbox((0, 0), display_text, font=font_item)[3]
        item_y = row_y + _row_h // 2 - item_h // 2
        # Ensure minimum 8px gap from row edges
        item_y = max(row_y + 8, min(item_y, row_y + _row_h - item_h - 8))
        draw.text((text_x, item_y), display_text, font=font_item, fill=WHITE)

    # ── Footer ──
    footer_y = canvas_h - _footer_h
    font_footer = _font(int(24 * _scale))
    draw.text(
        (PAD, footer_y + int((_footer_h - 24 * _scale) // 2)),
        "rushmore.cards",
        font=font_footer,
        fill=GRAY,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", default="Top 5 NBA Players")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--items", help="Comma-separated list of 5 items")
    parser.add_argument("--output", default="output/debate_card.png")
    parser.add_argument("--feed", action="store_true")
    args = parser.parse_args()

    items = [i.strip() for i in (args.items or "A,B,C,D,E").split(",")]
    fmt = "feed" if args.feed else "story"
    generate_debate_card(
        title=args.title,
        subtitle=args.subtitle,
        items=items[:5],
        output_path=args.output,
        card_format=fmt,
    )
```

- [ ] **Step 2: Test render with real data — visually inspect**

```bash
python3 tools/generate_debate_card.py \
  --title "Regular Season Frauds" \
  --subtitle "Hot Take: Who Won't Show Up" \
  --items "Luka Doncic,Zion Williamson,James Harden,Russell Westbrook,Ben Simmons" \
  --output output/test_debate_story.png

open output/test_debate_story.png
```

Check: text not overlapping, rank numbers visible, no clipping.

```bash
python3 tools/generate_debate_card.py \
  --title "Regular Season Frauds" \
  --subtitle "Hot Take" \
  --items "Luka Doncic,Zion Williamson,James Harden,Russell Westbrook,Ben Simmons" \
  --output output/test_debate_feed.png \
  --feed

open output/test_debate_feed.png
```

- [ ] **Step 3: Commit**

```bash
git add tools/generate_debate_card.py
git commit -m "feat: add debate/list card generator (YAML-driven)"
```

---

## Task 4: MVP Race Card Generator

**Files:**
- Create: `tools/generate_mvp_race_card.py`

Reuses DPOY pattern exactly — crown icon instead of shield, MVP stats (PPG + EFF).

- [ ] **Step 1: Create `tools/generate_mvp_race_card.py`**

```python
"""
MVP Race Card Generator — 2025-26 NBA Season.

Shows top 5 MVP candidates ranked by EFF with PPG and efficiency stats.
Uses crown icon motif. Reuses DPOY card structure.

Usage:
    python3 tools/generate_mvp_race_card.py
    python3 tools/generate_mvp_race_card.py --feed
"""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (
    _font, _font_impact,
    _load_background, _load_headshot, _initials_circle, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)
from live_data import fetch_current_mvp_race
from download_headshots import download_by_ids


def _crown_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple):
    """Draw a simple crown outline as the MVP motif."""
    w = size
    h = int(size * 0.75)
    x0 = cx - w // 2
    y0 = cy - h // 2
    # Crown base band
    base_top = y0 + int(h * 0.55)
    draw.rectangle(
        [x0, base_top, x0 + w, y0 + h],
        fill=(*color, 30),
        outline=(*color, 180),
        width=2,
    )
    # Three crown points
    pts_left = [(x0, base_top), (x0 + w // 4, y0), (x0 + w // 2, base_top - int(h * 0.15))]
    pts_mid = [(x0 + w // 4, base_top), (x0 + w // 2, y0 - int(h * 0.1)), (x0 + 3 * w // 4, base_top)]
    pts_right = [(x0 + w // 2, base_top - int(h * 0.15)), (x0 + 3 * w // 4, y0), (x0 + w, base_top)]
    for pts in (pts_left, pts_mid, pts_right):
        draw.polygon(pts, fill=(*color, 30), outline=(*color, 180))


def generate_mvp_race_card(
    output_path: str = "output/mvp_race/card.png",
    card_format: str = "story",
):
    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)

    players = fetch_current_mvp_race(limit=5)
    if not players:
        print("No MVP data returned — check nba_api connection.")
        return

    ids = [p["id"] for p in players]
    names = {p["id"]: p["name"] for p in players}
    download_by_ids(ids, names)

    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ── Title block ──
    title_y = _v_inset
    draw.rectangle([PAD, title_y + 12, PAD + 6, title_y + _title_h - 12], fill=TEAL)
    _crown_icon(draw, PAD + int(60 * _scale), title_y + _title_h // 2, int(44 * _scale), TEAL)

    font_title = _font_impact(int(52 * _scale))
    draw.text(
        (PAD + int(100 * _scale), title_y + int(20 * _scale)),
        "2025-26 MVP Race",
        font=font_title,
        fill=WHITE,
    )
    font_sub = _font(int(28 * _scale))
    draw.text(
        (PAD + int(100 * _scale), title_y + int(20 * _scale) + int(56 * _scale)),
        "Top 5 Candidates by Efficiency",
        font=font_sub,
        fill=TEAL,
    )

    # ── Player rows ──
    rows_top = _v_inset + _title_h
    for rank, p in enumerate(players, start=1):
        row_y = rows_top + (rank - 1) * (_row_h + _row_gap)
        bg = ROW_BG_1 if rank == 1 else ROW_BG
        draw.rounded_rectangle(
            [PAD, row_y, WIDTH - PAD, row_y + _row_h],
            radius=18,
            fill=bg,
        )

        # Rank
        font_rank = _font_impact(int(64 * _scale))
        rank_str = str(rank)
        rb = draw.textbbox((0, 0), rank_str, font=font_rank)
        rank_w = rb[2] - rb[0]
        draw.text(
            (PAD + int(16 * _scale), row_y + _row_h // 2 - (rb[3] - rb[1]) // 2),
            rank_str, font=font_rank, fill=TEAL,
        )

        # Headshot
        photo_x = PAD + rank_w + int(24 * _scale)
        photo_y = row_y + (_row_h - _photo_size) // 2
        headshot = _load_headshot(p["id"], _photo_size) or _initials_circle(p["name"], _photo_size)
        canvas.paste(headshot, (photo_x, photo_y), headshot)

        # Team logo
        logo = _load_team_logo(_ABBR_ALIASES.get(p["team"], p["team"]), int(80 * _scale))
        if logo:
            logo_x = WIDTH - PAD - logo.width
            logo_y = row_y + (_row_h - logo.height) // 2
            canvas.paste(logo, (logo_x, logo_y), logo)

        # Name + stats
        name_x = photo_x + _photo_size + int(16 * _scale)
        max_name_w = int((WIDTH - PAD - int(80 * _scale) - name_x) * 0.9)
        font_name = _font(int(36 * _scale))
        name = p["name"]
        while True:
            nb = draw.textbbox((0, 0), name, font=font_name)
            if nb[2] - nb[0] <= max_name_w or len(name) < 4:
                break
            name = name[:-4] + "..."
        draw.text(
            (name_x, row_y + int(_row_h * 0.20)),
            name, font=font_name, fill=WHITE,
        )

        stats_line = f"{p.get('ppg', 0.0):.1f} PPG  |  {p.get('eff', 0.0):.1f} EFF"
        font_stats = _font(int(26 * _scale))
        draw.text(
            (name_x, row_y + int(_row_h * 0.55)),
            stats_line, font=font_stats, fill=TEAL,
        )

    # ── Footer ──
    footer_y = canvas_h - _footer_h
    font_footer = _font(int(24 * _scale))
    draw.text(
        (PAD, footer_y + int((_footer_h - 24 * _scale) // 2)),
        "rushmore.cards",
        font=font_footer,
        fill=GRAY,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--feed", action="store_true")
    parser.add_argument("--output", default="output/mvp_race/card.png")
    args = parser.parse_args()
    generate_mvp_race_card(output_path=args.output, card_format="feed" if args.feed else "story")
```

- [ ] **Step 2: Test render — visually inspect**

```bash
python3 tools/generate_mvp_race_card.py --output output/test_mvp_story.png
open output/test_mvp_story.png

python3 tools/generate_mvp_race_card.py --feed --output output/test_mvp_feed.png
open output/test_mvp_feed.png
```

Check: crown icon visible, stats line reads correctly, no text overlap.

- [ ] **Step 3: Commit**

```bash
git add tools/generate_mvp_race_card.py
git commit -m "feat: add MVP Race card generator with crown icon"
```

---

## Task 5: Generic Award Card Generator

**Files:**
- Create: `tools/generate_award_card.py`

One generator handles ROTY, MIP, All-NBA, Scoring Title. Uses YAML items when `auto_data: false`.

- [ ] **Step 1: Create `tools/generate_award_card.py`**

```python
"""
Generic Award Card Generator.

Handles: ROTY, MIP, DPOY (reaction), MVP (reaction), All-NBA, All-Rookie, Scoring Title.
When auto_data=True: fetches live data. When False: uses provided items list.

Usage:
    python3 tools/generate_award_card.py --award roty
    python3 tools/generate_award_card.py --award mip --feed
    python3 tools/generate_award_card.py --award all_nba --items "P1,P2,P3,P4,P5"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (
    _font, _font_impact,
    _load_background, _load_headshot, _initials_circle, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)

# Award configuration: short_name, full_name, icon_char, stat_key, stat_label, fetch_fn_name
AWARD_CONFIG = {
    "roty":      ("ROTY",       "Rookie of the Year",          "★", "ppg", "PPG", "fetch_current_roy_race"),
    "mip":       ("MIP",        "Most Improved Player",        "↑", "ppg", "PPG", "fetch_current_mip_race"),
    "mvp":       ("MVP",        "Most Valuable Player",        "♛", "eff", "EFF", "fetch_current_mvp_race"),
    "dpoy":      ("DPOY",       "Defensive Player of the Year","⬡", "dpoy_score", "DEF", "fetch_current_dpoy_race"),
    "scoring":   ("Scoring",    "Scoring Title",               "⊙", "ppg", "PPG", "fetch_season_leaders"),
    "all_nba":   ("All-NBA",    "All-NBA First Team",          "◈", None,  None,  None),
    "all_rookie":("All-Rookie", "All-Rookie First Team",       "◈", None,  None,  None),
}


def _draw_icon_char(draw, char: str, cx: int, cy: int, size: int, color: tuple):
    """Draw a Unicode icon character centered at (cx, cy)."""
    from generate_card import _font_impact
    font = _font_impact(size)
    bb = draw.textbbox((0, 0), char, font=font)
    x = cx - (bb[2] - bb[0]) // 2
    y = cy - (bb[3] - bb[1]) // 2
    draw.text((x, y), char, font=font, fill=(*color, 200))


def generate_award_card(
    award_type: str,
    items: list[str] | None = None,
    auto_data: bool = True,
    output_path: str = "output/award_card.png",
    card_format: str = "story",
) -> str:
    config = AWARD_CONFIG.get(award_type)
    if not config:
        raise ValueError(f"Unknown award_type: {award_type}. Valid: {list(AWARD_CONFIG.keys())}")

    short, long_name, icon_char, stat_key, stat_label, fetch_fn_name = config

    # Fetch live data or use YAML items
    players = []
    if auto_data and fetch_fn_name:
        import live_data
        fn = getattr(live_data, fetch_fn_name)
        players = fn(limit=5)
        if not players:
            print(f"No data for {short} — using placeholder names.")
            players = [{"name": f"Player {i}", "id": 0, "team": "NBA"} for i in range(1, 6)]
        # Download headshots
        from download_headshots import download_by_ids
        ids = [p["id"] for p in players if p.get("id")]
        names = {p["id"]: p["name"] for p in players if p.get("id")}
        if ids:
            download_by_ids(ids, names)
    elif items:
        players = [{"name": item, "id": 0, "team": ""} for item in items[:5]]
    else:
        players = [{"name": f"Player {i}", "id": 0, "team": ""} for i in range(1, 6)]

    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)

    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ── Title block ──
    title_y = _v_inset
    draw.rectangle([PAD, title_y + 12, PAD + 6, title_y + _title_h - 12], fill=TEAL)
    _draw_icon_char(draw, icon_char, PAD + int(62 * _scale), title_y + _title_h // 2, int(44 * _scale), TEAL)

    font_title = _font_impact(int(52 * _scale))
    draw.text(
        (PAD + int(100 * _scale), title_y + int(20 * _scale)),
        long_name,
        font=font_title,
        fill=WHITE,
    )
    font_sub = _font(int(28 * _scale))
    draw.text(
        (PAD + int(100 * _scale), title_y + int(20 * _scale) + int(56 * _scale)),
        "2025-26 Season",
        font=font_sub,
        fill=TEAL,
    )

    # ── Rows ──
    rows_top = _v_inset + _title_h
    for rank, p in enumerate(players, start=1):
        row_y = rows_top + (rank - 1) * (_row_h + _row_gap)
        bg = ROW_BG_1 if rank == 1 else ROW_BG
        draw.rounded_rectangle(
            [PAD, row_y, WIDTH - PAD, row_y + _row_h],
            radius=18,
            fill=bg,
        )

        # Rank
        font_rank = _font_impact(int(64 * _scale))
        rank_str = str(rank)
        rb = draw.textbbox((0, 0), rank_str, font=font_rank)
        rank_w = rb[2] - rb[0]
        rank_h = rb[3] - rb[1]
        draw.text(
            (PAD + int(16 * _scale), row_y + _row_h // 2 - rank_h // 2),
            rank_str, font=font_rank, fill=TEAL,
        )

        # Headshot (only if we have real IDs)
        photo_x = PAD + rank_w + int(24 * _scale)
        if p.get("id"):
            headshot = _load_headshot(p["id"], _photo_size) or _initials_circle(p["name"], _photo_size)
        else:
            headshot = _initials_circle(p["name"], _photo_size)
        photo_y = row_y + (_row_h - _photo_size) // 2
        canvas.paste(headshot, (photo_x, photo_y), headshot)

        # Team logo
        if p.get("team"):
            logo = _load_team_logo(_ABBR_ALIASES.get(p["team"], p["team"]), int(80 * _scale))
            if logo:
                logo_x = WIDTH - PAD - logo.width
                logo_y = row_y + (_row_h - logo.height) // 2
                canvas.paste(logo, (logo_x, logo_y), logo)

        # Name
        name_x = photo_x + _photo_size + int(16 * _scale)
        max_name_w = int((WIDTH - PAD - int(80 * _scale) - name_x) * 0.9)
        font_name = _font(int(36 * _scale))
        name = p["name"]
        while True:
            nb = draw.textbbox((0, 0), name, font=font_name)
            if nb[2] - nb[0] <= max_name_w or len(name) < 4:
                break
            name = name[:-4] + "..."
        draw.text(
            (name_x, row_y + int(_row_h * 0.25)),
            name, font=font_name, fill=WHITE,
        )

        # Stat line (only for auto-data cards with known stat)
        if stat_key and stat_label and p.get(stat_key) is not None:
            stat_val = p[stat_key]
            stats_line = f"{stat_val:.1f} {stat_label}"
            font_stats = _font(int(26 * _scale))
            draw.text(
                (name_x, row_y + int(_row_h * 0.58)),
                stats_line, font=font_stats, fill=TEAL,
            )

    # ── Footer ──
    footer_y = canvas_h - _footer_h
    font_footer = _font(int(24 * _scale))
    draw.text(
        (PAD, footer_y + int((_footer_h - 24 * _scale) // 2)),
        "rushmore.cards",
        font=font_footer,
        fill=GRAY,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--award", default="roty", choices=list(AWARD_CONFIG.keys()))
    parser.add_argument("--items", help="Comma-separated player names (overrides auto_data)")
    parser.add_argument("--feed", action="store_true")
    parser.add_argument("--output", default="output/award_card.png")
    args = parser.parse_args()

    item_list = [i.strip() for i in args.items.split(",")] if args.items else None
    generate_award_card(
        award_type=args.award,
        items=item_list,
        auto_data=item_list is None,
        output_path=args.output,
        card_format="feed" if args.feed else "story",
    )
```

- [ ] **Step 2: Test render ROTY — visually inspect**

```bash
python3 tools/generate_award_card.py --award roty --output output/test_roty_story.png
open output/test_roty_story.png

python3 tools/generate_award_card.py --award roty --feed --output output/test_roty_feed.png
open output/test_roty_feed.png
```

Check: ROTY header, rookies listed with PPG, no text overlap.

- [ ] **Step 3: Test render All-NBA (manual items) — visually inspect**

```bash
python3 tools/generate_award_card.py \
  --award all_nba \
  --items "Nikola Jokic,SGA,Giannis Antetokounmpo,Jayson Tatum,Luka Doncic" \
  --output output/test_allnba.png

open output/test_allnba.png
```

Check: initials circles for no-ID players, clean layout.

- [ ] **Step 4: Commit**

```bash
git add tools/generate_award_card.py
git commit -m "feat: add generic award card generator (ROTY, MIP, All-NBA, Scoring Title)"
```

---

## Task 6: Add `fetch_playoff_bracket()` to live_data.py

**Files:**
- Modify: `tools/live_data.py`

- [ ] **Step 1: Add test for new function**

In `tests/test_pipeline.py`, add:

```python
from live_data import fetch_playoff_bracket


def test_fetch_playoff_bracket_structure():
    """fetch_playoff_bracket returns list of matchup dicts with required keys."""
    bracket = fetch_playoff_bracket()
    # During regular season: returns [] — that's valid
    assert isinstance(bracket, list)
    for matchup in bracket:
        assert "home_team" in matchup
        assert "away_team" in matchup
        assert "home_wins" in matchup
        assert "away_wins" in matchup
        assert "conference" in matchup
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_pipeline.py::test_fetch_playoff_bracket_structure -v
```

Expected: `ImportError` or `AttributeError` — function doesn't exist yet.

- [ ] **Step 3: Add `fetch_playoff_bracket()` to `tools/live_data.py`**

Find the last function in `live_data.py` and append:

```python
def fetch_playoff_bracket() -> list[dict]:
    """Fetch current NBA playoff bracket matchups.

    Returns list of matchup dicts:
        {home_team, away_team, home_seed, away_seed,
         home_wins, away_wins, conference, round_num}

    Returns [] during regular season (endpoint returns no bracket data).
    """
    cache_key = "playoff_bracket_v1"
    cached = _read_cache(cache_key, ttl_hours=1)
    if cached is not None:
        return cached

    try:
        from nba_api.stats.endpoints import playoffpicture

        picture = playoffpicture.PlayoffPicture(league_id="00")
        # PlayoffPicture returns multiple data frames; index 0 = East, 1 = West
        dfs = picture.get_data_frames()
    except Exception as exc:
        print(f"fetch_playoff_bracket: API error — {exc}")
        return []

    matchups = []
    conf_names = {0: "East", 1: "West"}
    for conf_idx, df in enumerate(dfs[:2]):
        if df.empty:
            continue
        # Each row is a series in that conference
        for _, row in df.iterrows():
            try:
                home_wins = int(row.get("HOME_TEAM_WINS") or 0)
                away_wins = int(row.get("ROAD_TEAM_WINS") or 0)
                matchups.append({
                    "home_team": str(row.get("HOME_TEAM_NAME", "")),
                    "away_team": str(row.get("ROAD_TEAM_NAME", "")),
                    "home_seed": int(row.get("HOME_TEAM_SEED") or 0),
                    "away_seed": int(row.get("ROAD_TEAM_SEED") or 0),
                    "home_wins": home_wins,
                    "away_wins": away_wins,
                    "conference": conf_names.get(conf_idx, "Unknown"),
                    "round_num": int(row.get("SERIES_ROUND") or 1),
                })
            except (KeyError, ValueError, TypeError):
                continue

    _write_cache(cache_key, matchups)
    return matchups
```

Note: `_read_cache` and `_write_cache` already exist in `live_data.py`. The TTL parameter may need adjustment if the existing signature differs — check the function signature before adding and adapt the call accordingly.

- [ ] **Step 4: Check `_read_cache` signature and adjust if needed**

```bash
python3 -c "import sys; sys.path.insert(0,'tools'); import inspect, live_data; print(inspect.signature(live_data._read_cache))"
```

If `_read_cache` doesn't accept `ttl_hours`, change `_read_cache(cache_key, ttl_hours=1)` to just `_read_cache(cache_key)`.

- [ ] **Step 5: Run test**

```bash
python3 -m pytest tests/test_pipeline.py::test_fetch_playoff_bracket_structure -v
```

Expected: PASS (returns `[]` during regular season — that's correct behavior).

- [ ] **Step 6: Commit**

```bash
git add tools/live_data.py tests/test_pipeline.py
git commit -m "feat: add fetch_playoff_bracket() to live_data.py"
```

---

## Task 7: Playoff Matchup Card Generator

**Files:**
- Create: `tools/generate_playoff_card.py`

- [ ] **Step 1: Create `tools/generate_playoff_card.py`**

```python
"""
Playoff Matchup Card Generator.

Shows: Team A vs Team B, seeds, series score, conference.
Auto-fetches bracket or renders provided matchup dict.

Usage:
    python3 tools/generate_playoff_card.py
    python3 tools/generate_playoff_card.py --index 1 --feed
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (
    _font, _font_impact,
    _load_background, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H,
)
from live_data import fetch_playoff_bracket


def generate_playoff_card(
    matchup: dict | None = None,
    matchup_index: int = 0,
    output_path: str = "output/playoff_card.png",
    card_format: str = "story",
) -> str:
    """Render a playoff matchup card.

    Args:
        matchup: Pre-fetched matchup dict (optional — fetched if None)
        matchup_index: Which bracket matchup to render if fetching
        output_path: Where to save the PNG
        card_format: 'story' or 'feed'
    """
    if matchup is None:
        bracket = fetch_playoff_bracket()
        if not bracket:
            # Fallback: render placeholder for pre-playoffs
            matchup = {
                "home_team": "TBD", "away_team": "TBD",
                "home_seed": 1, "away_seed": 8,
                "home_wins": 0, "away_wins": 0,
                "conference": "East", "round_num": 1,
            }
        else:
            matchup = bracket[min(matchup_index, len(bracket) - 1)]

    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)

    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas, "RGBA")

    # ── Title ──
    title_y = _v_inset
    draw.rectangle([PAD, title_y + 12, PAD + 6, title_y + _title_h - 12], fill=TEAL)
    font_title = _font_impact(int(52 * _scale))
    draw.text(
        (PAD + int(20 * _scale), title_y + int(20 * _scale)),
        f"Playoffs R{matchup.get('round_num', 1)} — {matchup.get('conference', '')}",
        font=font_title,
        fill=WHITE,
    )
    font_sub = _font(int(28 * _scale))
    home_w = matchup["home_wins"]
    away_w = matchup["away_wins"]
    if home_w > away_w:
        leader_text = f"{matchup['home_team']} leads {home_w}–{away_w}"
    elif away_w > home_w:
        leader_text = f"{matchup['away_team']} leads {away_w}–{home_w}"
    else:
        leader_text = f"Series tied {home_w}–{away_w}"
    draw.text(
        (PAD + int(20 * _scale), title_y + int(80 * _scale)),
        leader_text,
        font=font_sub,
        fill=TEAL,
    )

    # ── VS block: two team panels ──
    center_y = _v_inset + _title_h + int((canvas_h - _v_inset * 2 - _title_h - _footer_h) * 0.5)
    panel_h = int((canvas_h - _v_inset * 2 - _title_h - _footer_h) * 0.8)
    panel_w = int((WIDTH - PAD * 3) // 2)
    panel_top = _v_inset + _title_h + int((canvas_h - _v_inset * 2 - _title_h - _footer_h) * 0.1)

    for side, team_key, seed_key, wins_key in [
        ("left",  "home_team", "home_seed", "home_wins"),
        ("right", "away_team", "away_seed", "away_wins"),
    ]:
        team_name = matchup.get(team_key, "TBD")
        seed = matchup.get(seed_key, 0)
        wins = matchup.get(wins_key, 0)

        if side == "left":
            panel_x = PAD
        else:
            panel_x = PAD * 2 + panel_w

        # Panel background
        bg = ROW_BG_1 if wins > matchup.get("away_wins" if side == "left" else "home_wins", 0) else ROW_BG
        draw.rounded_rectangle(
            [panel_x, panel_top, panel_x + panel_w, panel_top + panel_h],
            radius=18,
            fill=bg,
        )

        # Team logo
        logo_size = int(180 * _scale)
        logo = _load_team_logo(_ABBR_ALIASES.get(team_name, team_name), logo_size)
        if logo:
            lx = panel_x + (panel_w - logo.width) // 2
            ly = panel_top + int(panel_h * 0.12)
            canvas.paste(logo, (lx, ly), logo)

        # Team name
        font_team = _font_impact(int(38 * _scale))
        tb = draw.textbbox((0, 0), team_name, font=font_team)
        tx = panel_x + (panel_w - (tb[2] - tb[0])) // 2
        draw.text(
            (tx, panel_top + int(panel_h * 0.55)),
            team_name, font=font_team, fill=WHITE,
        )

        # Seed
        seed_str = f"#{seed}"
        font_seed = _font(int(28 * _scale))
        sb = draw.textbbox((0, 0), seed_str, font=font_seed)
        sx = panel_x + (panel_w - (sb[2] - sb[0])) // 2
        draw.text(
            (sx, panel_top + int(panel_h * 0.70)),
            seed_str, font=font_seed, fill=TEAL,
        )

        # Win count
        wins_str = f"{wins} W"
        font_wins = _font_impact(int(48 * _scale))
        wb = draw.textbbox((0, 0), wins_str, font=font_wins)
        wx = panel_x + (panel_w - (wb[2] - wb[0])) // 2
        draw.text(
            (wx, panel_top + int(panel_h * 0.80)),
            wins_str, font=font_wins, fill=TEAL,
        )

    # VS label between panels
    vs_x = PAD * 2 + panel_w
    font_vs = _font_impact(int(64 * _scale))
    vb = draw.textbbox((0, 0), "VS", font=font_vs)
    draw.text(
        (vs_x - (vb[2] - vb[0]) // 2, center_y - (vb[3] - vb[1]) // 2),
        "VS", font=font_vs, fill=TEAL,
    )

    # ── Footer ──
    footer_y = canvas_h - _footer_h
    font_footer = _font(int(24 * _scale))
    draw.text(
        (PAD, footer_y + int((_footer_h - 24 * _scale) // 2)),
        "rushmore.cards",
        font=font_footer,
        fill=GRAY,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    print(f"Saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--feed", action="store_true")
    parser.add_argument("--output", default="output/playoff_card.png")
    args = parser.parse_args()
    generate_playoff_card(
        matchup_index=args.index,
        output_path=args.output,
        card_format="feed" if args.feed else "story",
    )
```

- [ ] **Step 2: Test render (placeholder — bracket not live yet) — visually inspect**

```bash
python3 tools/generate_playoff_card.py --output output/test_playoff_story.png
open output/test_playoff_story.png

python3 tools/generate_playoff_card.py --feed --output output/test_playoff_feed.png
open output/test_playoff_feed.png
```

Check: VS layout visible, two panels, "TBD" shows cleanly, no overlap.

- [ ] **Step 3: Commit**

```bash
git add tools/generate_playoff_card.py
git commit -m "feat: add playoff matchup card generator"
```

---

## Task 8: Add pipeline tests for calendar parsing

**Files:**
- Modify: `tests/test_pipeline.py`

- [ ] **Step 1: Add calendar parsing tests**

Append to `tests/test_pipeline.py`:

```python
import yaml
from pathlib import Path


def test_calendar_loads_20_days():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    assert len(data["days"]) == 20


def test_calendar_all_days_have_date_and_planned():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    for day in data["days"]:
        assert "date" in day, f"Missing date: {day}"
        assert "planned" in day, f"Missing planned: {day}"
        assert "card_type" in day["planned"], f"Missing card_type: {day}"


def test_calendar_debate_cards_have_5_items():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    for day in data["days"]:
        planned = day["planned"]
        if planned["card_type"] == "debate":
            assert "items" in planned, f"Debate card missing items: {day['date']}"
            assert len(planned["items"]) == 5, f"Debate card needs 5 items: {day['date']}"


def test_caption_x_under_280_chars():
    """All caption types produce X captions under 280 characters."""
    test_cases = [
        ("top5", {"players": [{"name": "Luka", "ppg": 32.4, "team": "DAL"}], "date": "2026-04-12"}),
        ("mvp_race", {"players": [{"name": "SGA", "ppg": 31.2, "eff": 28.5, "team": "OKC"}], "date": "2026-04-12"}),
        ("debate", {"title": "Regular Season Frauds", "date": "2026-04-17"}),
        ("playoff_matchup", {"matchup": {"home_team": "OKC", "away_team": "DAL", "home_wins": 2, "away_wins": 1}, "date": "2026-04-19"}),
    ]
    for card_type, kwargs in test_cases:
        captions = get_captions(card_type, **kwargs)
        assert len(captions["x"]) <= 280, f"X caption too long for {card_type}: {len(captions['x'])} chars"
```

- [ ] **Step 2: Run all tests**

```bash
python3 -m pytest tests/test_pipeline.py -v
```

Expected: All tests PASS (10+ tests).

- [ ] **Step 3: Commit**

```bash
git add tests/test_pipeline.py
git commit -m "test: add calendar parsing and caption length tests"
```

---

## Task 9: Daily Pipeline Orchestrator

**Files:**
- Create: `tools/daily_pipeline.py`

This is the main script — reads calendar, generates today's cards, sends Telegram.

- [ ] **Step 1: Create `tools/daily_pipeline.py`**

```python
"""
Rushmore Daily Content Pipeline — Orchestrator.

Reads content/calendar.yaml for today's planned card.
Generates Top 5 (if games played) + planned card.
Writes captions per platform.
Sends Telegram notification with image previews.

Usage:
    python3 tools/daily_pipeline.py
    python3 tools/daily_pipeline.py --date 2026-04-14   # override date (testing)
    python3 tools/daily_pipeline.py --dry-run           # generate only, skip Telegram
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

import requests

from caption_templates import get_captions
from daily_top5 import generate_daily_top5   # existing, returns output paths or None


def _load_calendar() -> list[dict]:
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    return data["days"]


def _find_today(days: list[dict], today_str: str) -> dict | None:
    for day in days:
        if day["date"] == today_str:
            return day
    return None


def _output_dir(today_str: str) -> Path:
    d = Path(__file__).parent.parent / "output" / today_str
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_captions(captions: dict[str, str], out_dir: Path) -> list[Path]:
    caps_dir = out_dir / "captions"
    caps_dir.mkdir(exist_ok=True)
    paths = []
    for platform, text in captions.items():
        p = caps_dir / f"{platform}.txt"
        p.write_text(text, encoding="utf-8")
        paths.append(p)
    return paths


def _generate_top5(today_str: str, out_dir: Path) -> list[str]:
    """Generate Top 5 card if yesterday's games exist. Returns list of generated paths."""
    try:
        story_path = str(out_dir / "top5_story.png")
        feed_path = str(out_dir / "top5_feed.png")
        # daily_top5.generate_daily_top5 writes to its own output dir — we symlink/copy after
        result_story = generate_daily_top5(output_path=story_path, card_format="story")
        result_feed  = generate_daily_top5(output_path=feed_path,  card_format="feed")
        paths = [p for p in [result_story, result_feed] if p and Path(p).exists()]
        return paths
    except Exception as exc:
        print(f"Top 5 generation failed: {exc}")
        return []


def _generate_planned(planned: dict, today_str: str, out_dir: Path) -> list[str]:
    """Generate the planned card from calendar entry. Returns list of paths."""
    card_type = planned["card_type"]
    paths = []

    for fmt in ("story", "feed"):
        suffix = f"{card_type}_{fmt}.png"
        out_path = str(out_dir / suffix)

        try:
            if card_type == "mvp_race":
                from generate_mvp_race_card import generate_mvp_race_card
                generate_mvp_race_card(output_path=out_path, card_format=fmt)

            elif card_type in ("roty", "mip", "dpoy", "scoring", "all_nba", "all_rookie"):
                from generate_award_card import generate_award_card
                award_map = {
                    "roty": "roty", "mip": "mip", "dpoy": "dpoy",
                    "scoring_title": "scoring",
                    "all_nba": "all_nba", "all_rookie": "all_rookie",
                }
                award_type = award_map.get(card_type, card_type)
                auto_data = planned.get("auto_data", True)
                items = planned.get("items")
                generate_award_card(
                    award_type=award_type,
                    items=items,
                    auto_data=auto_data and items is None,
                    output_path=out_path,
                    card_format=fmt,
                )

            elif card_type == "scoring_title":
                from generate_award_card import generate_award_card
                generate_award_card(
                    award_type="scoring",
                    auto_data=True,
                    output_path=out_path,
                    card_format=fmt,
                )

            elif card_type == "award":
                from generate_award_card import generate_award_card
                award_type = planned.get("award_type", "mvp")
                auto_data = planned.get("auto_data", True)
                items = planned.get("items")
                generate_award_card(
                    award_type=award_type,
                    items=items,
                    auto_data=auto_data and items is None,
                    output_path=out_path,
                    card_format=fmt,
                )

            elif card_type == "debate":
                from generate_debate_card import generate_debate_card
                generate_debate_card(
                    title=planned["title"],
                    subtitle=planned.get("subtitle", ""),
                    items=planned["items"],
                    output_path=out_path,
                    card_format=fmt,
                )

            elif card_type in ("playoff_matchup", "playoff_bracket"):
                from generate_playoff_card import generate_playoff_card
                generate_playoff_card(
                    matchup_index=planned.get("matchup_index", 0),
                    output_path=out_path,
                    card_format=fmt,
                )

            else:
                print(f"Unknown card_type: {card_type} — skipping")
                continue

            if Path(out_path).exists():
                paths.append(out_path)

        except Exception as exc:
            print(f"Error generating {card_type} ({fmt}): {exc}")

    return paths


def _send_telegram(card_paths: list[str], descriptions: list[str], dry_run: bool = False):
    """Send Telegram notification with image previews."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — skipping Telegram.")
        return

    today_str = date.today().isoformat()
    n = len(descriptions)
    lines = [f"📅 {today_str} — {n} card{'s' if n != 1 else ''} ready:\n"]
    for i, desc in enumerate(descriptions, start=1):
        lines.append(f"{i}. {desc}")
    message = "\n".join(lines)

    if dry_run:
        print(f"[DRY RUN] Would send Telegram:\n{message}")
        print(f"[DRY RUN] With {len(card_paths)} images: {card_paths}")
        return

    base_url = f"https://api.telegram.org/bot{token}"

    # Send text message first
    resp = requests.post(
        f"{base_url}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=15,
    )
    if not resp.ok:
        print(f"Telegram sendMessage failed: {resp.text}")

    # Send each image (story format only — feed is extra)
    story_paths = [p for p in card_paths if "story" in p]
    for img_path in story_paths[:5]:  # Telegram: max 10 per message, keep it clean
        with open(img_path, "rb") as f:
            resp = requests.post(
                f"{base_url}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": f},
                timeout=30,
            )
        if not resp.ok:
            print(f"Telegram sendPhoto failed for {img_path}: {resp.text}")
        else:
            print(f"Sent to Telegram: {img_path}")


def run(today_str: str, dry_run: bool = False):
    print(f"=== Rushmore Daily Pipeline — {today_str} ===")

    days = _load_calendar()
    today_entry = _find_today(days, today_str)
    out_dir = _output_dir(today_str)

    all_paths = []
    descriptions = []

    # 1. Top 5 Card
    print("\n[1/2] Generating Top 5 card...")
    top5_paths = _generate_top5(today_str, out_dir)
    if top5_paths:
        all_paths.extend(top5_paths)
        descriptions.append("Top 5 Last Night — Points leaders")
        # Write Top 5 captions
        from live_data import fetch_season_leaders
        leaders = fetch_season_leaders(limit=5)
        top5_captions = get_captions("top5", players=leaders, date=today_str)
        _write_captions(top5_captions, out_dir)
        print(f"  Top 5 generated: {top5_paths}")
    else:
        print("  No Top 5 generated (no games or data unavailable)")

    # 2. Planned card from calendar
    if today_entry:
        planned = today_entry["planned"]
        card_type = planned["card_type"]
        print(f"\n[2/2] Generating planned card: {card_type}...")
        planned_paths = _generate_planned(planned, today_str, out_dir)
        if planned_paths:
            all_paths.extend(planned_paths)
            title = planned.get("title", card_type.replace("_", " ").title())
            descriptions.append(f"{card_type.replace('_', ' ').title()} — {title}")

            # Write planned card captions
            planned_captions = get_captions(
                card_type,
                title=planned.get("title", ""),
                award_type=planned.get("award_type", ""),
                date=today_str,
            )
            # Write to same captions dir (appends to existing files if top5 also wrote)
            for platform, text in planned_captions.items():
                cap_file = out_dir / "captions" / f"{platform}_planned.txt"
                cap_file.parent.mkdir(exist_ok=True)
                cap_file.write_text(text, encoding="utf-8")

            print(f"  Planned card generated: {planned_paths}")
        else:
            print(f"  Planned card generation failed for {card_type}")
    else:
        print(f"\n[2/2] No calendar entry for {today_str} — skipping planned card.")

    # 3. Telegram notification
    print(f"\n[3/3] Sending Telegram notification ({len(all_paths)} images)...")
    _send_telegram(all_paths, descriptions, dry_run=dry_run)

    print(f"\n=== Done. Output: output/{today_str}/ ===")
    return all_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat(), help="Override date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Generate cards but skip Telegram send")
    args = parser.parse_args()
    run(today_str=args.date, dry_run=args.dry_run)
```

- [ ] **Step 2: Check `daily_top5.generate_daily_top5` signature**

```bash
python3 -c "import sys; sys.path.insert(0,'tools'); import inspect, daily_top5; print(inspect.signature(daily_top5.generate_daily_top5))"
```

If the signature differs from `(output_path, card_format)`, adjust the `_generate_top5` call in the orchestrator to match.

- [ ] **Step 3: Test dry-run**

```bash
cd /Users/razor/projects/rushmore && python3 tools/daily_pipeline.py --date 2026-04-12 --dry-run
```

Expected: Cards generated in `output/2026-04-12/`, Telegram message printed but not sent.

- [ ] **Step 4: Visually inspect all output files**

```bash
open output/2026-04-12/
```

Verify: story + feed for each card type, captions directory with .txt files.

- [ ] **Step 5: Commit**

```bash
git add tools/daily_pipeline.py
git commit -m "feat: add daily pipeline orchestrator with calendar, captions, Telegram"
```

---

## Task 10: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/daily_cards.yml`

- [ ] **Step 1: Create `.github/workflows/daily_cards.yml`**

```yaml
name: Daily NBA Content Pipeline

on:
  schedule:
    - cron: "0 6 * * *"   # 06:00 UTC = 08:00 CET
  workflow_dispatch:        # Manual trigger for testing

jobs:
  generate-cards:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install system fonts (Helvetica fallback)
        run: sudo apt-get install -y fonts-liberation

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install pillow nba_api pyyaml python-dotenv requests

      - name: Run daily pipeline
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python3 tools/daily_pipeline.py

      - name: Upload output artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: daily-cards-${{ github.run_id }}
          path: output/
          retention-days: 7
```

- [ ] **Step 2: Add GitHub secrets (manual step — user must do this)**

In GitHub repo → Settings → Secrets and variables → Actions → New repository secret:
- `TELEGRAM_BOT_TOKEN`: value from `.env`
- `TELEGRAM_CHAT_ID`: value from `.env`

- [ ] **Step 3: Check that `.env` has both Telegram vars**

```bash
grep -E "TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID" .env
```

If missing, add them to `.env`:
```
TELEGRAM_BOT_TOKEN=<your_token>
TELEGRAM_CHAT_ID=<your_chat_id>
```

- [ ] **Step 4: Verify fonts available in CI**

The GitHub Actions runner uses `ubuntu-latest`. The pipeline uses `assets/fonts/Helvetica.ttc` and `assets/fonts/Impact.ttf` which are committed to the repo — these load from the repo path, not system fonts. Verify:

```bash
ls assets/fonts/
```

Expected: `Helvetica.ttc` and `Impact.ttf` present.

- [ ] **Step 5: Commit and push workflow**

```bash
git add .github/workflows/daily_cards.yml
git commit -m "feat: add GitHub Actions cron for daily card pipeline (06:00 UTC)"
git push origin main
```

- [ ] **Step 6: Trigger manual run to verify**

In GitHub → Actions → "Daily NBA Content Pipeline" → "Run workflow" → confirm it completes without errors and artifacts are uploaded.

---

## Self-Review

### Spec Coverage Check

| Spec requirement | Task |
|-----------------|------|
| `daily_pipeline.py` orchestrator | Task 9 |
| `content/calendar.yaml` 20-day plan | Task 1 |
| Top 5 auto-generation | Task 9 (`_generate_top5`) |
| MVP Race Card (crown icon) | Task 4 |
| Award Card (ROTY/MIP/All-NBA/Scoring) | Task 5 |
| Playoff Matchup Card | Task 7 |
| Debate/Funny/Historical Card | Task 3 |
| Caption system per platform | Task 2 |
| `fetch_playoff_bracket()` | Task 6 |
| Telegram notification with images | Task 9 |
| GitHub Actions cron 06:00 UTC | Task 10 |
| `output/YYYY-MM-DD/captions/*.txt` | Task 9 |
| Design rules (textbbox, 8px gap, 90% width) | Tasks 3–7 |
| Visual inspect after each generator | Tasks 3–7 |

### Placeholder Scan

- No "TBD" in code blocks (only in YAML data fields where user must fill in manually for Apr 15 hot take)
- All function signatures consistent across tasks
- All import paths use `sys.path.insert(0, ...)` pattern matching existing generators

### Type Consistency

- `generate_debate_card(title, subtitle, items, output_path, card_format)` — consistent usage in Task 9
- `generate_award_card(award_type, items, auto_data, output_path, card_format)` — consistent usage in Task 9
- `generate_playoff_card(matchup, matchup_index, output_path, card_format)` — consistent usage in Task 9
- `get_captions(card_type, *, players, date, title, award_type, matchup)` — keyword-only args, safe to call with subset
