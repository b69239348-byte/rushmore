"""
Rushmore — Card Generator v4
Layout: AI-generated background, semi-transparent player rows,
teal accent numbers, circular headshots, team logos in rows.
"""

import json
import sys
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- Constants ---
WIDTH, HEIGHT = 1080, 1920
PAD = 48

TEAL        = (76, 201, 240)
WHITE       = (255, 255, 255)
WHITE_70    = (255, 255, 255, 178)
GRAY        = (180, 180, 180)      # neutral gray, no blue tint
MUTED       = (140, 140, 140)
ROW_BG      = (10, 10, 12, 215)   # near-black, neutral
ROW_BG_1    = (20, 20, 24, 225)   # rank-1 row: slightly lighter

# Backgrounds that need light treatment (white overlay + dark text in title area)
LIGHT_BACKGROUNDS = {"sunny_outdoor", "morning_fog"}

DARK_NAVY   = (8, 16, 32)
DARK_GRAY   = (40, 50, 70)

HEADSHOT_DIR  = Path(__file__).parent.parent / "assets" / "headshots"
LOGO_DIR      = Path(__file__).parent.parent / "assets" / "team_logos"
BG_DIR        = Path(__file__).parent.parent / "assets" / "card_backgrounds"
USER_BG_DIR   = Path(__file__).parent.parent / "assets" / "design-inspiration "
DB_PATH       = Path(__file__).parent.parent / "players.json"

TITLE_H   = 210
FOOTER_H  = 80
ROW_COUNT = 5
ROW_AREA  = HEIGHT - TITLE_H - FOOTER_H
ROW_H     = ROW_AREA // ROW_COUNT
ROW_GAP   = 10
ROW_R     = 18   # corner radius for row panels


def load_players():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _find_player(db, query: str):
    if str(query).isdigit():
        pid = int(query)
        return next((p for p in db if p["id"] == pid), None)
    q = str(query).lower()
    return next((p for p in db if q in p["name"].lower()), None)


# ── Fonts ─────────────────────────────────────────────────────────────────────

def _font(size: int, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _font_impact(size: int):
    """Impact or DIN Condensed Bold — for card titles."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return _font(size, bold=True)


# ── Image helpers ──────────────────────────────────────────────────────────────

def _load_background(name: str) -> Image.Image:
    """Load and resize background to card dimensions."""
    # Try card_backgrounds first, then user uploads
    candidates = [
        BG_DIR / f"{name}.png",
        BG_DIR / f"{name}",
        USER_BG_DIR / f"{name}.png",
        USER_BG_DIR / f"{name}",
    ]
    for path in candidates:
        if path.exists():
            img = Image.open(path).convert("RGB")
            # Fill 1080x1920 preserving aspect ratio
            img_ratio = img.width / img.height
            card_ratio = WIDTH / HEIGHT
            if img_ratio > card_ratio:
                new_h = HEIGHT
                new_w = int(HEIGHT * img_ratio)
            else:
                new_w = WIDTH
                new_h = int(WIDTH / img_ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - WIDTH) // 2
            top  = (new_h - HEIGHT) // 2
            return img.crop((left, top, left + WIDTH, top + HEIGHT))
    # Fallback: dark gradient
    fallback = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 24))
    draw = ImageDraw.Draw(fallback)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(8  + t * 4)
        g = int(12 + t * 4)
        b = int(24 + t * 8)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return fallback


def _load_headshot(player_id: int, size: int) -> Optional[Image.Image]:
    for ext in ("jpg", "jpeg", "png"):
        path = HEADSHOT_DIR / f"{player_id}.{ext}"
        if path.exists():
            img = Image.open(path).convert("RGBA")
            w, h = img.width, img.height
            # Step 1: center-crop to square (NBA headshots are landscape 1040×760)
            if w > h:
                left = (w - h) // 2
                img = img.crop((left, 0, left + h, h))
            elif h > w:
                top = (h - w) // 2
                img = img.crop((0, top, w, top + w))
            # Step 2: crop top 80% to focus on face (remove lower body)
            sq = img.width
            face_h = int(sq * 0.80)
            img = img.crop((0, 0, sq, face_h))
            # Step 3: pad back to square with transparent bottom
            square = Image.new("RGBA", (sq, sq), (0, 0, 0, 0))
            square.paste(img, (0, 0))
            img = square
            # Step 4: resize to target size
            img = img.resize((size, size), Image.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
            result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            result.paste(img, mask=mask)
            return result
    return None


def _initials_circle(name: str, size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, size - 1, size - 1), fill=(*TEAL, 180))
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    font = _font(size // 3, bold=True)
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) // 2, (size - th) // 2), initials, fill=WHITE, font=font)
    return img


# Historical abbreviations → current franchise
_ABBR_ALIASES = {
    "UTH": "UTA", "SAN": "SAS", "NJN": "BKN", "NJD": "BKN",
    "NOH": "NOP", "NOK": "NOP", "NOJ": "NOP",
    "PHW": "GSW", "SFW": "GSW", "GOS": "GSW",
    "VAN": "MEM", "SDC": "LAC", "SDR": "LAC",
    "SEA": "OKC", "KCK": "SAC",
    "CHH": "CHA", "CHO": "CHA",
    "CAP": "WAS", "BLT": "WAS",
    "STL": "ATL", "MIH": "LAL", "MNL": "LAL",
    "SYR": "PHI", "PHL": "PHI",
    "NYN": "BKN", "ROC": "SAC", "CIN": "SAC",
    "BUF": "LAC",
}


def _load_team_logo(team_abbr_or_list, size: int, opacity: float = 0.45) -> Optional[Image.Image]:
    """Load team logo — accepts single abbr or list, picks first match."""
    candidates = team_abbr_or_list if isinstance(team_abbr_or_list, list) else [team_abbr_or_list]
    for abbr in candidates:
        if not abbr:
            continue
        resolved = _ABBR_ALIASES.get(abbr.upper(), abbr.upper())
        path = LOGO_DIR / f"{resolved}.png"
        if path.exists():
            img = Image.open(path).convert("RGBA")
            # Pad to square so non-square logos (e.g. UTA) don't distort
            if img.width != img.height:
                max_dim = max(img.width, img.height)
                square = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
                square.paste(img, ((max_dim - img.width) // 2, (max_dim - img.height) // 2))
                img = square
            img = img.resize((size, size), Image.LANCZOS)
            r, g, b, a = img.split()
            a = a.point(lambda x: int(x * opacity))
            return Image.merge("RGBA", (r, g, b, a))
    return None


def _rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_card(
    queries,
    title="MY TOP 5",
    subtitle="ALL-TIME GREATS",
    output_path="card.png",
    background="night_court_outdoor",
    extra_players=None,
    game_stats=None,          # {player_id: {pts, reb, ast, stl, blk}}; overrides season averages
):
    db = load_players()
    if extra_players:
        existing_ids = {p["id"] for p in db}
        db = db + [p for p in extra_players if p["id"] not in existing_ids]

    # Build live-player lookup for current-team override
    live_by_id = {p["id"]: p for p in (extra_players or []) if p.get("team")}

    players = []
    for q in queries[:5]:
        p = _find_player(db, str(q))
        if p:
            # Active players: use current team from live data
            if p["id"] in live_by_id:
                p = dict(p)
                p["current_team"] = live_by_id[p["id"]]["team"]
            players.append(p)

    # ── Canvas: background image ──
    canvas = _load_background(background).convert("RGBA")
    is_light = background in LIGHT_BACKGROUNDS

    # ── Top gradient overlay ──
    grad = Image.new("RGBA", (WIDTH, TITLE_H + 40), (0, 0, 0, 0))
    if is_light:
        # White overlay for light backgrounds — keeps brightness, dark text on top
        for y in range(TITLE_H + 40):
            alpha = int(200 * (1 - y / (TITLE_H + 40)) + 40)
            ImageDraw.Draw(grad).line([(0, y), (WIDTH, y)], fill=(255, 255, 255, alpha))
    else:
        for y in range(TITLE_H + 40):
            alpha = int(180 * (1 - y / (TITLE_H + 40)) + 60)
            ImageDraw.Draw(grad).line([(0, y), (WIDTH, y)], fill=(4, 8, 18, alpha))
    canvas.alpha_composite(grad, (0, 0))

    # ── Bottom gradient (ground area) ──
    bot_grad = Image.new("RGBA", (WIDTH, 160), (0, 0, 0, 0))
    fill_color = (255, 255, 255, 0) if is_light else (4, 8, 18, 0)
    for y in range(160):
        alpha = int(100 * (y / 160))
        r, g, b, _ = (*fill_color[:3], 0)
        ImageDraw.Draw(bot_grad).line([(0, y), (WIDTH, y)], fill=(r, g, b, alpha))
    canvas.alpha_composite(bot_grad, (0, HEIGHT - 160))

    draw = ImageDraw.Draw(canvas)

    # ── Accent color: white on dark panels, dark navy on light backgrounds ──
    accent     = DARK_NAVY if is_light else WHITE
    accent_dim = DARK_GRAY  if is_light else (160, 160, 160)
    accent_alpha = (*DARK_NAVY, 60) if is_light else (*TEAL, 80)

    # ── Title ──
    title_font = _font_impact(96)
    sub_font   = _font(36)

    title_color    = DARK_NAVY if is_light else WHITE
    subtitle_color = DARK_GRAY if is_light else (200, 200, 200)
    divider_color  = (*DARK_NAVY, 60) if is_light else (*accent, 80)

    t_up = title.upper()
    t_bbox = draw.textbbox((0, 0), t_up, font=title_font)
    t_w = t_bbox[2] - t_bbox[0]
    draw.text(((WIDTH - t_w) // 2, 44), t_up, fill=title_color, font=title_font)

    s_up = subtitle.upper()
    s_bbox = draw.textbbox((0, 0), s_up, font=sub_font)
    s_w = s_bbox[2] - s_bbox[0]
    draw.text(((WIDTH - s_w) // 2, 44 + 102), s_up, fill=subtitle_color, font=sub_font)

    # ── Thin divider under title ──
    div_y = TITLE_H - 10
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=divider_color)

    # ── Player rows ──
    rank_font  = _font(80, bold=True)
    name_font  = _font(46, bold=True)
    meta_font  = _font(28)
    stats_font = _font(30)

    PHOTO_SIZE = int(ROW_H * 0.70)
    RANK_W     = 100

    for i, player in enumerate(players):
        row_y  = TITLE_H + i * ROW_H + ROW_GAP // 2
        row_h  = ROW_H - ROW_GAP
        is_top = i == 0

        # Panel background
        panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
        canvas.alpha_composite(panel, (PAD, row_y))

        # Accent bar — full opacity for rank 1, slightly dimmer for others
        bar_alpha = 255 if is_top else 140
        bar = Image.new("RGBA", (5, row_h), (*accent, bar_alpha))
        canvas.alpha_composite(bar, (PAD, row_y))

        draw = ImageDraw.Draw(canvas)

        # Team logo — prefer current_team (active) over main_team (historical)
        team_for_logo = player.get("current_team") or player.get("main_team")
        team_candidates = [team_for_logo] if team_for_logo else (player.get("teams") or ([player["team"]] if player.get("team") else []))
        LOGO_SIZE = 160
        logo = _load_team_logo(team_candidates, LOGO_SIZE, opacity=0.75)
        logo_x = WIDTH - PAD - LOGO_SIZE - 10
        if logo:
            canvas.alpha_composite(logo, (logo_x, row_y + 6))
            draw = ImageDraw.Draw(canvas)

        # Rank number
        rank_str = f"0{i + 1}" if i + 1 < 10 else str(i + 1)
        rank_color = accent if is_top else accent_dim
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
        draw = ImageDraw.Draw(canvas)

        # Ring around headshot — brighter for rank 1
        ring = Image.new("RGBA", (PHOTO_SIZE + 6, PHOTO_SIZE + 6), (0, 0, 0, 0))
        ring_alpha = 200 if is_top else 100
        ImageDraw.Draw(ring).ellipse((0, 0, PHOTO_SIZE + 5, PHOTO_SIZE + 5),
                                     outline=(*accent, ring_alpha), width=3)
        canvas.alpha_composite(ring, (photo_x - 3, photo_y - 3))
        draw = ImageDraw.Draw(canvas)

        # Text block
        text_x = photo_x + PHOTO_SIZE + 24
        text_max_w = logo_x - text_x - 16

        # Name (truncate if too long)
        name = player["name"].upper()
        n_bbox = draw.textbbox((0, 0), name, font=name_font)
        while (n_bbox[2] - n_bbox[0]) > text_max_w and len(name) > 4:
            name = name[:-2] + "…"
            n_bbox = draw.textbbox((0, 0), name, font=name_font)

        text_block_h = 50 + 8 + 28 + 8 + 32  # name + gap + meta + gap + stats
        text_y = row_y + (row_h - text_block_h) // 2

        name_color = WHITE if not is_top else WHITE
        draw.text((text_x, text_y), name, fill=name_color, font=name_font)

        # Meta (position + main team)
        meta_parts = []
        if player.get("position"):
            meta_parts.append(player["position"])
        team_abbr = player.get("main_team") or player.get("team") or (player.get("teams") or [None])[0]
        if team_abbr:
            meta_parts.append(_ABBR_ALIASES.get(team_abbr.upper(), team_abbr.upper()))
        meta = "  ·  ".join(meta_parts) if meta_parts else ""
        meta_y = text_y + 50 + 8
        draw.text((text_x, meta_y), meta, fill=GRAY, font=meta_font)

        # Stats line — game stats override season averages
        if game_stats and player["id"] in game_stats:
            gs = game_stats[player["id"]]
            pts = gs.get("pts", 0)
            reb = gs.get("reb", 0)
            ast = gs.get("ast", 0)
            stl = gs.get("stl", 0)
            blk = gs.get("blk", 0)
            stats = f"{pts} PTS  ·  {reb} REB  ·  {ast} AST  ·  {stl} STL  ·  {blk} BLK"
        else:
            ppg = player.get("ppg", 0)
            rpg = player.get("rpg", 0)
            apg = player.get("apg", 0) or 0
            spg = player.get("spg", 0) or 0
            bpg = player.get("bpg", 0) or 0
            third_candidates = [
                (apg, "APG", apg / 10),
                (spg, "SPG", spg / 2.0),
                (bpg, "BPG", bpg / 3.5),
            ]
            third_val, third_label, _ = max(
                (c for c in third_candidates if c[0] > 0),
                key=lambda c: c[2],
                default=(apg, "APG", 0),
            )
            stats = f"{ppg} PPG  ·  {rpg} RPG  ·  {third_val} {third_label}"
        stats_y = meta_y + 28 + 8
        draw.text((text_x, stats_y), stats, fill=GRAY, font=stats_font)

    # ── Footer: mountain icon + RUSHMORE text ──
    footer_font = _font(30, bold=True)
    label      = "RUSHMORE"
    icon_h, icon_w = 28, 34
    gap        = 9

    draw       = ImageDraw.Draw(canvas)
    t_bbox     = draw.textbbox((0, 0), label, font=footer_font)
    t_w        = t_bbox[2] - t_bbox[0]
    t_h        = t_bbox[3] - t_bbox[1]

    total_w    = icon_w + gap + t_w
    sx         = (WIDTH - total_w) // 2
    iy         = HEIGHT - FOOTER_H + (FOOTER_H - icon_h) // 2

    # Two overlapping mountain peaks drawn on a transparent layer
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
    icon_color = DARK_NAVY if is_light else WHITE
    ld.polygon([(x, y) for x, y in small_peak], fill=(*icon_color, 80))
    ld.polygon([(x, y) for x, y in big_peak],   fill=(*icon_color, 140))
    canvas.alpha_composite(logo_layer)

    footer_color = (*DARK_NAVY, 130) if is_light else (*WHITE, 150)
    draw  = ImageDraw.Draw(canvas)
    tx    = sx + icon_w + gap
    ty    = iy + (icon_h - t_h) // 2 - t_bbox[1]
    draw.text((tx, ty), label, fill=footer_color, font=footer_font)

    canvas.convert("RGB").save(output_path, "PNG", optimize=True)


if __name__ == "__main__":
    import tempfile
    backgrounds = ["night_court_outdoor", "indoor_arena", "rooftop_city", "karte_1"]
    bg = sys.argv[1] if len(sys.argv) > 1 else "night_court_outdoor"
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name
    generate_card(
        queries=["203999", "1629029", "1629627", "201142", "203081"],
        title="MY TOP 5",
        subtitle="ALL-TIME GREATS",
        output_path=out,
        background=bg,
    )
    print(f"Card saved to: {out}")
