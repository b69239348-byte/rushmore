"""
MVP Eligibility Card Generator — 65-Game Rule Snapshot.

Renders top MVP candidates with eligibility status per row.
Uses the same design template as generate_mvp_race_card.py.

Usage:
    python3 tools/generate_mvp_eligibility_card.py
    python3 tools/generate_mvp_eligibility_card.py --feed
"""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (  # noqa: E402
    _font, _font_impact,
    _load_background, _load_headshot, _initials_circle, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)
from download_headshots import download_by_ids  # noqa: E402

# Status badge colors
STATUS_COLORS = {
    "eligible":   (0, 220, 120),    # green
    "tonight":    (255, 190, 0),    # yellow/amber
    "ineligible": (220, 60, 60),    # red
    "injured":    (200, 80, 200),   # purple
}

# ── Data: top MVP candidates with eligibility status ──────────────────────────
# Last day of 2025-26 regular season (2026-04-12).
# GP threshold: 65 games. Season games remaining: 1 for most teams.
MVP_CANDIDATES = [
    {
        "id": 1629029,
        "name": "Shai Gilgeous-Alexander",
        "team": "OKC",
        "gp": 68,
        "ppg": 31.1,
        "apg": 6.6,
        "spg": 1.4,
        "status": "eligible",
        "status_label": "ELIGIBLE",
    },
    {
        "id": 203999,
        "name": "Nikola Jokić",
        "team": "DEN",
        "gp": 64,
        "ppg": 27.8,
        "rpg": 12.9,
        "apg": 10.9,
        "status": "tonight",
        "status_label": "Needs 1 tonight",
    },
    {
        "id": 1641705,
        "name": "Victor Wembanyama",
        "team": "SAS",
        "gp": 64,
        "ppg": 25.0,
        "rpg": 11.5,
        "bpg": 3.1,
        "status": "tonight",
        "status_label": "Needs 1 tonight",
    },
    {
        "id": 1628384,
        "name": "Cade Cunningham",
        "team": "DET",
        "gp": 63,
        "ppg": 24.2,
        "apg": 9.8,
        "rpg": 5.5,
        "status": "ineligible",
        "status_label": "INELIGIBLE",
    },
    {
        "id": 1629029,   # placeholder — Luka's real ID
        "id": 1628384,   # overridden below
        "name": "Luka Dončić",
        "team": "LAL",
        "gp": 64,
        "ppg": 33.5,
        "apg": 8.3,
        "rpg": 7.7,
        "status": "injured",
        "status_label": "INJURED — Out",
    },
]

# Fix Luka's player ID (real: 1629029 is SGA; Luka = 1629029... let me use correct IDs)
# SGA: 1629029, Jokić: 203999, Wemby: 1641705, Cade: 1628384, Luka: 1629029
# Luka Dončić real nba_api ID: 1629029
# SGA real nba_api ID: 1628384
# Fix: SGA=1628384, Luka=1629029
MVP_CANDIDATES = [
    {
        "id": 1628983,
        "name": "Shai Gilgeous-Alexander",
        "team": "OKC",
        "gp": 68,
        "stats_line": "31.1 PPG · 6.6 APG · 1.4 SPG",
        "status": "eligible",
        "status_label": "ELIGIBLE",
    },
    {
        "id": 203999,
        "name": "Nikola Jokić",
        "team": "DEN",
        "gp": 64,
        "stats_line": "27.8 PPG · 12.9 RPG · 10.9 APG",
        "status": "tonight",
        "status_label": "Needs 1 tonight",
    },
    {
        "id": 1641705,
        "name": "Victor Wembanyama",
        "team": "SAS",
        "gp": 64,
        "stats_line": "25.0 PPG · 11.5 RPG · 3.1 BPG",
        "status": "tonight",
        "status_label": "Needs 1 tonight",
    },
    {
        "id": 1630595,
        "name": "Cade Cunningham",
        "team": "DET",
        "gp": 63,
        "stats_line": "24.2 PPG · 9.8 APG · 5.5 RPG",
        "status": "ineligible",
        "status_label": "INELIGIBLE",
    },
    {
        "id": 1629029,
        "name": "Luka Dončić",
        "team": "LAL",
        "gp": 64,
        "stats_line": "33.5 PPG · 8.3 APG · 7.7 RPG",
        "status": "injured",
        "status_label": "INJURED — Out",
    },
]


def generate_mvp_eligibility_card(
    output_path: str = "output/2026-04-12/mvp_eligibility_v2_feed.png",
    card_format: str = "story",
):
    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h  = _FORMATS.get(card_format, HEIGHT)
    _scale    = canvas_h / HEIGHT
    _v_inset  = 80 if card_format == "feed" else 0
    _title_h  = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap  = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h    = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)

    players = MVP_CANDIDATES

    # Download missing headshots
    ids   = [p["id"] for p in players]
    names = {p["id"]: p["name"] for p in players}
    download_by_ids(ids, names)

    # ── Canvas ──
    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")

    overlay = Image.new("RGBA", (WIDTH, canvas_h), (0, 0, 0, 120))
    canvas.alpha_composite(overlay)

    _grad_top = _title_h + 60
    grad = Image.new("RGBA", (WIDTH, _grad_top), (0, 0, 0, 0))
    for y in range(_grad_top):
        alpha = int(200 * (1 - y / _grad_top) + 60)
        ImageDraw.Draw(grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(grad, (0, 0))

    _grad_h = max(80, canvas_h // 12)
    bot_grad = Image.new("RGBA", (WIDTH, _grad_h), (0, 0, 0, 0))
    for y in range(_grad_h):
        alpha = int(120 * (y / _grad_h))
        ImageDraw.Draw(bot_grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(bot_grad, (0, canvas_h - _grad_h))

    draw = ImageDraw.Draw(canvas)

    # ── Title ──
    title_font = _font_impact(max(54, int(88 * _scale)))
    sub_font   = _font(max(18, int(28 * _scale)))

    title_text = "SGA by Default?"
    sub_text   = "65-Game Rule · 2025-26 MVP Race"

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    t_w = t_bbox[2] - t_bbox[0]
    t_h = t_bbox[3] - t_bbox[1]
    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    s_w = s_bbox[2] - s_bbox[0]

    block_h = t_h + 12 + (s_bbox[3] - s_bbox[1])
    block_y = _v_inset + (_title_h - block_h) // 2

    draw.text(((WIDTH - t_w) // 2, block_y), title_text, fill=WHITE, font=title_font)
    sub_y = block_y + t_h + 12
    draw.text(((WIDTH - s_w) // 2, sub_y), sub_text, fill=(*TEAL, 220), font=sub_font)

    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Row constants ──
    rank_font   = _font(max(40, int(80 * _scale)), bold=True)
    name_font   = _font(max(24, int(46 * _scale)), bold=True)
    meta_font   = _font(max(14, int(26 * _scale)))
    stats_font  = _font(max(13, int(26 * _scale)))
    status_font = _font(max(13, int(24 * _scale)), bold=True)
    PHOTO_SIZE  = _photo_size
    RANK_W      = max(60, int(100 * _scale))
    LOGO_SIZE   = 160

    for i, player in enumerate(players):
        row_y = _v_inset + _title_h + i * _row_h + _row_gap // 2
        row_h = _row_h - _row_gap
        is_top = i == 0

        # Panel
        panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
        canvas.alpha_composite(panel, (PAD, row_y))

        # Status-colored accent bar
        status_key  = player.get("status", "eligible")
        bar_color   = STATUS_COLORS.get(status_key, TEAL)
        bar_alpha   = 255 if is_top else 180
        bar = Image.new("RGBA", (5, row_h), (*bar_color, bar_alpha))
        canvas.alpha_composite(bar, (PAD, row_y))

        draw = ImageDraw.Draw(canvas)

        # Team logo (right side, big)
        team_abbr = player.get("team", "")
        logo = _load_team_logo([team_abbr] if team_abbr else [], LOGO_SIZE, opacity=0.75)
        logo_x = WIDTH - PAD - LOGO_SIZE - 10
        if logo:
            canvas.alpha_composite(logo, (logo_x, row_y + 6))
            draw = ImageDraw.Draw(canvas)

        # Rank number
        rank_str   = f"0{i + 1}" if i + 1 < 10 else str(i + 1)
        rank_color = WHITE if is_top else (160, 160, 160)
        r_bbox = draw.textbbox((0, 0), rank_str, font=rank_font)
        r_h = r_bbox[3] - r_bbox[1]
        r_x = PAD + 14
        r_y = row_y + (row_h - r_h) // 2
        draw.text((r_x, r_y), rank_str, fill=rank_color, font=rank_font)

        # Headshot
        photo_x = PAD + RANK_W + 16
        photo_y = row_y + (row_h - PHOTO_SIZE) // 2
        headshot = _load_headshot(player["id"], PHOTO_SIZE)
        if headshot is None:
            headshot = _initials_circle(player["name"], PHOTO_SIZE)
        canvas.alpha_composite(headshot, (photo_x, photo_y))

        # Ring around headshot
        ring = Image.new("RGBA", (PHOTO_SIZE + 6, PHOTO_SIZE + 6), (0, 0, 0, 0))
        ring_alpha = 200 if is_top else 100
        ImageDraw.Draw(ring).ellipse(
            (0, 0, PHOTO_SIZE + 5, PHOTO_SIZE + 5),
            outline=(*bar_color, ring_alpha), width=3,
        )
        canvas.alpha_composite(ring, (photo_x - 3, photo_y - 3))

        draw = ImageDraw.Draw(canvas)

        # Text block: Name / Stats / Status
        text_x    = photo_x + PHOTO_SIZE + 24
        text_max_w = logo_x - text_x - 16

        full_name = player["name"].upper()
        name = full_name
        n_bbox = draw.textbbox((0, 0), name, font=name_font)
        if (n_bbox[2] - n_bbox[0]) > text_max_w:
            parts = player["name"].split()
            if len(parts) >= 2:
                name = f"{parts[0][0]}. {' '.join(parts[1:]).upper()}"
                n_bbox = draw.textbbox((0, 0), name, font=name_font)
        while (n_bbox[2] - n_bbox[0]) > text_max_w and len(name) > 4:
            name = name[:-2] + "…"
            n_bbox = draw.textbbox((0, 0), name, font=name_font)

        _name_h   = max(24, int(46 * _scale))
        _meta_h   = max(13, int(26 * _scale))
        _status_h = max(13, int(24 * _scale))
        text_block_h = _name_h + 6 + _meta_h + 6 + _status_h
        text_y = row_y + (row_h - text_block_h) // 2

        # Name
        draw.text((text_x, text_y), name, fill=WHITE, font=name_font)

        # Stats line (gray)
        stats_str = player.get("stats_line", "")
        stats_y = text_y + _name_h + 6
        draw.text((text_x, stats_y), stats_str, fill=GRAY, font=stats_font)

        # Eligibility status (colored)
        gp = player.get("gp", 0)
        status_label = player.get("status_label", "")
        status_str = f"{gp} GP  —  {status_label}"
        status_color = STATUS_COLORS.get(status_key, TEAL)
        status_y = stats_y + _meta_h + 6
        draw.text((text_x, status_y), status_str, fill=(*status_color, 230), font=status_font)

    # ── Footer ──
    footer_font = _font(max(16, int(30 * _scale)), bold=True)
    label = "RUSHMORE"
    icon_h = max(16, int(28 * _scale))
    icon_w = max(20, int(34 * _scale))
    gap = 9

    draw   = ImageDraw.Draw(canvas)
    t_bbox = draw.textbbox((0, 0), label, font=footer_font)
    t_w = t_bbox[2] - t_bbox[0]
    t_h = t_bbox[3] - t_bbox[1]

    total_w = icon_w + gap + t_w
    sx = (WIDTH - total_w) // 2
    iy = canvas_h - _v_inset - _footer_h + (_footer_h - icon_h) // 2

    ix = sx
    small_peak = [
        (ix + icon_w * 0.12, iy + icon_h * 0.40),
        (ix,                  iy + icon_h),
        (ix + icon_w * 0.52,  iy + icon_h),
    ]
    big_peak = [
        (ix + icon_w * 0.65, iy),
        (ix + icon_w * 0.22, iy + icon_h),
        (ix + icon_w,        iy + icon_h),
    ]
    logo_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(logo_layer)
    ld.polygon([(x, y) for x, y in small_peak], fill=(*WHITE, 80))
    ld.polygon([(x, y) for x, y in big_peak],   fill=(*WHITE, 140))
    canvas.alpha_composite(logo_layer)

    draw = ImageDraw.Draw(canvas)
    tx = sx + icon_w + gap
    ty = iy + (icon_h - t_h) // 2 - t_bbox[1]
    draw.text((tx, ty), label, fill=(*WHITE, 150), font=footer_font)

    # ── Save ──
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out), "PNG", optimize=True)
    print(f"Saved: {out}")
    return str(out)


if __name__ == "__main__":
    feed_mode = "--feed" in sys.argv
    fmt = "feed" if feed_mode else "story"

    out_dir = Path(__file__).parent.parent / "output" / "2026-04-12"
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = "_feed" if feed_mode else "_story"
    out_path = str(out_dir / f"mvp_eligibility_v2{suffix}.png")

    generate_mvp_eligibility_card(output_path=out_path, card_format=fmt)
    print("Done.")
