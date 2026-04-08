"""
Generate a 1920x1080 playoff bracket card image using PIL.
West left, East right, Finals center.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
BG_DIR   = Path(__file__).parent.parent / "assets" / "card_backgrounds"
LOGO_DIR = Path(__file__).parent.parent / "assets" / "team_logos"

DARK   = (7, 11, 20)
GOLD   = (201, 168, 76)
WHITE  = (235, 235, 240)
GRAY   = (120, 120, 135)
SLOT_FILL = (18, 24, 42, 210)


def _font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf" if bold
            else "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _load_logo(code: str, size: int) -> Image.Image | None:
    if not code:
        return None
    path = LOGO_DIR / f"{code.upper()}.png"
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    if img.width != img.height:
        d = max(img.width, img.height)
        sq = Image.new("RGBA", (d, d), (0, 0, 0, 0))
        sq.paste(img, ((d - img.width) // 2, (d - img.height) // 2))
        img = sq
    return img.resize((size, size), Image.LANCZOS)


def _draw_slot(canvas: Image.Image, x: int, y: int, w: int, h: int, code: str | None):
    """Draw one team slot (pill with logo + abbreviation)."""
    # Background
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=SLOT_FILL)
    canvas.alpha_composite(pill, (x, y))

    draw = ImageDraw.Draw(canvas)
    if not code:
        draw.text((x + 12, y + h // 2 - 8), "?", fill=GRAY, font=_font(16))
        return

    logo_size = h - 10
    logo = _load_logo(code, logo_size)
    if logo:
        canvas.alpha_composite(logo, (x + 5, y + 5))

    draw.text(
        (x + logo_size + 10, y + h // 2 - 9),
        code.upper(),
        fill=WHITE,
        font=_font(18, bold=True),
    )


def _draw_connector(draw: ImageDraw.ImageDraw, x1: int, y_top: int, y_bot: int, right: bool):
    """L-shaped connector between two slots and the next round."""
    mid_y = (y_top + y_bot) // 2
    step = 20
    color = (*GRAY, 90)
    if right:
        draw.line([(x1, y_top), (x1 + step, y_top)], fill=color, width=1)
        draw.line([(x1, y_bot), (x1 + step, y_bot)], fill=color, width=1)
        draw.line([(x1 + step, y_top), (x1 + step, y_bot)], fill=color, width=1)
        draw.line([(x1 + step, mid_y), (x1 + step * 2, mid_y)], fill=color, width=1)
    else:
        draw.line([(x1, y_top), (x1 - step, y_top)], fill=color, width=1)
        draw.line([(x1, y_bot), (x1 - step, y_bot)], fill=color, width=1)
        draw.line([(x1 - step, y_top), (x1 - step, y_bot)], fill=color, width=1)
        draw.line([(x1 - step, mid_y), (x1 - step * 2, mid_y)], fill=color, width=1)


def generate_bracket_card(
    slots: list,          # 31 items: [W-R1×8, W-Semis×4, W-Finals×2, Finals×2, E-Finals×2, E-Semis×4, E-R1×8] + champion
    title: str = "MY PLAYOFF BRACKET",
    output_path: str = "bracket.png",
    background: str = "trophy_celebration",
) -> str:
    # ── Background ──────────────────────────────────────────────────────────────
    bg_path = BG_DIR / f"{background}.png"
    if bg_path.exists():
        canvas = Image.open(bg_path).convert("RGBA")
        # scale to fill 1920x1080
        r = max(WIDTH / canvas.width, HEIGHT / canvas.height)
        canvas = canvas.resize((int(canvas.width * r), int(canvas.height * r)), Image.LANCZOS)
        left = (canvas.width - WIDTH) // 2
        top  = (canvas.height - HEIGHT) // 2
        canvas = canvas.crop((left, top, left + WIDTH, top + HEIGHT))
    else:
        canvas = Image.new("RGBA", (WIDTH, HEIGHT), (*DARK, 255))

    # Dark overlay
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (*DARK, 195))
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    # ── Title ───────────────────────────────────────────────────────────────────
    title_font = _font(56, bold=True)
    tb = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((WIDTH - (tb[2] - tb[0])) // 2, 18), title, fill=WHITE, font=title_font)

    sub_font = _font(20)
    sub = "▲ RUSHMORE"
    sb = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((WIDTH - (sb[2] - sb[0])) // 2, 80), sub, fill=(*GOLD, 160), font=sub_font)

    # ── Layout constants ─────────────────────────────────────────────────────────
    TOP      = 115
    BOTTOM   = HEIGHT - 30
    CONTENT  = BOTTOM - TOP          # 935px

    SW, SH   = 130, 36               # slot width / height
    COL_GAP  = 48                    # gap between round columns
    PAIR_GAP = 10                    # gap between the two slots of a matchup

    # Column x positions (West side, left-to-right)
    # R1=4 pairs, Semis=2, Finals=1, [center], EFinals=1, ESemis=2, ER1=4
    W_R1_X      = 30
    W_SEM_X     = W_R1_X + SW + COL_GAP
    W_FIN_X     = W_SEM_X + SW + COL_GAP
    CENTER_X    = (WIDTH - SW) // 2
    E_FIN_X     = WIDTH - W_FIN_X - SW
    E_SEM_X     = WIDTH - W_SEM_X - SW
    E_R1_X      = WIDTH - W_R1_X - SW

    # Slot index mapping (matches frontend slots array):
    # 0-7: W R1 (pairs: 0-1, 2-3, 4-5, 6-7)
    # 8-11: W Semis (pairs: 8-9, 10-11)
    # 12-13: W Finals
    # 14-15: Finals (champion box)
    # 16-17: E Finals
    # 18-21: E Semis
    # 22-29: E R1
    # 30: Champion

    def s(i: int) -> str | None:
        return slots[i] if i < len(slots) else None

    def pair_ys(n_pairs: int, pair_idx: int) -> tuple[int, int]:
        """Return y positions for top and bottom slot of a matchup."""
        slot_total = SH * 2 + PAIR_GAP
        section    = CONTENT // n_pairs
        base_y     = TOP + section * pair_idx + (section - slot_total) // 2
        return base_y, base_y + SH + PAIR_GAP

    def draw_pair(x: int, n_pairs: int, pair_idx: int, slot_a: int, slot_b: int, connector_right: bool | None = None):
        ya, yb = pair_ys(n_pairs, pair_idx)
        _draw_slot(canvas, x, ya, SW, SH, s(slot_a))
        _draw_slot(canvas, x, yb, SW, SH, s(slot_b))
        if connector_right is not None:
            cx = x + SW if connector_right else x
            _draw_connector(draw, cx, ya + SH // 2, yb + SH // 2, connector_right)

    # ── West R1 ─────────────────────────────────────────────────────────────────
    for i in range(4):
        draw_pair(W_R1_X, 4, i, i * 2, i * 2 + 1, connector_right=True)

    # ── West Semis ───────────────────────────────────────────────────────────────
    for i in range(2):
        draw_pair(W_SEM_X, 2, i, 8 + i * 2, 8 + i * 2 + 1, connector_right=True)

    # ── West Finals ──────────────────────────────────────────────────────────────
    draw_pair(W_FIN_X, 1, 0, 12, 13, connector_right=True)

    # ── Finals center ────────────────────────────────────────────────────────────
    cy1, cy2 = pair_ys(1, 0)
    _draw_slot(canvas, CENTER_X, cy1, SW, SH, s(14))
    _draw_slot(canvas, CENTER_X, cy2, SW, SH, s(15))
    # Gold border
    draw.rounded_rectangle(
        (CENTER_X - 4, cy1 - 6, CENTER_X + SW + 4, cy2 + SH + 6),
        radius=10, outline=(*GOLD, 180), width=2,
    )
    lf = _font(10)
    draw.text((CENTER_X, cy1 - 18), "THE FINALS", fill=GOLD, font=lf)

    # ── East Finals ──────────────────────────────────────────────────────────────
    draw_pair(E_FIN_X, 1, 0, 16, 17, connector_right=False)

    # ── East Semis ───────────────────────────────────────────────────────────────
    for i in range(2):
        draw_pair(E_SEM_X, 2, i, 18 + i * 2, 18 + i * 2 + 1, connector_right=False)

    # ── East R1 ──────────────────────────────────────────────────────────────────
    for i in range(4):
        draw_pair(E_R1_X, 4, i, 22 + i * 2, 22 + i * 2 + 1, connector_right=False)

    # ── Column labels ────────────────────────────────────────────────────────────
    lf2 = _font(11)
    labels = [
        (W_R1_X  + SW // 2, "ROUND 1"),
        (W_SEM_X + SW // 2, "CONF. SEMIS"),
        (W_FIN_X + SW // 2, "CONF. FINALS"),
        (E_FIN_X + SW // 2, "CONF. FINALS"),
        (E_SEM_X + SW // 2, "CONF. SEMIS"),
        (E_R1_X  + SW // 2, "ROUND 1"),
    ]
    for lx, lt in labels:
        lb = draw.textbbox((0, 0), lt, font=lf2)
        draw.text((lx - (lb[2] - lb[0]) // 2, TOP - 18), lt, fill=(*GRAY, 160), font=lf2)

    conf_font = _font(12)
    draw.text((W_R1_X, TOP - 34), "WESTERN CONFERENCE", fill=(*GRAY, 200), font=conf_font)
    rb = draw.textbbox((0, 0), "EASTERN CONFERENCE", font=conf_font)
    draw.text((WIDTH - E_R1_X - SW - (rb[2] - rb[0]) + SW, TOP - 34), "EASTERN CONFERENCE", fill=(*GRAY, 200), font=conf_font)

    canvas.convert("RGB").save(output_path, "PNG", optimize=True)
    return output_path
