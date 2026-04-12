"""
Playoff Matchup Card Generator — 2025-26 NBA Playoffs.

Shows a playoff series matchup: two team panels side-by-side with VS
in the middle, seeds, series score, conference/round label.

Usage:
    python3 tools/generate_playoff_card.py
    python3 tools/generate_playoff_card.py --feed        # Instagram feed (1080x1080)
    python3 tools/generate_playoff_card.py --index 2     # use 3rd bracket entry
    python3 tools/generate_playoff_card.py --output output/my_card.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (  # noqa: E402
    _font, _font_impact,
    _load_background, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H,
)
from live_data import fetch_playoff_bracket  # noqa: E402

PLACEHOLDER: dict = {
    "home_team": "TBD", "away_team": "TBD",
    "home_seed": 1, "away_seed": 8,
    "home_wins": 0, "away_wins": 0,
    "conference": "East", "round_num": 1,
}


def _series_label(home_wins: int, away_wins: int, home_team: str, away_team: str) -> str:
    """Return a human-readable series status line."""
    if home_wins == away_wins:
        return f"Series tied {home_wins}–{away_wins}"
    elif home_wins > away_wins:
        return f"{home_team} leads {home_wins}–{away_wins}"
    else:
        return f"{away_team} leads {away_wins}–{home_wins}"


def generate_playoff_card(
    matchup: dict | None = None,
    matchup_index: int = 0,
    output_path: str = "output/playoff_card.png",
    card_format: str = "story",
) -> str:
    """Generate a playoff matchup card.

    Args:
        matchup:       Pre-built matchup dict (optional). If None, fetch from bracket.
        matchup_index: Which bracket entry to use when fetching (default 0).
        output_path:   Where to save the PNG.
        card_format:   "story" (1080×1920) or "feed" (1080×1080).

    Returns:
        Absolute path to the saved image.
    """
    # ── Data ──────────────────────────────────────────────────────────────────
    if matchup is None:
        bracket = fetch_playoff_bracket()
        if bracket and matchup_index < len(bracket):
            matchup = bracket[matchup_index]
        else:
            print("[playoff_card] No bracket data — using placeholder matchup.")
            matchup = PLACEHOLDER.copy()

    home_team  = matchup["home_team"]
    away_team  = matchup["away_team"]
    home_seed  = matchup["home_seed"]
    away_seed  = matchup["away_seed"]
    home_wins  = matchup["home_wins"]
    away_wins  = matchup["away_wins"]
    conference = matchup["conference"]
    round_num  = matchup["round_num"]

    # ── Scale factors ─────────────────────────────────────────────────────────
    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale   = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)

    # ── Canvas + Background ───────────────────────────────────────────────────
    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")

    # Dark overlay
    overlay = Image.new("RGBA", (WIDTH, canvas_h), (0, 0, 0, 140))
    canvas.alpha_composite(overlay)

    # Top gradient
    grad_top_h = _title_h + 60
    grad = Image.new("RGBA", (WIDTH, grad_top_h), (0, 0, 0, 0))
    for y in range(grad_top_h):
        alpha = int(200 * (1 - y / grad_top_h) + 60)
        ImageDraw.Draw(grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(grad, (0, 0))

    # Bottom gradient
    grad_bot_h = max(80, canvas_h // 12)
    bot_grad = Image.new("RGBA", (WIDTH, grad_bot_h), (0, 0, 0, 0))
    for y in range(grad_bot_h):
        alpha = int(120 * (y / grad_bot_h))
        ImageDraw.Draw(bot_grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(bot_grad, (0, canvas_h - grad_bot_h))

    draw = ImageDraw.Draw(canvas)

    # ── Title block ───────────────────────────────────────────────────────────
    title_text = f"Playoffs R{round_num} — {conference.upper()}"
    series_text = _series_label(home_wins, away_wins, home_team, away_team)

    title_font  = _font_impact(max(52, int(88 * _scale)))
    series_font = _font(max(18, int(30 * _scale)))

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    t_w    = t_bbox[2] - t_bbox[0]
    t_h    = t_bbox[3] - t_bbox[1]

    s_bbox = draw.textbbox((0, 0), series_text, font=series_font)
    s_w    = s_bbox[2] - s_bbox[0]
    s_h    = s_bbox[3] - s_bbox[1]

    block_h = t_h + 12 + s_h
    block_y = _v_inset + (_title_h - block_h) // 2

    # Teal accent bar on left
    bar_x = PAD
    bar_y = block_y - 4
    bar_h = block_h + 8
    bar = Image.new("RGBA", (5, bar_h), (*TEAL, 230))
    canvas.alpha_composite(bar, (bar_x, bar_y))
    draw = ImageDraw.Draw(canvas)

    # Title text (left-aligned after accent bar)
    title_x = bar_x + 18
    draw.text((title_x, block_y), title_text, fill=WHITE, font=title_font)

    series_y = block_y + t_h + 12
    draw.text((title_x, series_y), series_text, fill=(*TEAL, 220), font=series_font)

    # Divider under title
    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Main panel area ───────────────────────────────────────────────────────
    panel_area_y = _v_inset + _title_h
    panel_area_h = canvas_h - _v_inset * 2 - _title_h - _footer_h

    # Panel dimensions — two panels with a VS gap in the middle
    vs_gap = max(80, int(140 * _scale))
    panel_w = (WIDTH - PAD * 2 - vs_gap) // 2
    panel_h = panel_area_h - 20  # small vertical margin

    home_panel_x = PAD
    away_panel_x = PAD + panel_w + vs_gap
    panel_y = panel_area_y + 10

    # Decide which panel gets highlighted background (more wins = highlight)
    home_bg = ROW_BG_1 if home_wins >= away_wins else ROW_BG
    away_bg = ROW_BG_1 if away_wins > home_wins else ROW_BG

    # Draw panels
    home_panel = Image.new("RGBA", (panel_w, panel_h), home_bg)
    away_panel = Image.new("RGBA", (panel_w, panel_h), away_bg)
    canvas.alpha_composite(home_panel, (home_panel_x, panel_y))
    canvas.alpha_composite(away_panel, (away_panel_x, panel_y))
    draw = ImageDraw.Draw(canvas)

    # Teal left accent bar on each panel
    home_bar = Image.new("RGBA", (5, panel_h), (*TEAL, 200))
    away_bar = Image.new("RGBA", (5, panel_h), (*TEAL, 200))
    canvas.alpha_composite(home_bar, (home_panel_x, panel_y))
    canvas.alpha_composite(away_bar, (away_panel_x, panel_y))
    draw = ImageDraw.Draw(canvas)

    # ── VS text (centered between panels) ────────────────────────────────────
    vs_font = _font_impact(max(60, int(110 * _scale)))
    vs_bbox = draw.textbbox((0, 0), "VS", font=vs_font)
    vs_w    = vs_bbox[2] - vs_bbox[0]
    vs_h    = vs_bbox[3] - vs_bbox[1]
    vs_cx   = PAD + panel_w + vs_gap // 2
    vs_x    = vs_cx - vs_w // 2
    vs_y    = panel_y + (panel_h - vs_h) // 2
    draw.text((vs_x, vs_y), "VS", fill=(*TEAL, 240), font=vs_font)

    # ── Team panel content ────────────────────────────────────────────────────
    logo_size = max(120, int(180 * _scale))
    team_font  = _font_impact(max(30, int(52 * _scale)))
    seed_font  = _font_impact(max(28, int(46 * _scale)))
    wins_font  = _font_impact(max(50, int(90 * _scale)))

    def _draw_team_panel(team_name: str, seed: int, wins: int, panel_x: int):
        """Draw logo, team name, seed, and win count inside one panel."""
        nonlocal draw
        inner_w = panel_w - 10  # avoid overlap with accent bar
        cx = panel_x + 5 + inner_w // 2  # center of inner area (skip 5px bar)

        # Vertical layout: logo → name → seed → wins
        # Compute total block height first
        logo_h = logo_size
        name_bbox = draw.textbbox((0, 0), team_name, font=team_font)
        name_h    = name_bbox[3] - name_bbox[1]
        seed_str  = f"#{seed}"
        seed_bbox = draw.textbbox((0, 0), seed_str, font=seed_font)
        seed_h    = seed_bbox[3] - seed_bbox[1]
        wins_str  = f"{wins} W"
        wins_bbox = draw.textbbox((0, 0), wins_str, font=wins_font)
        wins_h    = wins_bbox[3] - wins_bbox[1]

        gap = max(8, int(16 * _scale))
        total_h = logo_h + gap + name_h + gap + seed_h + gap + wins_h
        start_y = panel_y + (panel_h - total_h) // 2

        # Logo
        logo = _load_team_logo(_ABBR_ALIASES.get(team_name, team_name), logo_size, opacity=0.90)
        logo_y = start_y
        if logo:
            logo_x = cx - logo_size // 2
            canvas.alpha_composite(logo, (logo_x, logo_y))
        else:
            # Placeholder circle if no logo
            placeholder = Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 0))
            ImageDraw.Draw(placeholder).ellipse(
                (0, 0, logo_size - 1, logo_size - 1),
                fill=(*TEAL, 60), outline=(*TEAL, 120), width=2,
            )
            canvas.alpha_composite(placeholder, (cx - logo_size // 2, logo_y))

        draw = ImageDraw.Draw(canvas)

        # Team name
        name_x = cx - (name_bbox[2] - name_bbox[0]) // 2
        name_y = logo_y + logo_h + gap
        draw.text((name_x, name_y), team_name, fill=WHITE, font=team_font)

        # Seed
        seed_x = cx - (seed_bbox[2] - seed_bbox[0]) // 2
        seed_y = name_y + name_h + gap
        draw.text((seed_x, seed_y), seed_str, fill=(*TEAL, 220), font=seed_font)

        # Win count
        wins_x = cx - (wins_bbox[2] - wins_bbox[0]) // 2
        wins_y = seed_y + seed_h + gap
        draw.text((wins_x, wins_y), wins_str, fill=(*TEAL, 240), font=wins_font)

    _draw_team_panel(home_team, home_seed, home_wins, home_panel_x)
    _draw_team_panel(away_team, away_seed, away_wins, away_panel_x)

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_font = _font(max(18, int(28 * _scale)))
    footer_text = "rushmore.cards"
    f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    f_w    = f_bbox[2] - f_bbox[0]
    f_h    = f_bbox[3] - f_bbox[1]
    f_x    = (WIDTH - f_w) // 2
    f_y    = canvas_h - _v_inset - _footer_h + (_footer_h - f_h) // 2
    draw.text((f_x, f_y), footer_text, fill=(*GRAY, 180), font=footer_font)

    # ── Save ──────────────────────────────────────────────────────────────────
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out), "PNG", optimize=True)
    print(f"[playoff_card] Saved → {out.resolve()}")
    return str(out.resolve())


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate NBA playoff matchup card.")
    parser.add_argument("--index",  type=int, default=0,                        help="Bracket entry index (default 0)")
    parser.add_argument("--feed",   action="store_true",                         help="Render as 1080×1080 feed card")
    parser.add_argument("--output", type=str, default="output/playoff_card.png", help="Output path")
    args = parser.parse_args()

    generate_playoff_card(
        matchup_index=args.index,
        output_path=args.output,
        card_format="feed" if args.feed else "story",
    )
