"""
Generate the Mount Rushmore hero image with NBA legend headshots.
Creates a mountain-like composition with 4 player portraits.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ASSETS_DIR = Path(__file__).parent.parent / "assets"
HEADSHOTS_DIR = ASSETS_DIR / "headshots"
OUTPUT_PATH = Path(__file__).parent.parent / "web" / "public" / "hero.png"

# The 4 GOATs for the mountain
PLAYER_IDS = [893, 2544, 76003, 77142]  # Jordan, LeBron, Kareem, Magic

WIDTH = 1200
HEIGHT = 600


def generate_hero():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Create canvas with dark gradient background
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (8, 8, 13, 255))
    draw = ImageDraw.Draw(canvas)

    # Draw subtle mountain silhouette shape in background
    mountain_color = (22, 22, 31, 255)
    # Main mountain
    draw.polygon(
        [(0, HEIGHT), (200, 200), (400, 280), (600, 150), (800, 250), (1000, 180), (WIDTH, HEIGHT)],
        fill=mountain_color,
    )
    # Foreground ridge
    ridge_color = (17, 17, 24, 255)
    draw.polygon(
        [(0, HEIGHT), (150, 350), (350, 300), (500, 380), (700, 320), (900, 360), (1100, 310), (WIDTH, HEIGHT)],
        fill=ridge_color,
    )

    # Place headshots as "carved" portraits
    head_size = 220
    positions = [
        (100, 160),   # Kareem (left)
        (340, 120),   # Jordan (center-left)
        (580, 140),   # LeBron (center-right)
        (820, 170),   # Magic (right)
    ]
    order = [76003, 893, 2544, 77142]  # Kareem, Jordan, LeBron, Magic

    for pid, (x, y) in zip(order, positions):
        headshot_path = HEADSHOTS_DIR / f"{pid}.png"
        if not headshot_path.exists():
            print(f"  Headshot not found: {pid}")
            continue

        head = Image.open(headshot_path).convert("RGBA")

        # Crop to face area (center portion of the headshot)
        w, h = head.size
        crop_size = min(w, h) * 0.75
        cx, cy = w // 2, h * 0.38  # slightly above center for face
        left = int(cx - crop_size / 2)
        top = int(cy - crop_size / 2)
        right = int(cx + crop_size / 2)
        bottom = int(cy + crop_size / 2)
        head = head.crop((max(0, left), max(0, top), min(w, right), min(h, bottom)))

        # Resize
        head = head.resize((head_size, head_size), Image.LANCZOS)

        # Apply golden/bronze tint for "carved in stone" effect
        stone = Image.new("RGBA", head.size, (180, 160, 100, 60))
        head = Image.alpha_composite(head, stone)

        # Desaturate partially
        enhancer = ImageEnhance.Color(head)
        head = enhancer.enhance(0.3)

        # Darken slightly
        enhancer = ImageEnhance.Brightness(head)
        head = enhancer.enhance(0.7)

        # Create circular mask with soft edges
        mask = Image.new("L", (head_size, head_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, head_size, head_size), fill=255)
        # Blur for soft edges
        mask = mask.filter(ImageFilter.GaussianBlur(radius=8))

        # Paste onto canvas
        canvas.paste(head, (x, y), mask)

    # Add gold accent line at the bottom
    gold_color = (201, 168, 76, 80)
    draw = ImageDraw.Draw(canvas)
    draw.line([(0, HEIGHT - 2), (WIDTH, HEIGHT - 2)], fill=gold_color, width=2)

    # Add subtle vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for i in range(80):
        alpha = int(i * 2.5)
        v_draw.rectangle(
            [i, i, WIDTH - i, HEIGHT - i],
            outline=(8, 8, 13, alpha),
        )
    canvas = Image.alpha_composite(canvas, vignette)

    # Save
    canvas.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"Hero image saved: {OUTPUT_PATH}")
    print(f"Size: {OUTPUT_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    generate_hero()
