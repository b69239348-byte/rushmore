"""
DPOY Race Card Generator — 2025-26 NBA Season.

Fetches top 5 DPOY candidates via composite defensive metric
(BLK/G × 2.0 + STL/G × 1.5 − (DRTG − 105) × 0.3) and renders
a shareable card with defensive stats.

Usage:
    python3 tools/generate_dpoy_card.py
    python3 tools/generate_dpoy_card.py --feed   # Instagram feed (1080x1080)
"""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

# Reuse all helpers from the main card generator
from generate_card import (  # noqa: E402
    _font, _font_impact,
    _load_background, _load_headshot, _initials_circle, _load_team_logo,
    _ABBR_ALIASES,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)
from live_data import fetch_current_dpoy_race  # noqa: E402
from download_headshots import download_by_ids  # noqa: E402


def _shield_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple):
    """Draw a simple shield outline as the DPOY motif."""
    w = size
    h = int(size * 1.2)
    x0 = cx - w // 2
    y0 = cy - h // 2
    # Shield: rounded-top rectangle that tapers to a point at bottom
    pts = [
        (x0,          y0 + h * 0.25),   # left mid
        (x0,          y0 + h * 0.05),   # left shoulder
        (cx,          y0),              # top center
        (x0 + w,      y0 + h * 0.05),   # right shoulder
        (x0 + w,      y0 + h * 0.25),   # right mid
        (x0 + w,      y0 + h * 0.65),   # right lower
        (cx,          y0 + h),          # bottom tip
        (x0,          y0 + h * 0.65),   # left lower
    ]
    draw.polygon(pts, fill=(*color, 30), outline=(*color, 180), width=2)


def generate_dpoy_card(
    output_path: str = "output/dpoy2026/card.png",
    card_format: str = "story",
):
    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale   = canvas_h / HEIGHT
    _v_inset = 80 if card_format == "feed" else 0
    _title_h = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap  = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h    = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)

    # Fetch top 5 DPOY candidates
    players = fetch_current_dpoy_race(limit=5)
    if not players:
        print("No DPOY data returned — check nba_api connection.")
        return

    # Download any missing headshots
    ids = [p["id"] for p in players]
    names = {p["id"]: p["name"] for p in players}
    download_by_ids(ids, names)

    # ── Canvas ──
    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")

    # Dark overlay for readability
    overlay = Image.new("RGBA", (WIDTH, canvas_h), (0, 0, 0, 120))
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

    # ── Title: shield icon + "DPOY RACE" ──
    shield_size = max(28, int(44 * _scale))
    title_font  = _font_impact(max(54, int(96 * _scale)))
    sub_font    = _font(max(18, int(30 * _scale)))

    title_text = "DPOY RACE"
    sub_text   = "2025-26 · DEFENSIVE PLAYER OF THE YEAR"

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    t_w    = t_bbox[2] - t_bbox[0]
    t_h    = t_bbox[3] - t_bbox[1]

    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    s_w    = s_bbox[2] - s_bbox[0]

    # Vertical centering in title area
    block_h = shield_size + 8 + t_h + 12 + (s_bbox[3] - s_bbox[1])
    block_y = _v_inset + (_title_h - block_h) // 2

    # Shield icon centered above title
    shield_cx = WIDTH // 2
    shield_cy = block_y + shield_size // 2
    _shield_icon(draw, shield_cx, shield_cy, shield_size, TEAL)

    title_y = block_y + shield_size + 8
    draw.text(((WIDTH - t_w) // 2, title_y), title_text, fill=WHITE, font=title_font)

    sub_y = title_y + t_h + 12
    draw.text(((WIDTH - s_w) // 2, sub_y), sub_text, fill=(*TEAL, 220), font=sub_font)

    # Divider
    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Player rows ──
    rank_font  = _font(max(40, int(80 * _scale)), bold=True)
    name_font  = _font(max(24, int(46 * _scale)), bold=True)
    meta_font  = _font(max(14, int(28 * _scale)))
    stats_font = _font(max(14, int(30 * _scale)))
    PHOTO_SIZE = _photo_size
    RANK_W     = max(60, int(100 * _scale))
    LOGO_SIZE  = 160

    for i, player in enumerate(players):
        row_y = _v_inset + _title_h + i * _row_h + _row_gap // 2
        row_h = _row_h - _row_gap
        is_top = i == 0

        # Panel
        panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
        canvas.alpha_composite(panel, (PAD, row_y))

        # Accent bar
        bar_alpha = 255 if is_top else 140
        bar = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
        canvas.alpha_composite(bar, (PAD, row_y))

        draw = ImageDraw.Draw(canvas)

        # Team logo
        team_abbr = player.get("team", "")
        logo_candidates = [team_abbr] if team_abbr else []
        logo = _load_team_logo(logo_candidates, LOGO_SIZE, opacity=0.75)
        logo_x = WIDTH - PAD - LOGO_SIZE - 10
        if logo:
            canvas.alpha_composite(logo, (logo_x, row_y + 6))
            draw = ImageDraw.Draw(canvas)

        # Rank
        rank_str   = f"0{i + 1}" if i + 1 < 10 else str(i + 1)
        rank_color = WHITE if is_top else (160, 160, 160)
        r_bbox = draw.textbbox((0, 0), rank_str, font=rank_font)
        r_h    = r_bbox[3] - r_bbox[1]
        r_x    = PAD + 14
        r_y    = row_y + (row_h - r_h) // 2
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
            outline=(*TEAL, ring_alpha), width=3,
        )
        canvas.alpha_composite(ring, (photo_x - 3, photo_y - 3))

        draw = ImageDraw.Draw(canvas)

        # Text block
        text_x     = photo_x + PHOTO_SIZE + 24
        text_max_w = logo_x - text_x - 16

        # Use last name only if full name doesn't fit
        full_name = player["name"].upper()
        name = full_name
        n_bbox = draw.textbbox((0, 0), name, font=name_font)
        if (n_bbox[2] - n_bbox[0]) > text_max_w:
            parts = player["name"].split()
            # Try "F. LASTNAME" format first
            if len(parts) >= 2:
                name = f"{parts[0][0]}. {' '.join(parts[1:]).upper()}"
                n_bbox = draw.textbbox((0, 0), name, font=name_font)
        while (n_bbox[2] - n_bbox[0]) > text_max_w and len(name) > 4:
            name = name[:-2] + "…"
            n_bbox = draw.textbbox((0, 0), name, font=name_font)

        _name_h  = max(24, int(50 * _scale))
        _meta_h  = max(14, int(28 * _scale))
        _stats_h = max(14, int(32 * _scale))
        text_block_h = _name_h + 8 + _meta_h + 8 + _stats_h
        text_y = row_y + (row_h - text_block_h) // 2

        draw.text((text_x, text_y), name, fill=WHITE, font=name_font)

        # Meta: position · team
        meta_parts = []
        pos = player.get("position") or ""
        if pos:
            meta_parts.append(pos)
        t = _ABBR_ALIASES.get(team_abbr.upper(), team_abbr.upper()) if team_abbr else ""
        if t:
            meta_parts.append(t)
        meta = "  ·  ".join(meta_parts) if meta_parts else team_abbr
        meta_y = text_y + _name_h + 8
        draw.text((text_x, meta_y), meta, fill=GRAY, font=meta_font)

        # Defensive stats line: BLK · STL · DRTG
        bpg  = player.get("bpg", 0)
        spg  = player.get("spg", 0)
        drtg = player.get("drtg", 0)
        stats_str = f"{bpg} BLK  ·  {spg} STL  ·  {drtg} DRTG"
        stats_y = meta_y + _meta_h + 8
        draw.text((text_x, stats_y), stats_str, fill=(*TEAL, 220), font=stats_font)

    # ── Footer ──
    footer_font = _font(max(16, int(30 * _scale)), bold=True)
    label = "RUSHMORE"
    icon_h = max(16, int(28 * _scale))
    icon_w = max(20, int(34 * _scale))
    gap = 9

    draw   = ImageDraw.Draw(canvas)
    t_bbox = draw.textbbox((0, 0), label, font=footer_font)
    t_w    = t_bbox[2] - t_bbox[0]
    t_h    = t_bbox[3] - t_bbox[1]

    total_w = icon_w + gap + t_w
    sx      = (WIDTH - total_w) // 2
    iy      = canvas_h - _v_inset - _footer_h + (_footer_h - icon_h) // 2

    # Mountain icon
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
    print(f"Card saved: {out}")
    return str(out)


def build_captions(players: list[dict], out_dir: Path):
    """Write platform-specific caption files."""
    top = players[0] if players else {}
    top_name = top.get("name", "Wemby").split()[-1]

    # Compact stat line for top 3
    def stat_line(p):
        return f"{p['name']}  {p['bpg']} BLK · {p['spg']} STL · {p['drtg']} DRTG"

    top3_lines = "\n".join(f"{i+1}. {stat_line(p)}" for i, p in enumerate(players[:3]))

    # ── X (Quote-Tweet der Bleacher Report Post) ──
    x_caption = (
        f"Wemby wouldn't even be surprised 😂\n\n"
        f"The numbers back it up.\n\n"
        f"{top3_lines}\n\n"
        f"Build your Mt. Rushmore 👉 rushmore.cards\n\n"
        f"#NBA #DPOY #Wembanyama"
    )

    # ── Instagram ──
    insta_caption = (
        f"DPOY isn't even a debate anymore 🔒\n\n"
        f"The defensive numbers for 2025-26:\n\n"
        f"{top3_lines}\n\n"
        f"Who's your DPOY? Drop it below 👇\n\n"
        f"Build your own Mt. Rushmore at rushmore.cards\n\n"
        f"#NBA #DPOY #Wembanyama #Basketball #Defense #NBAStats #SanAntonioSpurs"
    )

    # ── TikTok ──
    tiktok_caption = (
        f"The DPOY race by the numbers 🛡️ "
        f"#NBA #DPOY #Wembanyama #NBAStats #Basketball #Defense"
    )

    (out_dir / "caption_x.txt").write_text(x_caption, encoding="utf-8")
    (out_dir / "caption_instagram.txt").write_text(insta_caption, encoding="utf-8")
    (out_dir / "caption_tiktok.txt").write_text(tiktok_caption, encoding="utf-8")
    print(f"Captions saved to {out_dir}")


if __name__ == "__main__":
    feed_mode = "--feed" in sys.argv
    fmt = "feed" if feed_mode else "story"

    out_dir = Path(__file__).parent.parent / "output" / "dpoy2026"
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = "_feed" if feed_mode else "_story"
    card_path = out_dir / f"dpoy_card{suffix}.png"

    print("Fetching DPOY race data...")
    players = fetch_current_dpoy_race(limit=5)
    if not players:
        print("No data — check connection.")
        sys.exit(1)

    print(f"\nTop 5 DPOY candidates (composite score):")
    for i, p in enumerate(players, 1):
        print(f"  {i}. {p['name']:25s} {p['team']:4s}  BLK {p['bpg']}  STL {p['spg']}  DRTG {p['drtg']}  score {p['_def_score']}")

    generate_dpoy_card(output_path=str(card_path), card_format=fmt)
    build_captions(players, out_dir)

    print(f"\nDone — output/dpoy2026/")
