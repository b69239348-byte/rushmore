"""
Rushmore — Debate / List Card Generator

Renders any 5-item ranked list as a shareable card.
Used for debate, funny, and historical content from the calendar YAML.

Usage:
    python3 tools/generate_debate_card.py \
        --title "Regular Season Frauds" \
        --subtitle "Hot Take" \
        --items "Luka Doncic,Zion Williamson,James Harden,Russell Westbrook,Ben Simmons"
    python3 tools/generate_debate_card.py ... --feed   # 1080x1080
    python3 tools/generate_debate_card.py ... --output output/my_card.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))

from generate_card import (  # noqa: E402
    _font, _font_impact,
    _load_background,
    TEAL, WHITE, GRAY, ROW_BG, ROW_BG_1, PAD,
    WIDTH, HEIGHT, TITLE_H, FOOTER_H, ROW_COUNT, ROW_H, ROW_GAP,
)

_FORMATS = {"story": HEIGHT, "feed": 1080}


def _truncate(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> str:
    """Shorten text with '...' until it fits within max_w pixels."""
    bbox = draw.textbbox((0, 0), text, font=font)
    if (bbox[2] - bbox[0]) <= max_w:
        return text
    while len(text) > 1:
        text = text[:-1].rstrip()
        candidate = text + "..."
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return candidate
    return "..."


def generate_debate_card(
    title: str,
    subtitle: str,
    items: list[str],
    output_path: str = "output/debate_card.png",
    card_format: str = "story",
) -> str:
    """
    Render a 5-item debate/list card.

    Args:
        title:       Bold headline (Impact font), e.g. "Regular Season Frauds"
        subtitle:    Teal sub-label, e.g. "Hot Take"
        items:       Exactly 5 strings, ranked #1 → #5
        output_path: Destination PNG path
        card_format: "story" (1080×1920) or "feed" (1080×1080)

    Returns:
        Absolute path to the saved PNG.
    """
    if len(items) != 5:
        raise ValueError(f"Expected exactly 5 items, got {len(items)}")

    canvas_h = _FORMATS.get(card_format, HEIGHT)
    _scale    = canvas_h / HEIGHT

    # Feed mode: add vertical inset to keep content centred in square canvas
    _v_inset  = 80 if card_format == "feed" else 0

    _title_h  = int(TITLE_H * _scale)
    _footer_h = int(FOOTER_H * _scale)
    _row_gap  = max(4, int(ROW_GAP * _scale))
    _row_area = canvas_h - _v_inset * 2 - _title_h - _footer_h
    _row_h    = _row_area // ROW_COUNT

    # ── Canvas ──────────────────────────────────────────────────────────────────
    canvas = _load_background("underground_court", height=canvas_h).convert("RGBA")

    # Dark overlay for readability
    overlay = Image.new("RGBA", (WIDTH, canvas_h), (0, 0, 0, 130))
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

    # ── Fonts ────────────────────────────────────────────────────────────────────
    title_font = _font_impact(max(54, int(88 * _scale)))
    sub_font   = _font(max(18, int(30 * _scale)))

    # ── Title block ──────────────────────────────────────────────────────────────
    # Teal accent bar on left edge
    bar_h   = int(_title_h * 0.70)
    bar_w   = 6
    bar_y0  = _v_inset + (_title_h - bar_h) // 2
    bar_layer = Image.new("RGBA", (bar_w, bar_h), (*TEAL, 230))
    canvas.alpha_composite(bar_layer, (PAD, bar_y0))

    draw = ImageDraw.Draw(canvas)

    # Measure title and subtitle
    title_text = title.upper()
    sub_text   = subtitle.upper()

    t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    t_w    = t_bbox[2] - t_bbox[0]
    t_h    = t_bbox[3] - t_bbox[1]

    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    s_h    = s_bbox[3] - s_bbox[1]

    # Truncate if title overflows canvas width
    max_title_w = WIDTH - PAD * 2 - bar_w - 16
    if t_w > max_title_w:
        title_text = _truncate(draw, title_text, title_font, max_title_w)
        t_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        t_w    = t_bbox[2] - t_bbox[0]
        t_h    = t_bbox[3] - t_bbox[1]

    # Vertical centering of title + subtitle block within title area
    gap          = 10
    block_h      = t_h + gap + s_h
    block_y      = _v_inset + (_title_h - block_h) // 2
    text_x_start = PAD + bar_w + 16

    # Title
    title_y = block_y - t_bbox[1]   # compensate for ascender offset
    draw.text((text_x_start, title_y), title_text, fill=WHITE, font=title_font)

    # Subtitle (teal)
    sub_y = block_y + t_h + gap
    draw.text((text_x_start, sub_y), sub_text, fill=(*TEAL, 220), font=sub_font)

    # Thin teal divider under title block
    div_y = _v_inset + _title_h - 8
    draw.rectangle([PAD, div_y, WIDTH - PAD, div_y + 2], fill=(*TEAL, 60))

    # ── Row fonts ────────────────────────────────────────────────────────────────
    rank_font = _font_impact(max(48, int(90 * _scale)))
    item_font = _font(max(22, int(40 * _scale)), bold=True)

    RANK_W    = max(80, int(120 * _scale))   # width reserved for rank number column
    INNER_PAD = 8                             # min gap between text and row edges

    # ── Player / item rows ───────────────────────────────────────────────────────
    for i, item_text in enumerate(items):
        row_y = _v_inset + _title_h + i * _row_h + _row_gap // 2
        row_h = _row_h - _row_gap
        is_top = i == 0

        # Semi-transparent row panel
        panel = Image.new("RGBA", (WIDTH - PAD * 2, row_h), ROW_BG_1 if is_top else ROW_BG)
        canvas.alpha_composite(panel, (PAD, row_y))

        # Left accent bar (full-height, more opaque for rank-1)
        bar_alpha = 255 if is_top else 140
        accent = Image.new("RGBA", (5, row_h), (*TEAL, bar_alpha))
        canvas.alpha_composite(accent, (PAD, row_y))

        draw = ImageDraw.Draw(canvas)

        # ── Rank number ──
        rank_str   = str(i + 1)
        rank_color = TEAL if is_top else (160, 160, 160)

        r_bbox = draw.textbbox((0, 0), rank_str, font=rank_font)
        r_w    = r_bbox[2] - r_bbox[0]
        r_h    = r_bbox[3] - r_bbox[1]

        # Centre rank vertically; offset for ascender
        r_x = PAD + 5 + (RANK_W - r_w) // 2
        r_y = row_y + (row_h - r_h) // 2 - r_bbox[1]
        draw.text((r_x, r_y), rank_str, fill=rank_color, font=rank_font)

        # ── Item text ──
        item_x     = PAD + RANK_W
        # 90 % of available width, with min 8px gap on each side
        item_max_w = int((WIDTH - PAD - item_x - INNER_PAD) * 0.90)

        display = _truncate(draw, item_text, item_font, item_max_w)

        i_bbox = draw.textbbox((0, 0), display, font=item_font)
        i_h    = i_bbox[3] - i_bbox[1]

        # Centre text vertically in row, compensate for ascender offset
        i_y = row_y + (row_h - i_h) // 2 - i_bbox[1]

        fill_color = WHITE if is_top else (220, 220, 220)
        draw.text((item_x, i_y), display, fill=fill_color, font=item_font)

    # ── Footer ───────────────────────────────────────────────────────────────────
    footer_font = _font(max(16, int(28 * _scale)), bold=True)
    footer_text = "rushmore.cards"

    draw    = ImageDraw.Draw(canvas)
    f_bbox  = draw.textbbox((0, 0), footer_text, font=footer_font)
    f_w     = f_bbox[2] - f_bbox[0]
    f_h     = f_bbox[3] - f_bbox[1]

    footer_y = canvas_h - _v_inset - _footer_h
    f_x = (WIDTH - f_w) // 2
    f_y = footer_y + (_footer_h - f_h) // 2 - f_bbox[1]
    draw.text((f_x, f_y), footer_text, fill=GRAY, font=footer_font)

    # ── Save ─────────────────────────────────────────────────────────────────────
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(str(out), "PNG", optimize=True)
    print(f"Card saved: {out}")
    return str(out)


# ── CLI ──────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a Rushmore debate/list card.")
    p.add_argument("--title",    required=True, help="Card headline")
    p.add_argument("--subtitle", required=True, help="Teal sub-label below title")
    p.add_argument(
        "--items", required=True,
        help="Comma-separated list of exactly 5 items (ranked #1 → #5)",
    )
    p.add_argument("--feed",   action="store_true", help="Render as 1080x1080 feed card")
    p.add_argument("--output", default=None,         help="Output PNG path")
    return p.parse_args()


def main():
    args = _parse_args()
    items = [s.strip() for s in args.items.split(",")]
    fmt   = "feed" if args.feed else "story"

    if args.output:
        output_path = args.output
    else:
        output_path = f"output/debate_card_{fmt}.png"

    generate_debate_card(
        title=args.title,
        subtitle=args.subtitle,
        items=items,
        output_path=output_path,
        card_format=fmt,
    )


if __name__ == "__main__":
    main()
