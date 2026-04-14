"""
Generic Award Card Generator — 2025-26 NBA Season.

Generates shareable cards for multiple award types (ROTY, MIP, MVP, DPOY,
Scoring Title, All-NBA, All-Rookie) using a single unified renderer.

Usage:
    python3 tools/generate_award_card.py --award roty
    python3 tools/generate_award_card.py --award all_nba --items "Jokic,SGA,Giannis,Tatum,Luka"
    python3 tools/generate_award_card.py --award mip --feed --output output/test_mip_feed.png
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
import live_data as live_data_module  # noqa: E402
from download_headshots import download_by_ids  # noqa: E402


# ── Award configuration ────────────────────────────────────────────────────
# Each entry: (short_label, full_title, icon_char, stat_key, stat_label, fetch_fn_name)
AWARD_CONFIG: dict[str, tuple] = {
    "roty":       ("ROTY",       "Rookie of the Year",           "★",  "ppg",        "PPG",  "fetch_current_roy_race"),
    "mip":        ("MIP",        "Most Improved Player",         "↑",  "ppg",        "PPG",  "fetch_current_mip_race"),
    "mvp":        ("MVP",        "Most Valuable Player",         "♛",  "eff",        "EFF",  "fetch_current_mvp_race"),
    "dpoy":       ("DPOY",       "Defensive Player of the Year", "⬡",  "dpoy_score", "DEF",  "fetch_current_dpoy_race"),
    "scoring":    ("Scoring",    "Scoring Title",                "⊙",  "ppg",        "PPG",  "fetch_season_leaders"),
    "all_nba":    ("All-NBA",    "All-NBA First Team",           "◈",  None,         None,   None),
    "all_rookie": ("All-Rookie", "All-Rookie First Team",        "◈",  None,         None,   None),
}


def _draw_icon_char(
    draw: ImageDraw.ImageDraw,
    char: str,
    cx: int,
    cy: int,
    size: int,
    color: tuple,
):
    """Draw a Unicode icon character centered at (cx, cy)."""
    font = _font_impact(size)
    bbox = draw.textbbox((0, 0), char, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = cx - w // 2 - bbox[0]
    y = cy - h // 2 - bbox[1]
    draw.text((x, y), char, fill=(*color, 200), font=font)


def generate_award_card(
    award_type: str,
    items: list[str] | None = None,
    auto_data: bool = True,
    output_path: str = "output/award_card.png",
    card_format: str = "story",
) -> str:
    """Generate a shareable award race card.

    Args:
        award_type:  Key from AWARD_CONFIG (e.g. "roty", "mvp", "all_nba").
        items:       Player name strings for manual cards (all_nba, all_rookie)
                     or to override auto data.
        auto_data:   If True and a fetch function exists, pull live data.
        output_path: Where to save the output PNG.
        card_format: "story" (1080×1920) or "feed" (1080×1080).

    Returns:
        Absolute path to the saved PNG.
    """
    if award_type not in AWARD_CONFIG:
        raise ValueError(f"Unknown award type '{award_type}'. Valid: {list(AWARD_CONFIG)}")

    short_label, full_title, icon_char, stat_key, stat_label, fetch_fn_name = AWARD_CONFIG[award_type]

    # ── Resolve player list ────────────────────────────────────────────────
    players: list[dict] = []

    if items:
        # Manual override: items can be strings or dicts {name, team, player_id}
        from generate_card import load_players, _find_player
        db = load_players()
        resolved = []
        for item in items[:5]:
            if isinstance(item, dict):
                # Dict form: explicit player_id takes priority
                pid  = item.get("player_id") or item.get("id") or 0
                name = item.get("name", "")
                team = item.get("team", "")
                resolved.append({"name": name, "id": pid, "team": team, "stats": item.get("stats", "")})
            else:
                name = str(item).strip()
                p = _find_player(db, name)
                if p:
                    resolved.append({"name": p["name"], "id": p["id"], "team": p.get("team", "")})
                else:
                    resolved.append({"name": name, "id": 0, "team": ""})
        players = resolved
        auto_data = False

    if auto_data and fetch_fn_name:
        fetch_fn = getattr(live_data_module, fetch_fn_name, None)
        if fetch_fn is None:
            print(f"Warning: fetch function '{fetch_fn_name}' not found in live_data. Falling back to empty list.")
        else:
            players = fetch_fn(limit=5)

    if not players:
        print(f"No player data for '{award_type}'. Provide --items or check live_data connection.")
        return ""

    # ── Download headshots for real player IDs ──────────────────────────
    real_ids = [p["id"] for p in players if p.get("id", 0) != 0]
    if real_ids:
        names = {p["id"]: p["name"] for p in players if p.get("id", 0) != 0}
        download_by_ids(real_ids, names)

    # ── Canvas dimensions ─────────────────────────────────────────────────
    _FORMATS = {"story": HEIGHT, "feed": 1080}
    canvas_h   = _FORMATS.get(card_format, HEIGHT)
    _scale     = canvas_h / HEIGHT
    _v_inset   = 80 if card_format == "feed" else 0
    _title_h   = int(TITLE_H * _scale)
    _footer_h  = int(FOOTER_H * _scale)
    _row_gap   = max(4, int(ROW_GAP * _scale))
    _row_area  = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h     = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)

    # ── Canvas ────────────────────────────────────────────────────────────
    _BG_MAP = {
        "roty":       "trophy_spotlight",
        "mip":        "trophy_celebration",
        "mvp":        "trophy_jordan",
        "dpoy":       "indoor_arena",
        "scoring":    "indoor_arena",
        "all_nba":    "golden_arena",
        "all_rookie": "trophy_celebration",
    }
    bg_name = _BG_MAP.get(award_type, "underground_court")
    canvas = _load_background(bg_name, height=canvas_h).convert("RGBA")

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

    # ── Title ─────────────────────────────────────────────────────────────
    title_font = _font_impact(max(54, int(96 * _scale)))
    sub_font   = _font(max(18, int(30 * _scale)))

    # Static award types (all_nba, all_rookie) don't have a "race" — use full title
    _STATIC_AWARDS = {"all_nba", "all_rookie"}
    if award_type in _STATIC_AWARDS:
        title_text = full_title.upper()
        sub_text   = "2025-26 NBA SEASON"
    else:
        title_text = f"{short_label} RACE"
        sub_text   = f"2025-26  ·  {full_title.upper()}"

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    t_w = t_bbox[2] - t_bbox[0]
    s_w = s_bbox[2] - s_bbox[0]

    # Visual height of the block: from visual top of title to visual bottom of subtitle.
    # t_bbox[1] is a positive offset (Impact font renders below the draw point).
    # So visual extent = t_bbox[3] (title bottom from draw point) + gap + s_bbox[3].
    _GAP_TITLE_SUB = 14
    visual_h = t_bbox[3] + _GAP_TITLE_SUB + s_bbox[3]

    # Align visual top of the block to the center of the title area.
    # visual top of title = title_y + t_bbox[1], so:
    visual_start = _v_inset + max(16, (_title_h - visual_h) // 2)
    title_y = visual_start - t_bbox[1]
    sub_y   = title_y + t_bbox[3] + _GAP_TITLE_SUB

    draw.text(((WIDTH - t_w) // 2, title_y), title_text, fill=WHITE, font=title_font)
    draw.text(((WIDTH - s_w) // 2, sub_y),   sub_text,   fill=(*TEAL, 220), font=sub_font)

    # Divider
    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Player rows ───────────────────────────────────────────────────────
    rank_font  = _font(max(40, int(80 * _scale)), bold=True)
    name_font  = _font(max(24, int(46 * _scale)), bold=True)
    meta_font  = _font(max(14, int(28 * _scale)))
    stats_font = _font(max(14, int(30 * _scale)))
    PHOTO_SIZE = _photo_size
    RANK_W     = max(60, int(100 * _scale))

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
        _logo_size = int(row_h * 0.55)
        logo = _load_team_logo(logo_candidates, _logo_size, opacity=0.55)
        logo_x = WIDTH - PAD - _logo_size - 16
        if logo:
            logo_y = row_y + (row_h - _logo_size) // 2
            canvas.alpha_composite(logo, (logo_x, logo_y))
            draw = ImageDraw.Draw(canvas)

        # Rank number
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
        player_id = player.get("id", 0)
        headshot = None
        if player_id != 0:
            headshot = _load_headshot(player_id, PHOTO_SIZE)
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

        # Text block layout
        text_x     = photo_x + PHOTO_SIZE + 24
        text_max_w = logo_x - text_x - 12

        # Name (truncate to fit) — try full → last-name-only → abbreviated → truncated
        full_name = player["name"].upper()
        name = full_name
        n_bbox = draw.textbbox((0, 0), name, font=name_font)
        if (n_bbox[2] - n_bbox[0]) > text_max_w:
            parts = player["name"].split()
            if len(parts) >= 2:
                # Try last name(s) only, e.g. "GILGEOUS-ALEXANDER" or "WEMBANYAMA"
                last_only = " ".join(parts[1:]).upper()
                lb = draw.textbbox((0, 0), last_only, font=name_font)
                if (lb[2] - lb[0]) <= text_max_w:
                    name = last_only
                    n_bbox = lb
                else:
                    # Fall back to first initial + last name
                    name = f"{parts[0][0]}. {last_only}"
                    n_bbox = draw.textbbox((0, 0), name, font=name_font)
        while (n_bbox[2] - n_bbox[0]) > text_max_w and len(name) > 4:
            name = name[:-2] + "…"
            n_bbox = draw.textbbox((0, 0), name, font=name_font)

        _name_h  = max(24, int(50 * _scale))
        _meta_h  = max(14, int(28 * _scale))
        _stats_h = max(14, int(32 * _scale))

        # Decide if we'll show a stat line
        # Priority: explicit 'stats' string in player dict (for manual cards like all_nba)
        # Fallback: computed from stat_key (for live-data cards)
        manual_stats = player.get("stats", "")
        show_stat = bool(manual_stats) or (
            stat_key is not None
            and stat_label is not None
            and stat_key in player
        )

        text_block_h = _name_h + 8 + _meta_h
        if show_stat:
            text_block_h += 8 + _stats_h

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

        # Stat line
        if show_stat:
            if manual_stats:
                stats_str = manual_stats
            else:
                stat_val = player[stat_key]
                if award_type == "dpoy":
                    bpg  = player.get("bpg", 0)
                    spg  = player.get("spg", 0)
                    drtg = player.get("drtg", 0)
                    stats_str = f"{bpg} BLK  ·  {spg} STL  ·  {drtg} DRTG"
                elif award_type == "mip":
                    delta = player.get("_improvement", "")
                    delta_str = f"+{delta}" if delta else ""
                    stats_str = f"{stat_val} {stat_label}  ·  {delta_str} vs last season" if delta_str else f"{stat_val} {stat_label}"
                elif award_type == "roty":
                    rpg = player.get("rpg", "")
                    apg = player.get("apg", "")
                    extras = []
                    if rpg:
                        extras.append(f"{rpg} RPG")
                    if apg:
                        extras.append(f"{apg} APG")
                    stats_str = f"{stat_val} PPG  ·  " + "  ·  ".join(extras) if extras else f"{stat_val} PPG"
                elif award_type in ("mvp", "scoring"):
                    rpg = player.get("rpg", "")
                    apg = player.get("apg", "")
                    extras = []
                    if rpg:
                        extras.append(f"{rpg} RPG")
                    if apg:
                        extras.append(f"{apg} APG")
                    stats_str = f"{stat_val} {stat_label}  ·  " + "  ·  ".join(extras) if extras else f"{stat_val} {stat_label}"
                else:
                    stats_str = f"{stat_val} {stat_label}"
            stats_y = meta_y + _meta_h + 8
            draw.text((text_x, stats_y), stats_str, fill=(*TEAL, 220), font=stats_font)

    # ── Footer ────────────────────────────────────────────────────────────
    footer_font = _font(max(16, int(30 * _scale)), bold=True)
    label   = "RUSHMORE"
    icon_h  = max(16, int(28 * _scale))
    icon_w  = max(20, int(34 * _scale))
    gap     = 9

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

    # ── Save ──────────────────────────────────────────────────────────────
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out), "PNG", optimize=True)
    print(f"Card saved: {out}")
    return str(out)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generic NBA Award Card Generator")
    parser.add_argument("--award",  required=True, choices=list(AWARD_CONFIG), help="Award type")
    parser.add_argument("--items",  default=None,  help="Comma-separated player names (manual mode)")
    parser.add_argument("--feed",   action="store_true", help="Generate feed format (1080x1080) instead of story")
    parser.add_argument("--output", default=None,  help="Output file path (default: output/<award>_<format>.png)")
    args = parser.parse_args()

    fmt = "feed" if args.feed else "story"

    if args.output:
        out_path = args.output
    else:
        out_path = f"output/{args.award}_card_{fmt}.png"

    item_list: list[str] | None = None
    if args.items:
        item_list = [s.strip() for s in args.items.split(",")]

    use_auto = item_list is None  # auto unless manual items provided

    print(f"Generating {args.award.upper()} card ({fmt})...")
    result = generate_award_card(
        award_type=args.award,
        items=item_list,
        auto_data=use_auto,
        output_path=out_path,
        card_format=fmt,
    )
    if result:
        print(f"Done → {result}")
    else:
        sys.exit(1)
