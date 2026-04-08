"""
Generate a Rushmore Top-5 card image (9:16, 1080x1920).
Input: list of 5 player IDs or names, optional title
Output: PNG image
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- Constants ---
WIDTH, HEIGHT = 1080, 1920
PADDING = 48
CARD_GAP = 16
TITLE_AREA_HEIGHT = 240
FOOTER_HEIGHT = 100

CARD_AREA_TOP = TITLE_AREA_HEIGHT
CARD_AREA_BOTTOM = HEIGHT - FOOTER_HEIGHT
CARD_HEIGHT = (CARD_AREA_BOTTOM - CARD_AREA_TOP - 4 * CARD_GAP) // 5

# Colors
BG_COLOR = "#08080d"
CARD_BG = "#121219"
CARD_BG_LIGHT = "#1a1a24"
TEXT_WHITE = "#f0f0f5"
TEXT_SECONDARY = "#b0b0c0"
TEXT_MUTED = "#6a6a80"
GOLD = "#c9a84c"
GOLD_BRIGHT = "#e8c84a"

TEAM_COLORS = {
    "BOS": {"primary": "#007A33", "secondary": "#BA9653"},
    "BKN": {"primary": "#000000", "secondary": "#FFFFFF"},
    "NYK": {"primary": "#006BB6", "secondary": "#F58426"},
    "PHI": {"primary": "#006BB6", "secondary": "#ED174C"},
    "TOR": {"primary": "#CE1141", "secondary": "#000000"},
    "CHI": {"primary": "#CE1141", "secondary": "#000000"},
    "CLE": {"primary": "#860038", "secondary": "#FDBB30"},
    "DET": {"primary": "#C8102E", "secondary": "#1D42BA"},
    "IND": {"primary": "#002D62", "secondary": "#FDBB30"},
    "MIL": {"primary": "#00471B", "secondary": "#EEE1C6"},
    "ATL": {"primary": "#E03A3E", "secondary": "#C1D32F"},
    "CHA": {"primary": "#1D1160", "secondary": "#00788C"},
    "MIA": {"primary": "#98002E", "secondary": "#F9A01B"},
    "ORL": {"primary": "#0077C0", "secondary": "#C4CED4"},
    "WAS": {"primary": "#002B5C", "secondary": "#E31837"},
    "DEN": {"primary": "#0E2240", "secondary": "#FEC524"},
    "MIN": {"primary": "#0C2340", "secondary": "#236192"},
    "OKC": {"primary": "#007AC1", "secondary": "#EF6024"},
    "POR": {"primary": "#E03A3E", "secondary": "#000000"},
    "UTA": {"primary": "#002B5C", "secondary": "#F9A01B"},
    "GSW": {"primary": "#1D428A", "secondary": "#FFC72C"},
    "LAC": {"primary": "#C8102E", "secondary": "#1D428A"},
    "LAL": {"primary": "#552583", "secondary": "#FDB927"},
    "PHX": {"primary": "#1D1160", "secondary": "#E56020"},
    "SAC": {"primary": "#5A2D81", "secondary": "#63727A"},
    "DAL": {"primary": "#00538C", "secondary": "#002B5E"},
    "HOU": {"primary": "#CE1141", "secondary": "#000000"},
    "MEM": {"primary": "#5D76A9", "secondary": "#12173F"},
    "NOP": {"primary": "#0C2340", "secondary": "#C8102E"},
    "SAS": {"primary": "#C4CED4", "secondary": "#000000"},
    "NJN": {"primary": "#002A60", "secondary": "#CD1041"},
    "SEA": {"primary": "#00653A", "secondary": "#FFC200"},
    "VAN": {"primary": "#00B2A9", "secondary": "#E43C40"},
    "NOH": {"primary": "#0C2340", "secondary": "#C8102E"},
    "NOK": {"primary": "#0C2340", "secondary": "#C8102E"},
    "CHH": {"primary": "#1D1160", "secondary": "#00788C"},
    "CHO": {"primary": "#1D1160", "secondary": "#00788C"},
    "WSB": {"primary": "#002B5C", "secondary": "#E31837"},
    "KCK": {"primary": "#C8102E", "secondary": "#1D428A"},
    "SDC": {"primary": "#C8102E", "secondary": "#1D428A"},
    "BUF": {"primary": "#003DA5", "secondary": "#CE1141"},
    "PHW": {"primary": "#006BB6", "secondary": "#ED174C"},
    "STL": {"primary": "#E03A3E", "secondary": "#002B5C"},
    "CIN": {"primary": "#C8102E", "secondary": "#000000"},
    "NOJ": {"primary": "#00778B", "secondary": "#E31837"},
    "DEFAULT": {"primary": "#555566", "secondary": "#888899"},
}

# --- Font cache ---
_font_cache = {}


def get_font(size, weight="regular"):
    """Load fonts with caching. weight: 'regular', 'medium', 'bold', 'heavy'"""
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]

    font_map = {
        "heavy": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ],
        "bold": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ],
        "medium": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ],
        "regular": [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ],
    }

    # Font index within .ttc files for different weights
    index_map = {
        "heavy": [0, 10, 0],
        "bold": [0, 8, 0],
        "medium": [0, 6, 0],
        "regular": [0, 0, 0],
    }

    paths = font_map.get(weight, font_map["regular"])
    indices = index_map.get(weight, index_map["regular"])

    for fp, idx in zip(paths, indices):
        try:
            font = ImageFont.truetype(fp, size, index=idx)
            _font_cache[key] = font
            return font
        except (OSError, IOError):
            try:
                font = ImageFont.truetype(fp, size)
                _font_cache[key] = font
                return font
            except (OSError, IOError):
                continue

    font = ImageFont.load_default()
    _font_cache[key] = font
    return font


def load_players():
    db_path = Path(__file__).parent.parent / "players.json"
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_players(player_db, queries):
    """Find players by ID (int) or name (string, partial match)."""
    results = []
    for q in queries:
        found = None
        if isinstance(q, int) or (isinstance(q, str) and q.isdigit()):
            pid = int(q)
            found = next((p for p in player_db if p["id"] == pid), None)
        if not found:
            q_lower = q.lower() if isinstance(q, str) else str(q).lower()
            found = next(
                (p for p in player_db if q_lower in p["name"].lower()), None
            )
        if found:
            results.append(found)
        else:
            print(f"Warning: Player '{q}' not found, skipping.")
    return results


def get_team_colors(teams):
    if not teams:
        return TEAM_COLORS["DEFAULT"]
    return TEAM_COLORS.get(teams[0], TEAM_COLORS["DEFAULT"])


def hex_to_rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def blend_color(hex_color, alpha, bg=(18, 18, 25)):
    """Blend a hex color with alpha onto a background."""
    r, g, b = hex_to_rgb(hex_color)
    a = alpha / 255
    return (
        int(r * a + bg[0] * (1 - a)),
        int(g * a + bg[1] * (1 - a)),
        int(b * a + bg[2] * (1 - a)),
    )


def draw_team_gradient(img, card_x, card_y, card_w, card_h, team_color):
    """Draw a subtle horizontal gradient with team color on the left fading out."""
    gradient_w = int(card_w * 0.35)
    for x_offset in range(gradient_w):
        alpha = int(35 * (1 - x_offset / gradient_w))
        color = blend_color(team_color, alpha)
        x = card_x + x_offset
        img_draw = ImageDraw.Draw(img)
        img_draw.line([(x, card_y + 1), (x, card_y + card_h - 1)], fill=color)


SILHOUETTE_DIR = Path(__file__).parent.parent / "assets" / "silhouettes"
HEADSHOT_DIR = Path(__file__).parent.parent / "assets" / "headshots"


def draw_player_image(draw, x, y, w, h, team_color, player_id=None, img=None):
    """Draw player image — headshot first, then silhouette, then geometric fallback."""
    color = blend_color(team_color, 100)

    if player_id and img:
        # Try headshot first
        headshot_path = HEADSHOT_DIR / f"{player_id}.png"
        if headshot_path.exists():
            hs = Image.open(headshot_path).convert("RGBA")

            # Fit into available space
            pad = 2
            target_w = w - 2 * pad
            target_h = h - 2 * pad
            hs.thumbnail((target_w, target_h), Image.LANCZOS)

            # Center, align to bottom of area
            paste_x = x + pad + (target_w - hs.width) // 2
            paste_y = y + h - pad - hs.height
            img.paste(hs, (paste_x, paste_y), hs)
            return

        # Try silhouette
        sil_path = SILHOUETTE_DIR / f"{player_id}.png"
        if sil_path.exists():
            sil = Image.open(sil_path).convert("RGBA")

            pad = 4
            target_w = w - 2 * pad
            target_h = h - 2 * pad
            sil.thumbnail((target_w, target_h), Image.LANCZOS)

            # Tint with team color
            r, g, b = color
            tinted = Image.new("RGBA", sil.size, (r, g, b, 255))
            tinted.putalpha(sil.getchannel("A"))

            paste_x = x + pad + (target_w - sil.width) // 2
            paste_y = y + pad + (target_h - sil.height) // 2
            img.paste(tinted, (paste_x, paste_y), tinted)
            return

    # Fallback: geometric placeholder
    cx = x + w // 2

    head_r = int(w * 0.14)
    head_cy = y + int(h * 0.22)
    draw.ellipse(
        [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
        fill=color,
    )

    body_top = head_cy + head_r + int(h * 0.02)
    body_w = int(w * 0.65)
    body_h = int(h * 0.55)
    bx = cx - body_w // 2

    points = [
        (bx, body_top + int(body_h * 0.15)),
        (bx + int(body_w * 0.15), body_top),
        (bx + int(body_w * 0.85), body_top),
        (bx + body_w, body_top + int(body_h * 0.15)),
        (bx + int(body_w * 0.85), body_top + body_h),
        (bx + int(body_w * 0.15), body_top + body_h),
    ]
    draw.polygon(points, fill=color)


def draw_stat_pill(draw, x, y, value, label, font_val, font_label):
    """Draw a stat with value above label."""
    val_str = str(value)
    val_bbox = draw.textbbox((0, 0), val_str, font=font_val)
    val_w = val_bbox[2] - val_bbox[0]

    lab_bbox = draw.textbbox((0, 0), label, font=font_label)
    lab_w = lab_bbox[2] - lab_bbox[0]

    total_w = max(val_w, lab_w)
    cx = x + total_w // 2

    draw.text((cx - val_w // 2, y), val_str, fill=TEXT_WHITE, font=font_val)
    draw.text((cx - lab_w // 2, y + 30), label, fill=TEXT_MUTED, font=font_label)

    return total_w


def draw_player_card(img, draw, player, rank, y_pos):
    """Draw a single player card row."""
    card_x = PADDING
    card_y = y_pos
    card_w = WIDTH - 2 * PADDING
    card_h = CARD_HEIGHT

    colors = get_team_colors(player.get("teams", []))
    team_primary = colors["primary"]

    # Card background
    draw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=14,
        fill=CARD_BG,
    )

    # Team color gradient overlay
    draw_team_gradient(img, card_x, card_y, card_w, card_h, team_primary)

    # Left accent bar
    bar_h = int(card_h * 0.6)
    bar_y = card_y + (card_h - bar_h) // 2
    draw.rounded_rectangle(
        (card_x, bar_y, card_x + 4, bar_y + bar_h),
        radius=2,
        fill=team_primary,
    )

    # --- Rank ---
    rank_x = card_x + 20
    rank_font = get_font(56, "heavy")
    rank_str = str(rank)
    draw.text(
        (rank_x, card_y + card_h // 2 - 32),
        rank_str,
        fill=GOLD,
        font=rank_font,
    )

    # --- Silhouette ---
    sil_w = int(card_h * 0.65)
    sil_x = card_x + 70
    draw_player_image(draw, sil_x, card_y + 6, sil_w, card_h - 12, team_primary, player.get("id"), img)

    # --- Player info ---
    info_x = sil_x + sil_w + 12
    info_y = card_y + int(card_h * 0.16)

    # Name
    font_name = get_font(30, "bold")
    draw.text((info_x, info_y), player["name"], fill=TEXT_WHITE, font=font_name)

    # Position | Teams | Years
    font_meta = get_font(17, "regular")
    position = player.get("position", "")
    teams_str = " / ".join(player.get("teams", [])[:3])
    from_year = player.get("from_year", "")
    to_year = player.get("to_year", "")
    years = f"{from_year}-{to_year}" if from_year and to_year else ""

    meta_parts = [p for p in [position, teams_str, years] if p]
    meta_str = "  ·  ".join(meta_parts)
    draw.text((info_x, info_y + 36), meta_str, fill=TEXT_MUTED, font=font_meta)

    # Awards
    awards = player.get("awards", {})
    award_parts = []
    rings = awards.get("championships", 0)
    mvps = awards.get("mvps", 0)
    allstar = awards.get("all_star", 0)
    if rings:
        award_parts.append(f"{rings}x Champ")
    if mvps:
        award_parts.append(f"{mvps}x MVP")
    if allstar:
        award_parts.append(f"{allstar}x All-Star")

    if award_parts:
        font_awards = get_font(15, "medium")
        award_str = "  ·  ".join(award_parts)
        draw.text((info_x, info_y + 58), award_str, fill=GOLD, font=font_awards)

    # --- Stats (right-aligned) ---
    stats_right = card_x + card_w - 24
    font_stat_val = get_font(24, "bold")
    font_stat_label = get_font(12, "regular")

    ppg = player.get("ppg", "N/A")
    rpg = player.get("rpg", "N/A")
    apg = player.get("apg", "N/A")

    stat_items = [("APG", apg), ("RPG", rpg), ("PPG", ppg)]
    stat_x = stats_right

    for label, val in stat_items:
        val_str = str(val)
        val_bbox = draw.textbbox((0, 0), val_str, font=font_stat_val)
        lab_bbox = draw.textbbox((0, 0), label, font=font_stat_label)
        col_w = max(val_bbox[2] - val_bbox[0], lab_bbox[2] - lab_bbox[0]) + 8

        stat_x -= col_w
        cx = stat_x + col_w // 2

        val_w = val_bbox[2] - val_bbox[0]
        lab_w = lab_bbox[2] - lab_bbox[0]

        stat_y = card_y + int(card_h * 0.25)
        draw.text((cx - val_w // 2, stat_y), val_str, fill=TEXT_WHITE, font=font_stat_val)
        draw.text((cx - lab_w // 2, stat_y + 32), label, fill=TEXT_MUTED, font=font_stat_label)

        stat_x -= 16  # gap between stats

    # Thin separator line between stats and info
    sep_x = stat_x - 8
    sep_y1 = card_y + int(card_h * 0.2)
    sep_y2 = card_y + int(card_h * 0.8)
    draw.line([(sep_x, sep_y1), (sep_x, sep_y2)], fill="#252535", width=1)


def generate_card(player_queries, title="MY MT. RUSHMORE", subtitle="ALL-TIME GREATEST", output_path=None):
    """Generate the full card image."""
    player_db = load_players()
    players = find_players(player_db, player_queries)

    if not players:
        print("Error: No valid players found.")
        return None

    if len(players) > 5:
        players = players[:5]

    # Create image
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- Background texture: subtle vertical lines ---
    for x in range(0, WIDTH, 4):
        if x % 8 == 0:
            draw.line([(x, 0), (x, HEIGHT)], fill="#0b0b10", width=1)

    # --- Title area ---
    font_title = get_font(48, "heavy")
    font_subtitle = get_font(20, "medium")

    # Title centered
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(
        ((WIDTH - title_w) // 2, 60),
        title,
        fill=TEXT_WHITE,
        font=font_title,
    )

    # Subtitle
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(
        ((WIDTH - sub_w) // 2, 120),
        subtitle,
        fill=GOLD,
        font=font_subtitle,
    )

    # Decorative line
    line_y = 162
    line_half = 50
    # Gold center segment
    draw.line(
        [(WIDTH // 2 - line_half, line_y), (WIDTH // 2 + line_half, line_y)],
        fill=GOLD,
        width=2,
    )
    # Fading side lines
    fade_len = 80
    for i in range(fade_len):
        alpha = int(60 * (1 - i / fade_len))
        c = blend_color(GOLD, alpha, hex_to_rgb(BG_COLOR))
        draw.point((WIDTH // 2 - line_half - i, line_y), fill=c)
        draw.point((WIDTH // 2 + line_half + i, line_y), fill=c)

    # --- Player cards ---
    for i, player in enumerate(players):
        y = CARD_AREA_TOP + i * (CARD_HEIGHT + CARD_GAP)
        draw_player_card(img, draw, player, i + 1, y)

    # --- Footer ---
    font_footer = get_font(14, "regular")
    font_brand = get_font(18, "bold")

    # Brand name
    brand = "RUSHMORE"
    bb = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bb[2] - bb[0]
    brand_y = HEIGHT - FOOTER_HEIGHT + 24
    draw.text(((WIDTH - bw) // 2, brand_y), brand, fill=TEXT_MUTED, font=font_brand)

    # Tagline
    tagline = "nba all-time lists"
    tb = draw.textbbox((0, 0), tagline, font=font_footer)
    tw = tb[2] - tb[0]
    draw.text(((WIDTH - tw) // 2, brand_y + 26), tagline, fill="#444455", font=font_footer)

    # --- Save ---
    if output_path is None:
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"rushmore_{ts}.png"

    img.save(output_path, "PNG")
    print(f"Card saved to: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    demo_players = [
        "Michael Jordan",
        "LeBron James",
        "Kobe Bryant",
        "Kareem Abdul-Jabbar",
        "Magic Johnson",
    ]

    if len(sys.argv) > 1:
        demo_players = sys.argv[1:6]

    generate_card(demo_players)
