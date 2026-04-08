"""
Generate a Rushmore Top-5 Teams card image.
Shows ranked team selection with team colors and logos.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

LOGO_DIR = Path(__file__).parent.parent / "assets" / "team_logos"

WIDTH, HEIGHT = 1080, 1920
PADDING = 40
CARD_GAP = 12
TITLE_AREA_HEIGHT = 180
FOOTER_HEIGHT = 80

CARD_AREA_TOP = TITLE_AREA_HEIGHT
CARD_AREA_BOTTOM = HEIGHT - FOOTER_HEIGHT
CARD_HEIGHT = (CARD_AREA_BOTTOM - CARD_AREA_TOP - 4 * CARD_GAP) // 5

BG_COLOR = "#0a0a0f"
CARD_BG = "#111118"
TEXT_WHITE = "#f0f0f5"
TEXT_SECONDARY = "#a0a0b8"
TEXT_MUTED = "#5a5a72"
GOLD = "#c9a84c"

TEAM_COLORS = {
    "ATL": {"primary": "#E03A3E", "secondary": "#C1D32F"},
    "BOS": {"primary": "#007A33", "secondary": "#BA9653"},
    "BKN": {"primary": "#FFFFFF", "secondary": "#000000"},
    "CHA": {"primary": "#1D1160", "secondary": "#00788C"},
    "CHI": {"primary": "#CE1141", "secondary": "#000000"},
    "CLE": {"primary": "#860038", "secondary": "#FDBB30"},
    "DAL": {"primary": "#00538C", "secondary": "#002B5E"},
    "DEN": {"primary": "#0E2240", "secondary": "#FEC524"},
    "DET": {"primary": "#C8102E", "secondary": "#1D42BA"},
    "GSW": {"primary": "#1D428A", "secondary": "#FFC72C"},
    "HOU": {"primary": "#CE1141", "secondary": "#000000"},
    "IND": {"primary": "#002D62", "secondary": "#FDBB30"},
    "LAC": {"primary": "#C8102E", "secondary": "#1D428A"},
    "LAL": {"primary": "#552583", "secondary": "#FDB927"},
    "MEM": {"primary": "#5D76A9", "secondary": "#12173F"},
    "MIA": {"primary": "#98002E", "secondary": "#F9A01B"},
    "MIL": {"primary": "#00471B", "secondary": "#EEE1C6"},
    "MIN": {"primary": "#0C2340", "secondary": "#236192"},
    "NOP": {"primary": "#0C2340", "secondary": "#C8102E"},
    "NYK": {"primary": "#006BB6", "secondary": "#F58426"},
    "OKC": {"primary": "#007AC1", "secondary": "#EF6024"},
    "ORL": {"primary": "#0077C0", "secondary": "#C4CED4"},
    "PHI": {"primary": "#006BB6", "secondary": "#ED174C"},
    "PHX": {"primary": "#1D1160", "secondary": "#E56020"},
    "POR": {"primary": "#E03A3E", "secondary": "#000000"},
    "SAC": {"primary": "#5A2D81", "secondary": "#63727A"},
    "SAS": {"primary": "#C4CED4", "secondary": "#000000"},
    "TOR": {"primary": "#CE1141", "secondary": "#000000"},
    "UTA": {"primary": "#002B5C", "secondary": "#F9A01B"},
    "WAS": {"primary": "#002B5C", "secondary": "#E31837"},
}

TEAM_NAMES = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}

_font_cache = {}


def get_font(size, weight="regular"):
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]
    _fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
    bold = weight in ("heavy", "bold")
    candidates = [
        str(_fonts_dir / ("Impact.ttf" if bold else "Helvetica.ttc")),
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in candidates:
        try:
            font = ImageFont.truetype(fp, size)
            _font_cache[key] = font
            return font
        except Exception:
            continue
    font = ImageFont.load_default()
    _font_cache[key] = font
    return font


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def is_light_color(hex_color: str, threshold: float = 0.5) -> bool:
    """Return True if the color is light (needs dark text on top)."""
    r, g, b = hex_to_rgb(hex_color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance > threshold


def blend_color(hex_color, alpha, bg=(17, 17, 24)):
    r, g, b = hex_to_rgb(hex_color)
    a = alpha / 255
    return (int(r * a + bg[0] * (1 - a)), int(g * a + bg[1] * (1 - a)), int(b * a + bg[2] * (1 - a)))


def _load_team_logo_pil(team_code: str, size: int):
    path = LOGO_DIR / f"{team_code.upper()}.png"
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    # Pad to square if needed
    if img.width != img.height:
        dim = max(img.width, img.height)
        sq = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        sq.paste(img, ((dim - img.width) // 2, (dim - img.height) // 2))
        img = sq
    return img.resize((size, size), Image.LANCZOS)


def draw_team_card(img, draw, team_code, rank, y_pos, stats=None, tier_label=None):
    card_x = PADDING
    card_y = y_pos
    card_w = WIDTH - 2 * PADDING
    card_h = CARD_HEIGHT

    colors = TEAM_COLORS.get(team_code, {"primary": "#555566", "secondary": "#888899"})
    primary = colors["primary"]
    secondary = colors["secondary"]
    primary_rgb = hex_to_rgb(primary)
    secondary_rgb = hex_to_rgb(secondary)
    bg_rgb = hex_to_rgb(CARD_BG)
    light_primary = is_light_color(primary)
    text_on_card   = TEXT_WHITE
    text_on_card_2 = TEXT_SECONDARY
    text_on_card_m = TEXT_MUTED

    # Card background
    draw.rounded_rectangle(
        (card_x, card_y, card_x + card_w, card_y + card_h),
        radius=16, fill=CARD_BG,
    )

    # Team color gradient — only for dark primaries (light ones stay dark for readability)
    if not light_primary:
        gradient_w = int(card_w * 0.75)
        for x_off in range(gradient_w):
            t = x_off / gradient_w
            alpha = int(90 * (1 - t) ** 1.2)
            color = blend_color(primary, alpha, bg_rgb)
            draw.line(
                [(card_x + x_off, card_y + 1), (card_x + x_off, card_y + card_h - 1)],
                fill=color,
            )

    # Bold left accent bar in primary color
    accent_h = int(card_h * 0.65)
    accent_y = card_y + (card_h - accent_h) // 2
    draw.rounded_rectangle(
        (card_x + 1, accent_y, card_x + 6, accent_y + accent_h),
        radius=3, fill=primary,
    )

    # Rank number
    font_rank = get_font(72, "heavy")
    rank_str = str(rank)
    rank_bbox = draw.textbbox((0, 0), rank_str, font=font_rank)
    rank_h = rank_bbox[3] - rank_bbox[1]
    rank_y = card_y + (card_h - rank_h) // 2 - 4
    draw.text((card_x + 22, rank_y), rank_str, fill=GOLD, font=font_rank)

    rank_w = rank_bbox[2] - rank_bbox[0]
    info_x = card_x + 22 + rank_w + 32
    center_y = card_y + card_h // 2

    # Team logo — right side, large
    LOGO_SIZE = int(card_h * 0.82)
    logo_x = card_x + card_w - LOGO_SIZE - 20
    logo_y = card_y + (card_h - LOGO_SIZE) // 2
    logo = _load_team_logo_pil(team_code, LOGO_SIZE)
    if logo:
        # Subtle shadow behind logo
        shadow = Image.new("RGBA", (LOGO_SIZE + 20, LOGO_SIZE + 20), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse((0, 0, LOGO_SIZE + 19, LOGO_SIZE + 19), fill=(*primary_rgb, 30))
        img.alpha_composite(shadow, (logo_x - 10, logo_y - 10))
        img.alpha_composite(logo, (logo_x, logo_y))

    # Team name block: abbreviation + full name
    text_max_x = logo_x - 20
    font_code = get_font(56, "heavy")
    team_name = TEAM_NAMES.get(team_code, team_code)
    font_name = get_font(24, "regular")

    font_stat_val = get_font(26, "heavy")
    font_stat_lbl = get_font(16, "regular")

    code_bbox = draw.textbbox((0, 0), team_code, font=font_code)
    name_bbox = draw.textbbox((0, 0), team_name, font=font_name)
    val_bbox  = draw.textbbox((0, 0), "0",       font=font_stat_val)
    lbl_bbox  = draw.textbbox((0, 0), "X",       font=font_stat_lbl)

    # Use y1 (not height) for vertical advance — avoids overlap caused by positive y0 offsets
    GAP_CODE_NAME = 6
    LINE_GAP      = 8
    STAT_GAP      = 10
    GAP_VAL_LBL   = 3

    if stats:
        total_h = (code_bbox[3] + GAP_CODE_NAME +
                   name_bbox[3] + LINE_GAP +
                   2 + STAT_GAP +
                   val_bbox[3] + GAP_VAL_LBL + lbl_bbox[3])
    else:
        total_h = code_bbox[3] + GAP_CODE_NAME + name_bbox[3]

    VERT_PAD = 20
    text_top = center_y - total_h // 2
    text_top = max(card_y + VERT_PAD, min(text_top, card_y + card_h - total_h - VERT_PAD))

    # Draw abbreviation
    draw.text((info_x, text_top), team_code, fill=text_on_card, font=font_code)
    name_y = text_top + code_bbox[3] + GAP_CODE_NAME
    draw.text((info_x, name_y), team_name, fill=text_on_card_2, font=font_name)

    # Tier label badge — top right corner of card
    if tier_label:
        font_tier = get_font(16, "bold")
        tier_bbox = draw.textbbox((0, 0), tier_label, font=font_tier)
        tier_w = tier_bbox[2] - tier_bbox[0]
        badge_pad_x, badge_pad_y = 10, 5
        badge_w = tier_w + badge_pad_x * 2
        badge_h = tier_bbox[3] - tier_bbox[1] + badge_pad_y * 2
        badge_x = card_x + card_w - badge_w - 10
        badge_y = card_y + 10
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
            radius=6, fill=(*hex_to_rgb(primary), 40),
        )
        draw.rounded_rectangle(
            (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
            radius=6, outline=(*hex_to_rgb(primary), 120), width=1,
        )
        draw.text(
            (badge_x + badge_pad_x, badge_y + badge_pad_y - tier_bbox[1]),
            tier_label, fill=(*hex_to_rgb(primary), 220), font=font_tier,
        )

    # Secondary color accent line
    line_y = name_y + name_bbox[3] + LINE_GAP
    draw.line([(info_x, line_y), (info_x + 60, line_y)], fill=secondary, width=2)

    # Season stats block
    if stats:
        net = stats.get("net_rtg", 0)
        net_str = f"+{net}" if net > 0 else str(net)
        net_color = (100, 220, 130) if net > 0 else (220, 100, 100)

        stat_items = [
            (f"{stats['w']}-{stats['l']}", "RECORD", text_on_card),
            (net_str,                       "NET",    net_color),
            (str(stats["off_rtg"]),         "OFF",    text_on_card_2),
            (str(stats["def_rtg"]),         "DEF",    text_on_card_2),
        ]

        stat_x = info_x
        stat_y = line_y + 2 + STAT_GAP
        for val, lbl, color in stat_items:
            draw.text((stat_x, stat_y), val, fill=color, font=font_stat_val)
            draw.text((stat_x, stat_y + val_bbox[3] + GAP_VAL_LBL), lbl, fill=text_on_card_m, font=font_stat_lbl)
            stat_x += 82


def generate_team_card(team_codes: list, title: str = "MY TOP 5 TEAMS", output_path=None, team_stats: dict = None, tier_labels: list = None) -> str:
    teams = team_codes[:5]

    img = Image.new("RGBA", (WIDTH, HEIGHT), (*hex_to_rgb(BG_COLOR), 255))
    draw = ImageDraw.Draw(img)

    # Title — Impact font for impact
    _fonts_dir = Path(__file__).parent.parent / "assets" / "fonts"
    try:
        font_title = ImageFont.truetype(str(_fonts_dir / "Impact.ttf"), 96)
    except Exception:
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 96)
        except Exception:
            font_title = get_font(72, "heavy")
    font_subtitle = get_font(28, "regular")

    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    draw.text(((WIDTH - (title_bbox[2] - title_bbox[0])) // 2, 36), title, fill=TEXT_WHITE, font=font_title)

    subtitle = "TEAM RANKING"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    draw.text(((WIDTH - (sub_bbox[2] - sub_bbox[0])) // 2, 36 + 102), subtitle, fill=GOLD, font=font_subtitle)

    # Decorative line
    line_y = 168
    draw.line([(WIDTH // 2 - 60, line_y), (WIDTH // 2 + 60, line_y)], fill=GOLD, width=1)

    # Team cards
    labels = tier_labels or []
    for i, code in enumerate(teams):
        y = CARD_AREA_TOP + i * (CARD_HEIGHT + CARD_GAP)
        stats = (team_stats or {}).get(code.upper())
        label = labels[i].upper() if i < len(labels) else None
        draw_team_card(img, draw, code.upper(), i + 1, y, stats=stats, tier_label=label)

    # Footer
    font_brand = get_font(16, "bold")
    brand = "RUSHMORE"
    bb = draw.textbbox((0, 0), brand, font=font_brand)
    draw.text(((WIDTH - (bb[2] - bb[0])) // 2, HEIGHT - 52), brand, fill=TEXT_MUTED, font=font_brand)

    if output_path is None:
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"rushmore_teams_{ts}.png"

    img.convert("RGB").save(output_path, "PNG")
    print(f"Team card saved to: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    import sys
    teams = sys.argv[1:6] if len(sys.argv) > 1 else ["LAL", "GSW", "CHI", "BOS", "MIA"]
    generate_team_card(teams)
