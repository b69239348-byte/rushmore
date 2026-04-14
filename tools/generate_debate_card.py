"""
Rushmore — Debate / List Card Generator v2

Supports three item modes detected automatically from item structure:
  - player mode: dict with 'name' (+ optional team, stats, player_id) → headshot + stats row
  - team mode:   dict with 'team' + 'context' (no player_id)          → logo-forward row
  - matchup:     dict with 'teams' (list of 2 abbrs) + 'text'         → dual-logo row
  - text mode:   plain string                                           → text row

Background is chosen per card via `bg` param or DEBATE_BG_MAP defaults.

Usage:
    python3 tools/generate_debate_card.py \
        --title "Most Likely to Ghost" \
        --subtitle "Disappear in the Playoffs" \
        --items "Trae Young,Zach LaVine,Devin Booker,Pascal Siakam,Darius Garland" \
        --bg illustrated_dunk_purple

    # With JSON items for player mode (stats + headshots):
    python3 tools/generate_debate_card.py \
        --title "Most Likely to Ghost" --subtitle "Disappear" \
        --items-json '[{"name":"Trae Young","team":"ATL","stats":"26.3 PPG · 10.8 APG","player_id":1629029}]' \
        --bg illustrated_dunk_purple --feed
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (  # noqa: E402
    _font, _font_impact,
    _load_background, _load_headshot, _initials_circle, _load_team_logo,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)
from download_headshots import download_by_ids  # noqa: E402

# ── Background map for debate cards ─────────────────────────────────────────
# Key = bg alias used in calendar.yaml; value = filename (without .png)
DEBATE_BG_MAP: dict[str, str] = {
    # Illustrated / vibrant
    "illustrated_court_orange":  "illustrated_court_orange",
    "illustrated_court_teal":    "illustrated_court_teal",
    "illustrated_dunk_purple":   "illustrated_dunk_purple",
    "illustrated_dunk_sunburst": "illustrated_dunk_sunburst",
    "illustrated_pass_gradient": "illustrated_pass_gradient",
    "illustrated_shooter_green": "illustrated_shooter_green",
    # Photographic
    "rooftop_city":         "rooftop_city",
    "night_court_outdoor":  "night_court_outdoor",
    "sunset_court":         "sunset_court",
    "indoor_arena":         "indoor_arena",
    "underground_court":    "underground_court",
    # Topic-based aliases (shorthand for calendar.yaml)
    "play_in":     "illustrated_court_orange",
    "player_take": "illustrated_dunk_purple",
    "series":      "rooftop_city",
    "award":       "indoor_arena",
    "hot_take":    "illustrated_dunk_sunburst",
    "default":     "illustrated_court_teal",
}

_FORMATS = {"story": HEIGHT, "feed": 1080}


# ── Item type detection ───────────────────────────────────────────────────────

def _is_player_item(item) -> bool:
    """Dict with 'name' and (player_id OR stats) — rendered with headshot.
    Note: 'team' alone without player_id/stats = team item, not player item."""
    if not isinstance(item, dict):
        return False
    return "name" in item and ("player_id" in item or "stats" in item)


def _is_team_item(item) -> bool:
    """Dict with 'team' and 'context' but no player_id/stats."""
    if not isinstance(item, dict):
        return False
    return "team" in item and "context" in item and "player_id" not in item and "stats" not in item


def _is_matchup_item(item) -> bool:
    """Dict with 'teams' (list of 2) and 'text'."""
    if not isinstance(item, dict):
        return False
    return "teams" in item and isinstance(item.get("teams"), list) and len(item["teams"]) == 2


def _item_text(item) -> str:
    """Extract display text from any item type."""
    if isinstance(item, str):
        return item
    return item.get("text") or item.get("name") or item.get("context") or ""


def _truncate(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> str:
    bbox = draw.textbbox((0, 0), text, font=font)
    if (bbox[2] - bbox[0]) <= max_w:
        return text
    while len(text) > 1:
        text = text[:-1].rstrip()
        candidate = text + "…"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return candidate
    return "…"


# ── Row renderers ─────────────────────────────────────────────────────────────

def _render_player_row(
    canvas: Image.Image,
    item: dict,
    row_y: int, row_h: int,
    is_top: bool,
    rank_str: str,
    fonts: dict,
    _scale: float,
):
    """Headshot + name + stats + team logo row."""
    draw = ImageDraw.Draw(canvas)

    # Panel
    panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
    canvas.alpha_composite(panel, (PAD, row_y))

    # Left accent bar
    bar_alpha = 255 if is_top else 140
    accent = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
    canvas.alpha_composite(accent, (PAD, row_y))

    draw = ImageDraw.Draw(canvas)

    RANK_W    = max(60, int(90 * _scale))
    PHOTO_SIZE = int(row_h * 0.70)

    # Rank
    r_bbox = draw.textbbox((0, 0), rank_str, font=fonts["rank"])
    r_h = r_bbox[3] - r_bbox[1]
    r_x = PAD + 5 + (RANK_W - (r_bbox[2] - r_bbox[0])) // 2
    r_y = row_y + (row_h - r_h) // 2 - r_bbox[1]
    draw.text((r_x, r_y), rank_str, fill=TEAL if is_top else (160, 160, 160), font=fonts["rank"])

    # Headshot
    photo_x = PAD + RANK_W + 8
    photo_y = row_y + (row_h - PHOTO_SIZE) // 2
    player_id = item.get("player_id", 0)
    headshot = _load_headshot(player_id, PHOTO_SIZE) if player_id else None
    if headshot is None:
        headshot = _initials_circle(item.get("name", "?"), PHOTO_SIZE)
    canvas.alpha_composite(headshot, (photo_x, photo_y))

    # Teal ring
    ring = Image.new("RGBA", (PHOTO_SIZE + 6, PHOTO_SIZE + 6), (0, 0, 0, 0))
    ring_alpha = 220 if is_top else 100
    ImageDraw.Draw(ring).ellipse(
        (0, 0, PHOTO_SIZE + 5, PHOTO_SIZE + 5),
        outline=(*TEAL, ring_alpha), width=3,
    )
    canvas.alpha_composite(ring, (photo_x - 3, photo_y - 3))

    draw = ImageDraw.Draw(canvas)

    # Team logo on right
    team = item.get("team", "")
    _logo_size = int(row_h * 0.55)
    logo = _load_team_logo(team, _logo_size, opacity=0.55) if team else None
    logo_x = WIDTH - PAD - _logo_size - 12
    if logo:
        logo_y = row_y + (row_h - _logo_size) // 2
        canvas.alpha_composite(logo, (logo_x, logo_y))
        draw = ImageDraw.Draw(canvas)

    # Text block
    text_x    = photo_x + PHOTO_SIZE + 16
    text_max_w = (logo_x if logo else WIDTH - PAD) - text_x - 12

    name = item.get("name", "").upper()
    n_bbox = draw.textbbox((0, 0), name, font=fonts["name"])
    if (n_bbox[2] - n_bbox[0]) > text_max_w:
        parts = item.get("name", "").split()
        if len(parts) >= 2:
            # Try last name(s) only first — cleaner than "P. BANCHERO"
            last_only = " ".join(parts[1:]).upper()
            lb = draw.textbbox((0, 0), last_only, font=fonts["name"])
            if (lb[2] - lb[0]) <= text_max_w:
                name = last_only
                n_bbox = lb
            else:
                name = f"{parts[0][0]}. {last_only}"
                n_bbox = draw.textbbox((0, 0), name, font=fonts["name"])
    name = _truncate(draw, name, fonts["name"], text_max_w)

    stats  = item.get("stats", "")
    _name_h    = max(20, int(46 * _scale))
    _stats_h   = max(13, int(26 * _scale))
    _meta_h    = max(11, int(24 * _scale))
    _stats_gap = 4  # gap between wrapped stats lines

    has_stats = bool(stats)

    # Pre-compute stats lines — wrap to max 2 lines if text overflows
    stats_lines: list[str] = []
    if has_stats:
        s_bbox = draw.textbbox((0, 0), stats, font=fonts["stats"])
        if (s_bbox[2] - s_bbox[0]) <= text_max_w:
            stats_lines = [stats]
        else:
            words = stats.split()
            acc, line = [], []
            for word in words:
                test = " ".join(line + [word])
                bw = draw.textbbox((0, 0), test, font=fonts["stats"])
                if (bw[2] - bw[0]) > text_max_w and line:
                    acc.append(" ".join(line))
                    line = [word]
                else:
                    line.append(word)
            if line:
                acc.append(" ".join(line))
            stats_lines = acc[:2]

    stats_block_h = (
        len(stats_lines) * _stats_h + (len(stats_lines) - 1) * _stats_gap
    ) if stats_lines else 0

    block_h = _name_h + (8 + stats_block_h if has_stats else 0) + (4 + _meta_h if team else 0)
    text_y = row_y + (row_h - block_h) // 2

    draw.text((text_x, text_y), name, fill=WHITE, font=fonts["name"])

    cur_y = text_y + _name_h + 4
    if team:
        draw.text((text_x, cur_y), team, fill=(*TEAL, 180), font=fonts["meta"])
        cur_y += _meta_h + 4

    for sl in stats_lines:
        draw.text((text_x, cur_y), sl, fill=GRAY, font=fonts["stats"])
        cur_y += _stats_h + _stats_gap


def _render_team_row(
    canvas: Image.Image,
    item: dict,
    row_y: int, row_h: int,
    is_top: bool,
    rank_str: str,
    fonts: dict,
    _scale: float,
):
    """Team logo (prominent) + team name + context text."""
    draw = ImageDraw.Draw(canvas)

    panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
    canvas.alpha_composite(panel, (PAD, row_y))

    bar_alpha = 255 if is_top else 140
    accent = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
    canvas.alpha_composite(accent, (PAD, row_y))

    draw = ImageDraw.Draw(canvas)

    RANK_W = max(60, int(90 * _scale))
    LOGO_SIZE = int(row_h * 0.72)  # bigger than team-logo-in-headshot-slot

    # Rank
    r_bbox = draw.textbbox((0, 0), rank_str, font=fonts["rank"])
    r_h = r_bbox[3] - r_bbox[1]
    r_x = PAD + 5 + (RANK_W - (r_bbox[2] - r_bbox[0])) // 2
    r_y = row_y + (row_h - r_h) // 2 - r_bbox[1]
    draw.text((r_x, r_y), rank_str, fill=TEAL if is_top else (160, 160, 160), font=fonts["rank"])

    # Team logo (primary, higher opacity)
    team = item.get("team", "")
    logo = _load_team_logo(team, LOGO_SIZE, opacity=0.90) if team else None
    logo_x = PAD + RANK_W + 8
    if logo:
        logo_y = row_y + (row_h - LOGO_SIZE) // 2
        canvas.alpha_composite(logo, (logo_x, logo_y))
        draw = ImageDraw.Draw(canvas)

    # Background logo on right (ghost)
    _bg_logo_size = int(row_h * 0.55)
    bg_logo = _load_team_logo(team, _bg_logo_size, opacity=0.18) if team else None
    if bg_logo:
        canvas.alpha_composite(bg_logo, (WIDTH - PAD - _bg_logo_size - 8, row_y + (row_h - _bg_logo_size) // 2))
        draw = ImageDraw.Draw(canvas)

    # Text
    text_x   = logo_x + (LOGO_SIZE + 16 if logo else 0)
    text_maxw = WIDTH - PAD - text_x - _bg_logo_size - 20

    team_name = item.get("name", team)
    context   = item.get("context", "")

    name_text = team_name.upper()
    name_text = _truncate(draw, name_text, fonts["name"], text_maxw)

    _name_h    = max(20, int(46 * _scale))
    _context_h = max(13, int(26 * _scale))

    block_h = _name_h + (6 + _context_h if context else 0)
    text_y  = row_y + (row_h - block_h) // 2

    draw.text((text_x, text_y), name_text, fill=WHITE, font=fonts["name"])
    if context:
        ctx = _truncate(draw, context, fonts["stats"], text_maxw)
        draw.text((text_x, text_y + _name_h + 6), ctx, fill=GRAY, font=fonts["stats"])


def _render_matchup_row(
    canvas: Image.Image,
    item: dict,
    row_y: int, row_h: int,
    is_top: bool,
    rank_str: str,
    fonts: dict,
    _scale: float,
):
    """Two team logos side by side + matchup text."""
    draw = ImageDraw.Draw(canvas)

    panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
    canvas.alpha_composite(panel, (PAD, row_y))

    bar_alpha = 255 if is_top else 140
    accent = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
    canvas.alpha_composite(accent, (PAD, row_y))

    draw = ImageDraw.Draw(canvas)

    RANK_W   = max(60, int(90 * _scale))
    LOGO_SIZE = int(row_h * 0.58)
    VS_GAP    = 8

    # Rank
    r_bbox = draw.textbbox((0, 0), rank_str, font=fonts["rank"])
    r_h = r_bbox[3] - r_bbox[1]
    r_x = PAD + 5 + (RANK_W - (r_bbox[2] - r_bbox[0])) // 2
    r_y = row_y + (row_h - r_h) // 2 - r_bbox[1]
    draw.text((r_x, r_y), rank_str, fill=TEAL if is_top else (160, 160, 160), font=fonts["rank"])

    teams = item.get("teams", [])
    pick  = item.get("pick", "")
    logo_start_x = PAD + RANK_W + 8

    # Determine opacity: winner full, loser dimmed
    op1 = 0.88
    op2 = 0.88
    if pick and len(teams) >= 2:
        if pick == teams[0]:
            op2 = 0.28
        elif pick == teams[1]:
            op1 = 0.28

    # Logo 1
    logo1 = _load_team_logo(teams[0], LOGO_SIZE, opacity=op1) if teams else None
    if logo1:
        canvas.alpha_composite(logo1, (logo_start_x, row_y + (row_h - LOGO_SIZE) // 2))

    # VS dot
    vs_x = logo_start_x + LOGO_SIZE + VS_GAP
    draw = ImageDraw.Draw(canvas)
    vs_font = _font(max(14, int(22 * _scale)), bold=True)
    vs_bbox = draw.textbbox((0, 0), "vs", font=vs_font)
    vs_h = vs_bbox[3] - vs_bbox[1]
    draw.text((vs_x, row_y + (row_h - vs_h) // 2 - vs_bbox[1]), "vs", fill=(*TEAL, 160), font=vs_font)
    vs_w = vs_bbox[2] - vs_bbox[0]

    # Logo 2
    logo2_x = vs_x + vs_w + VS_GAP
    logo2 = _load_team_logo(teams[1], LOGO_SIZE, opacity=op2) if len(teams) > 1 else None
    if logo2:
        canvas.alpha_composite(logo2, (logo2_x, row_y + (row_h - LOGO_SIZE) // 2))

    draw = ImageDraw.Draw(canvas)

    # Text layout: try right side first; if too narrow, go below the logos
    text_x    = logo2_x + (LOGO_SIZE + 14 if logo2 else 0)
    text_maxw = WIDTH - PAD - text_x - 12
    matchup_text = item.get("text", " vs ".join(teams))

    # Measure text in stats font
    t_bbox_full = draw.textbbox((0, 0), matchup_text, font=fonts["stats"])
    text_w_full = t_bbox_full[2] - t_bbox_full[0]

    if text_w_full <= text_maxw:
        # Fits to the right
        display_text = matchup_text
        t_bbox = draw.textbbox((0, 0), display_text, font=fonts["stats"])
        t_h    = t_bbox[3] - t_bbox[1]
        draw.text((text_x, row_y + (row_h - t_h) // 2 - t_bbox[1]),
                  display_text, fill=WHITE if is_top else (220, 220, 220), font=fonts["stats"])
    else:
        # Wrap below the logos: use full row width minus rank column
        wrap_x    = PAD + RANK_W + 8
        wrap_maxw = WIDTH - PAD - wrap_x - 12
        small_font = fonts["stats"]
        words = matchup_text.split()
        lines, line = [], []
        for word in words:
            test = " ".join(line + [word])
            bw = draw.textbbox((0, 0), test, font=small_font)
            if (bw[2] - bw[0]) > wrap_maxw and line:
                lines.append(" ".join(line))
                line = [word]
            else:
                line.append(word)
        if line:
            lines.append(" ".join(line))
        lines = lines[:2]

        line_h = max(14, int(28 * _scale))
        logos_bottom = row_y + (row_h - LOGO_SIZE) // 2 + LOGO_SIZE + 4
        for li, ln in enumerate(lines):
            lb = draw.textbbox((0, 0), ln, font=small_font)
            lh = lb[3] - lb[1]
            draw.text((wrap_x, logos_bottom + li * (line_h + 2) - lb[1]),
                      ln, fill=(200, 200, 200) if not is_top else WHITE, font=small_font)


def _render_text_row(
    canvas: Image.Image,
    item,
    row_y: int, row_h: int,
    is_top: bool,
    rank_str: str,
    fonts: dict,
    _scale: float,
):
    """Plain text row (improved: with wrapping for long text)."""
    draw = ImageDraw.Draw(canvas)

    panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
    canvas.alpha_composite(panel, (PAD, row_y))

    bar_alpha = 255 if is_top else 140
    accent = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
    canvas.alpha_composite(accent, (PAD, row_y))

    draw = ImageDraw.Draw(canvas)

    RANK_W = max(60, int(90 * _scale))

    r_bbox = draw.textbbox((0, 0), rank_str, font=fonts["rank"])
    r_h = r_bbox[3] - r_bbox[1]
    r_x = PAD + 5 + (RANK_W - (r_bbox[2] - r_bbox[0])) // 2
    r_y = row_y + (row_h - r_h) // 2 - r_bbox[1]
    draw.text((r_x, r_y), rank_str, fill=TEAL if is_top else (160, 160, 160), font=fonts["rank"])

    text   = _item_text(item)
    text_x = PAD + RANK_W + 16
    text_maxw = WIDTH - text_x - PAD - 12

    # Try to fit on one line; if not, use smaller font and wrap to 2 lines
    item_font = fonts["name"]
    display = _truncate(draw, text, item_font, text_maxw)

    # Check if truncated significantly → try wrapping with smaller font
    if len(display) < len(text) - 4:
        small_font = fonts["stats"]
        words = text.split()
        lines, line = [], []
        for word in words:
            test = " ".join(line + [word])
            bbox = draw.textbbox((0, 0), test, font=small_font)
            if (bbox[2] - bbox[0]) > text_maxw and line:
                lines.append(" ".join(line))
                line = [word]
            else:
                line.append(word)
        if line:
            lines.append(" ".join(line))
        lines = lines[:2]  # max 2 lines

        line_h = max(16, int(30 * _scale))
        gap    = 6
        block_h = len(lines) * line_h + (len(lines) - 1) * gap
        start_y = row_y + (row_h - block_h) // 2

        for li, ln in enumerate(lines):
            ln_bbox = draw.textbbox((0, 0), ln, font=small_font)
            ln_h    = ln_bbox[3] - ln_bbox[1]
            draw.text((text_x, start_y + li * (line_h + gap) - ln_bbox[1]),
                      ln, fill=WHITE if is_top else (220, 220, 220), font=small_font)
    else:
        i_bbox = draw.textbbox((0, 0), display, font=item_font)
        i_h    = i_bbox[3] - i_bbox[1]
        draw.text((text_x, row_y + (row_h - i_h) // 2 - i_bbox[1]),
                  display, fill=WHITE if is_top else (220, 220, 220), font=item_font)


# ── Main generator ────────────────────────────────────────────────────────────

def generate_debate_card(
    title: str,
    subtitle: str,
    items: list,
    output_path: str = "output/debate_card.png",
    card_format: str = "story",
    bg: str | None = None,
) -> str:
    """
    Render a 5-item debate/list card.

    Args:
        title:       Bold headline (Impact font)
        subtitle:    Teal sub-label
        items:       Exactly 5 items — str (text) or dict (player/team/matchup)
        output_path: Destination PNG path
        card_format: "story" (1080×1920) or "feed" (1080×1080)
        bg:          Background name key from DEBATE_BG_MAP (default: illustrated_court_teal)

    Returns:
        Absolute path to the saved PNG.
    """
    if len(items) != 5:
        raise ValueError(f"Expected exactly 5 items, got {len(items)}")

    # ── Download headshots for player items ──
    player_items = [it for it in items if isinstance(it, dict) and it.get("player_id")]
    if player_items:
        ids  = [it["player_id"] for it in player_items]
        names = {it["player_id"]: it["name"] for it in player_items}
        download_by_ids(ids, names)

    # ── Canvas dimensions ──
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale   = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap  = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h    = _row_area // ROW_COUNT

    # ── Background ──
    bg_key  = bg or "default"
    bg_file = DEBATE_BG_MAP.get(bg_key, bg_key)  # allow raw filename too
    canvas  = _load_background(bg_file, height=canvas_h).convert("RGBA")

    # Dark overlay
    overlay = Image.new("RGBA", (WIDTH, canvas_h), (0, 0, 0, 115))
    canvas.alpha_composite(overlay)

    # Top gradient
    _grad_top = _title_h + 60
    grad = Image.new("RGBA", (WIDTH, _grad_top), (0, 0, 0, 0))
    for y in range(_grad_top):
        alpha = int(200 * (1 - y / _grad_top) + 60)
        ImageDraw.Draw(grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(grad, (0, 0))

    # Bottom gradient
    _grad_h = max(80, canvas_h // 12)
    bot_grad = Image.new("RGBA", (WIDTH, _grad_h), (0, 0, 0, 0))
    for y in range(_grad_h):
        alpha = int(120 * (y / _grad_h))
        ImageDraw.Draw(bot_grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(bot_grad, (0, canvas_h - _grad_h))

    draw = ImageDraw.Draw(canvas)

    # ── Fonts ──
    title_font = _font_impact(max(54, int(88 * _scale)))
    sub_font   = _font(max(18, int(30 * _scale)))

    fonts = {
        "rank":  _font_impact(max(44, int(82 * _scale))),
        "name":  _font(max(28, int(52 * _scale)), bold=True),
        "meta":  _font(max(17, int(30 * _scale))),
        "stats": _font(max(16, int(30 * _scale))),
    }

    # ── Title block ──
    title_text = title.upper()
    sub_text   = subtitle.upper()

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    s_bbox = draw.textbbox((0, 0), sub_text,   font=sub_font)
    t_h    = t_bbox[3] - t_bbox[1]
    s_h    = s_bbox[3] - s_bbox[1]

    # Truncate if title overflows
    max_title_w = WIDTH - PAD * 2 - 22
    if (t_bbox[2] - t_bbox[0]) > max_title_w:
        while (draw.textbbox((0, 0), title_text, font=title_font)[2] -
               draw.textbbox((0, 0), title_text, font=title_font)[0]) > max_title_w and len(title_text) > 2:
            title_text = title_text[:-1].rstrip()
        title_text += "…"
        t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        t_h    = t_bbox[3] - t_bbox[1]

    # Teal accent bar on left of title
    bar_h  = int(_title_h * 0.72)
    bar_y0 = _v_inset + (_title_h - bar_h) // 2
    bar_layer = Image.new("RGBA", (6, bar_h), (*TEAL, 230))
    canvas.alpha_composite(bar_layer, (PAD, bar_y0))

    draw = ImageDraw.Draw(canvas)

    # Vertical centering: use t_bbox[1] offset fix (from design rules)
    _GAP = 12
    visual_h = t_h + _GAP + s_h
    visual_start = _v_inset + max(16, (_title_h - visual_h) // 2)
    title_y = visual_start - t_bbox[1]
    sub_y   = title_y + t_bbox[3] + _GAP

    text_x_start = PAD + 6 + 16
    draw.text((text_x_start, title_y), title_text, fill=WHITE, font=title_font)
    draw.text((text_x_start, sub_y),   sub_text,   fill=(*TEAL, 220), font=sub_font)

    # Teal divider
    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Rows ──
    for i, item in enumerate(items):
        row_y    = _v_inset + _title_h + i * _row_h + _row_gap // 2
        row_h    = _row_h - _row_gap
        is_top   = i == 0
        rank_str = str(i + 1)

        if _is_player_item(item):
            _render_player_row(canvas, item, row_y, row_h, is_top, rank_str, fonts, _scale)
        elif _is_matchup_item(item):
            _render_matchup_row(canvas, item, row_y, row_h, is_top, rank_str, fonts, _scale)
        elif _is_team_item(item):
            _render_team_row(canvas, item, row_y, row_h, is_top, rank_str, fonts, _scale)
        else:
            _render_text_row(canvas, item, row_y, row_h, is_top, rank_str, fonts, _scale)

    # ── Footer ──
    footer_font = _font(max(16, int(28 * _scale)), bold=True)
    footer_text = "rushmore.cards"
    draw = ImageDraw.Draw(canvas)
    f_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    f_w    = f_bbox[2] - f_bbox[0]
    f_h    = f_bbox[3] - f_bbox[1]
    footer_y = canvas_h - _v_inset - _footer_h
    draw.text(((WIDTH - f_w) // 2, footer_y + (_footer_h - f_h) // 2 - f_bbox[1]),
              footer_text, fill=GRAY, font=footer_font)

    # ── Save ──
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out), "PNG", optimize=True)
    print(f"Card saved: {out}")
    return str(out)


# ── CLI ──────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a Rushmore debate/list card.")
    p.add_argument("--title",      required=True)
    p.add_argument("--subtitle",   required=True)
    p.add_argument("--items",      default=None,
                   help="Comma-separated player/team names (text mode)")
    p.add_argument("--items-json", default=None,
                   help="JSON array of item dicts (player/team/matchup mode)")
    p.add_argument("--bg",         default=None,
                   help=f"Background key. Options: {', '.join(DEBATE_BG_MAP)}")
    p.add_argument("--feed",       action="store_true", help="1080x1080 feed format")
    p.add_argument("--output",     default=None)
    return p.parse_args()


def main():
    args   = _parse_args()
    fmt    = "feed" if args.feed else "story"

    if args.items_json:
        items = json.loads(args.items_json)
    elif args.items:
        items = [s.strip() for s in args.items.split(",")]
    else:
        raise ValueError("Provide --items or --items-json")

    output = args.output or f"output/debate_card_{fmt}.png"

    generate_debate_card(
        title=args.title,
        subtitle=args.subtitle,
        items=items,
        output_path=output,
        card_format=fmt,
        bg=args.bg,
    )


if __name__ == "__main__":
    main()
