"""
Generate a Rushmore Top-5 card image — V2 Design.
Headshot as faded background element, cleaner typography, more breathing room.
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# --- Constants ---
# Pass --insta to generate 4:5 format (1080×1350) optimized for Instagram feed
INSTA_MODE = '--insta' in sys.argv

WIDTH  = 1080
HEIGHT = 1350 if INSTA_MODE else 1920
PADDING = 48 if INSTA_MODE else 40
CARD_GAP = 10 if INSTA_MODE else 12
TITLE_AREA_HEIGHT = 160 if INSTA_MODE else 180
FOOTER_HEIGHT     = 65  if INSTA_MODE else 80

CARD_AREA_TOP    = TITLE_AREA_HEIGHT
CARD_AREA_BOTTOM = HEIGHT - FOOTER_HEIGHT
CARD_HEIGHT      = (CARD_AREA_BOTTOM - CARD_AREA_TOP - 4 * CARD_GAP) // 5

# Colors
BG_COLOR = "#0a0a0f"
CARD_BG = "#111118"
TEXT_WHITE = "#f0f0f5"
TEXT_SECONDARY = "#a0a0b8"
TEXT_MUTED = "#5a5a72"
GOLD = "#c9a84c"

HEADSHOT_DIR = Path(__file__).parent.parent / "assets" / "headshots"
SILHOUETTE_DIR = Path(__file__).parent.parent / "assets" / "silhouettes"
DB_PATH = Path(__file__).parent.parent / "players.json"

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
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]

    font_map = {
        "heavy": ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Avenir Next.ttc"],
        "bold": ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Avenir Next.ttc"],
        "medium": ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Avenir Next.ttc"],
        "regular": ["/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Avenir Next.ttc"],
    }
    index_map = {"heavy": [0, 10], "bold": [0, 8], "medium": [0, 6], "regular": [0, 0]}

    for fp, idx in zip(font_map.get(weight, font_map["regular"]), index_map.get(weight, [0, 0])):
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


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def blend_color(hex_color, alpha, bg=(17, 17, 24)):
    r, g, b = hex_to_rgb(hex_color)
    a = alpha / 255
    return (int(r * a + bg[0] * (1 - a)), int(g * a + bg[1] * (1 - a)), int(b * a + bg[2] * (1 - a)))


def get_team_colors(teams):
    if not teams:
        return TEAM_COLORS["DEFAULT"]
    return TEAM_COLORS.get(teams[0], TEAM_COLORS["DEFAULT"])


def load_players():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def find_players(player_db, queries):
    results = []
    for q in queries:
        found = None
        if isinstance(q, int) or (isinstance(q, str) and q.isdigit()):
            found = next((p for p in player_db if p["id"] == int(q)), None)
        if not found:
            q_lower = q.lower() if isinstance(q, str) else str(q).lower()
            found = next((p for p in player_db if q_lower in p["name"].lower()), None)
        if found:
            results.append(found)
    return results


def draw_headshot_bg(img, player_id, card_x, card_y, card_w, card_h, team_color):
    """Draw headshot as a faded background element on the right side of the card."""
    headshot_path = HEADSHOT_DIR / f"{player_id}.png"
    if not headshot_path.exists():
        # Try silhouette as fallback
        sil_path = SILHOUETTE_DIR / f"{player_id}.png"
        if not sil_path.exists():
            return
        headshot_path = sil_path

    hs = Image.open(headshot_path).convert("RGBA")

    # Scale headshot to fill card height
    scale = (card_h + 20) / hs.height
    new_w = int(hs.width * scale)
    new_h = int(hs.height * scale)
    hs = hs.resize((new_w, new_h), Image.LANCZOS)

    # Position: right-aligned within the card, vertically centered
    paste_x = card_x + card_w - new_w + int(new_w * 0.15)  # slight overflow right
    paste_y = card_y + (card_h - new_h) // 2

    # Create a faded version — reduce opacity
    alpha = hs.getchannel("A")
    # Dim the alpha to make it subtle
    alpha = ImageEnhance.Brightness(alpha).enhance(0.35)
    hs.putalpha(alpha)

    # Create a gradient mask to fade from right to left
    gradient = Image.new("L", (new_w, new_h), 0)
    grad_draw = ImageDraw.Draw(gradient)
    fade_start = int(new_w * 0.15)  # start fading from left portion
    for x in range(new_w):
        if x < fade_start:
            val = 0
        else:
            val = int(255 * ((x - fade_start) / (new_w - fade_start)) ** 0.7)
        grad_draw.line([(x, 0), (x, new_h)], fill=val)

    # Combine gradient with existing alpha
    current_alpha = hs.getchannel("A")
    combined = Image.new("L", (new_w, new_h))
    for px in range(new_w):
        for py in range(new_h):
            a = current_alpha.getpixel((px, py))
            g = gradient.getpixel((px, py))
            combined.putpixel((px, py), int(a * g / 255))
    hs.putalpha(combined)

    # Clip to card bounds
    # Create a temporary canvas the size of the full image
    temp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    temp.paste(hs, (paste_x, paste_y), hs)

    # Create card-shaped mask
    card_mask = Image.new("L", img.size, 0)
    card_mask_draw = ImageDraw.Draw(card_mask)
    card_mask_draw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=16,
        fill=255,
    )

    # Apply card mask to temp
    temp_alpha = temp.getchannel("A")
    clipped_alpha = Image.new("L", img.size, 0)
    for px in range(max(0, paste_x), min(img.width, paste_x + new_w)):
        for py in range(max(0, paste_y), min(img.height, paste_y + new_h)):
            a = temp_alpha.getpixel((px, py))
            m = card_mask.getpixel((px, py))
            clipped_alpha.putpixel((px, py), int(a * m / 255))
    temp.putalpha(clipped_alpha)

    img.paste(temp, (0, 0), temp)


def draw_headshot_bg_fast(img, player_id, card_x, card_y, card_w, card_h, team_color):
    """Draw headshot as faded background — optimized version using numpy-free approach."""
    headshot_path = HEADSHOT_DIR / f"{player_id}.png"
    if not headshot_path.exists():
        sil_path = SILHOUETTE_DIR / f"{player_id}.png"
        if not sil_path.exists():
            return
        headshot_path = sil_path

    hs = Image.open(headshot_path).convert("RGBA")

    # Scale to fill card height
    scale = (card_h + 10) / hs.height
    new_w = int(hs.width * scale)
    new_h = int(hs.height * scale)
    hs = hs.resize((new_w, new_h), Image.LANCZOS)

    # Reduce opacity
    r, g, b, a = hs.split()
    a = ImageEnhance.Brightness(a).enhance(0.3)

    # Create horizontal gradient fade (left side fades out)
    gradient = Image.new("L", (new_w, new_h), 0)
    grad_draw = ImageDraw.Draw(gradient)
    fade_start = int(new_w * 0.2)
    for x in range(fade_start, new_w):
        val = int(255 * ((x - fade_start) / (new_w - fade_start)) ** 0.6)
        grad_draw.line([(x, 0), (x, new_h)], fill=val)

    # Multiply alpha with gradient
    a = Image.composite(a, Image.new("L", (new_w, new_h), 0), gradient)
    hs = Image.merge("RGBA", (r, g, b, a))

    # Position right-aligned
    paste_x = card_x + card_w - new_w + int(new_w * 0.12)
    paste_y = card_y + (card_h - new_h) // 2

    # Crop to card bounds
    crop_left = max(0, card_x - paste_x)
    crop_top = max(0, card_y - paste_y)
    crop_right = min(new_w, card_x + card_w - paste_x)
    crop_bottom = min(new_h, card_y + card_h - paste_y)

    if crop_left >= crop_right or crop_top >= crop_bottom:
        return

    cropped = hs.crop((crop_left, crop_top, crop_right, crop_bottom))
    final_x = paste_x + crop_left
    final_y = paste_y + crop_top

    img.paste(cropped, (final_x, final_y), cropped)


def draw_player_card(img, draw, player, rank, y_pos):
    card_x = PADDING
    card_y = y_pos
    card_w = WIDTH - 2 * PADDING
    card_h = CARD_HEIGHT

    colors = get_team_colors(player.get("teams", []))
    team_primary = colors["primary"]

    # Card background
    draw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=16,
        fill=CARD_BG,
    )

    # Subtle team color gradient on left edge
    gradient_w = int(card_w * 0.25)
    for x_off in range(gradient_w):
        alpha = int(25 * (1 - x_off / gradient_w))
        color = blend_color(team_primary, alpha)
        draw.line([(card_x + x_off, card_y + 1), (card_x + x_off, card_y + card_h - 1)], fill=color)

    # Headshot as faded background element on right
    player_id = player.get("id")
    if player_id:
        draw_headshot_bg_fast(img, player_id, card_x, card_y, card_w, card_h, team_primary)

    # Left accent line
    accent_h = int(card_h * 0.5)
    accent_y = card_y + (card_h - accent_h) // 2
    draw.rounded_rectangle(
        (card_x + 1, accent_y, card_x + 4, accent_y + accent_h),
        radius=2,
        fill=team_primary,
    )

    # --- Rank number ---
    rank_font = get_font(72, "heavy")
    rank_str = str(rank)
    rank_bbox = draw.textbbox((0, 0), rank_str, font=rank_font)
    rank_w = rank_bbox[2] - rank_bbox[0]
    rank_x = card_x + 22
    rank_y = card_y + (card_h - (rank_bbox[3] - rank_bbox[1])) // 2 - 4

    # Rank with slight gold glow effect
    draw.text((rank_x, rank_y), rank_str, fill=GOLD, font=rank_font)

    # --- Player info ---
    info_x = rank_x + rank_w + 28
    info_y_center = card_y + card_h // 2

    # Name — larger, bolder
    font_name = get_font(34, "bold")
    name_bbox = draw.textbbox((0, 0), player["name"], font=font_name)
    name_h = name_bbox[3] - name_bbox[1]

    # Calculate total text block height to center it
    has_awards = bool(player.get("awards", {}).get("championships", 0) or
                      player.get("awards", {}).get("mvps", 0) or
                      player.get("awards", {}).get("all_star", 0))
    block_h = name_h + 24 + (20 if has_awards else 0)
    text_top = info_y_center - block_h // 2

    draw.text((info_x, text_top), player["name"], fill=TEXT_WHITE, font=font_name)

    # Meta line: Position · Teams · Years
    font_meta = get_font(16, "regular")
    position = player.get("position", "")
    teams_str = " / ".join(player.get("teams", [])[:3])
    from_year = player.get("from_year", "")
    to_year = player.get("to_year", "")
    years = f"{from_year}-{to_year}" if from_year and to_year else ""
    meta_parts = [p for p in [position, teams_str, years] if p]
    meta_str = "  ·  ".join(meta_parts)
    draw.text((info_x, text_top + name_h + 6), meta_str, fill=TEXT_MUTED, font=font_meta)

    # Awards line
    if has_awards:
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

        font_awards = get_font(14, "medium")
        award_str = "  ·  ".join(award_parts)
        draw.text((info_x, text_top + name_h + 28), award_str, fill=GOLD, font=font_awards)

    # --- Stats (left-aligned below player info) ---
    font_stat_val = get_font(20, "bold")
    font_stat_label = get_font(11, "regular")

    ppg = player.get("ppg", "N/A")
    rpg = player.get("rpg", "N/A")
    apg = player.get("apg", "N/A")

    stat_items = [("PPG", ppg), ("RPG", rpg), ("APG", apg)]
    stat_gap = 24
    stat_y = card_y + card_h - 46
    sx = info_x

    for label, val in stat_items:
        val_str = str(val)
        val_bbox = draw.textbbox((0, 0), val_str, font=font_stat_val)
        lab_bbox = draw.textbbox((0, 0), label, font=font_stat_label)
        val_w = val_bbox[2] - val_bbox[0]
        lab_w = lab_bbox[2] - lab_bbox[0]

        draw.text((sx, stat_y), val_str, fill=TEXT_WHITE, font=font_stat_val)
        draw.text((sx + val_w + 4, stat_y + 4), label, fill=TEXT_MUTED, font=font_stat_label)

        sx += val_w + lab_w + stat_gap


def generate_card(player_queries, title="MY MT. RUSHMORE", subtitle="ALL-TIME GREATEST", output_path=None):
    player_db = load_players()
    players = find_players(player_db, player_queries)

    if not players:
        print("Error: No valid players found.")
        return None

    players = players[:5]

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- Title area (compact) ---
    font_title = get_font(44, "heavy")
    font_subtitle = get_font(18, "medium")

    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_w) // 2, 48), title, fill=TEXT_WHITE, font=font_title)

    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((WIDTH - sub_w) // 2, 102), subtitle, fill=GOLD, font=font_subtitle)

    # Minimal decorative line
    line_y = 138
    line_half = 40
    draw.line(
        [(WIDTH // 2 - line_half, line_y), (WIDTH // 2 + line_half, line_y)],
        fill=GOLD, width=1,
    )
    # Fade sides
    for i in range(60):
        alpha = int(50 * (1 - i / 60))
        c = blend_color(GOLD, alpha, hex_to_rgb(BG_COLOR))
        draw.point((WIDTH // 2 - line_half - i, line_y), fill=c)
        draw.point((WIDTH // 2 + line_half + i, line_y), fill=c)

    # --- Player cards ---
    for i, player in enumerate(players):
        y = CARD_AREA_TOP + i * (CARD_HEIGHT + CARD_GAP)
        draw_player_card(img, draw, player, i + 1, y)

    # --- Footer (minimal) ---
    font_brand = get_font(16, "bold")
    brand = "RUSHMORE"
    bb = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bb[2] - bb[0]
    draw.text(((WIDTH - bw) // 2, HEIGHT - 52), brand, fill=TEXT_MUTED, font=font_brand)

    # --- Save ---
    if output_path is None:
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"rushmore_v2_{ts}.png"

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

    player_args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if player_args:
        demo_players = player_args[:5]

    generate_card(demo_players)
