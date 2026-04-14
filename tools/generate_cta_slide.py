"""
CTA Slide Generator — 9:16 (1080x1920)

Generates a promotional end-slide for Instagram/TikTok carousels.
Background: karte_1.PNG — dark overlay — Rushmore logo — CTA text.

Usage:
    python3 tools/generate_cta_slide.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT      = Path(__file__).parent.parent
ASSETS    = ROOT / "assets"
FONTS_DIR = ASSETS / "fonts"
OUTPUT    = ROOT / "output"

WIDTH, HEIGHT = 1080, 1920
TEAL  = (76, 201, 240)
WHITE = (255, 255, 255)


# ── Fonts ──────────────────────────────────────────────────────────────────────

def _font_impact(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        str(FONTS_DIR / "Impact.ttf"),
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return _font_helvetica(size, bold=True)


def _font_helvetica(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        str(FONTS_DIR / "Helvetica.ttc"),
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _centered_x(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return (WIDTH - (bbox[2] - bbox[0])) // 2


def generate_cta_slide(output_path: str = "output/cta_slide.png") -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # ── Background ──────────────────────────────────────────────────────────────
    bg_path = ASSETS / "card_backgrounds" / "karte_1.PNG"
    bg = Image.open(bg_path).convert("RGBA")
    # Crop/resize to exact canvas if needed
    bg = bg.resize((WIDTH, HEIGHT), Image.LANCZOS)
    canvas = bg.copy()

    # ── Dark overlay — heavier on top third (text zone), lighter bottom ────────
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    # Top third: solid dark so text is readable over sky
    text_zone_end = int(HEIGHT * 0.58)
    for i in range(text_zone_end):
        t = i / text_zone_end
        # Fade from 200 at top to 120 at bottom of text zone
        alpha = int(200 - 80 * t)
        draw_ov.rectangle([0, i, WIDTH, i + 1], fill=(4, 8, 18, alpha))

    # Bottom 42%: gentle dark-to-clear (preserve the action scene)
    for i in range(text_zone_end, HEIGHT):
        t = (i - text_zone_end) / (HEIGHT - text_zone_end)
        alpha = int(120 - 80 * t)
        draw_ov.rectangle([0, i, WIDTH, i + 1], fill=(4, 8, 18, alpha))

    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # ── Logo — upper area ────────────────────────────────────────────────────────
    logo_path = ASSETS / "rushmore_logo_social.png"
    logo = Image.open(logo_path).convert("RGBA")
    logo_size = 220
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
    logo_x = (WIDTH - logo_size) // 2
    logo_y = int(HEIGHT * 0.08)
    canvas.alpha_composite(logo, (logo_x, logo_y))

    # ── Main Headline ───────────────────────────────────────────────────────────
    f_headline = _font_impact(148)
    headline   = "MAKE YOURS."
    hx = _centered_x(draw, headline, f_headline)
    hy = logo_y + logo_size + 52
    draw.text((hx + 3, hy + 3), headline, font=f_headline, fill=(0, 0, 0, 160))
    draw.text((hx, hy), headline, font=f_headline, fill=WHITE)

    # ── URL in Teal ─────────────────────────────────────────────────────────────
    f_url = _font_impact(108)
    url   = "rushmore.cards"
    ux = _centered_x(draw, url, f_url)
    uy = hy + 166
    draw.text((ux + 2, uy + 2), url, font=f_url, fill=(0, 0, 0, 140))
    draw.text((ux, uy), url, font=f_url, fill=TEAL)

    # ── Teal separator line ─────────────────────────────────────────────────────
    line_y = uy + 130
    line_w = 180
    draw.rectangle(
        [(WIDTH // 2 - line_w // 2, line_y), (WIDTH // 2 + line_w // 2, line_y + 3)],
        fill=(*TEAL, 180),
    )

    # ── Sub-tagline ─────────────────────────────────────────────────────────────
    f_sub  = _font_helvetica(44, bold=False)
    subtext = "Rankings · Season Cards · Your Call"
    sx = _centered_x(draw, subtext, f_sub)
    sy = line_y + 24
    draw.text((sx, sy), subtext, font=f_sub, fill=(180, 210, 235, 210))

    # ── Save ────────────────────────────────────────────────────────────────────
    final = canvas.convert("RGB")
    final.save(str(out), quality=95)
    print(f"Saved: {out}")
    return str(out)


if __name__ == "__main__":
    generate_cta_slide()
