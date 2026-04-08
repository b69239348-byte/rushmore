"""
Generate AI card backgrounds using Imagen 4.
Produces 9:16 flat vector illustration backgrounds for the Rushmore card system.
"""

import os
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY") or open(Path(__file__).parent.parent / ".env").read().split("=", 1)[1].strip()
client = genai.Client(api_key=API_KEY)

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "card_backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_STYLE = (
    "flat vector illustration style, clean geometric shapes, "
    "deep navy and purple color palette, cinematic mood, "
    "no text, no watermark, no labels, portrait 9:16 format"
)

BACKGROUNDS = {
    "night_court_outdoor": (
        "Digital art, animated movie style illustration, "
        "basketball court at night under a starry sky, "
        "deep navy and purple tones, glowing teal neon court lines, "
        "mountain silhouettes in background, basketball hoop, "
        "two player silhouettes dunking, crowd silhouettes, "
        "no faces visible, no text, no watermark"
    ),
    "indoor_arena": (
        "Flat vector illustration of an indoor NBA basketball arena at night, "
        "dramatic spotlight beams, hardwood court with glowing purple lines, "
        "crowd silhouettes in stands, deep navy and purple color palette, "
        "player silhouette jumping, no faces, no watermark, no text"
    ),
    "rooftop_city": (
        "Rooftop basketball court in a city at night, "
        "glowing skyline in the background, purple and teal neon lights, "
        "basketball hoop at the edge, player silhouette shooting, "
        + BASE_STYLE
    ),
    "desert_dusk": (
        "Digital art, animated movie style illustration, "
        "basketball court in the desert at dusk, "
        "warm orange and purple gradient sky, cactus silhouettes, "
        "glowing neon court lines, basketball hoop, player silhouette dunking, "
        "no faces visible, no text, no watermark"
    ),
    "underground_court": (
        "Flat vector illustration of an underground basketball court, "
        "industrial concrete setting, purple and teal neon lights on walls, "
        "dramatic shadows, basketball hoop, player silhouette dribbling, "
        "no faces, no watermark, no text"
    ),

    # ── Trophy backgrounds (for Bracket card) ────────────────────────────
    "trophy_jordan": (
        "Flat vector illustration, animated movie style, "
        "solid deep crimson red background, "
        "basketball player silhouette kneeling and crying while holding a championship trophy overhead, "
        "confetti falling around the player, four-pointed sparkle stars scattered in background, "
        "dramatic single spotlight from above, warm gold trophy glow, "
        "no faces visible, no text, no watermark, portrait 9:16"
    ),
    "trophy_celebration": (
        "Flat vector illustration, animated movie style, "
        "solid deep navy blue background, "
        "basketball player silhouette standing tall holding a large championship trophy above head with both arms raised, "
        "gold and white confetti bursting outward from the trophy, "
        "crowd silhouettes cheering in background, four-pointed sparkle stars, "
        "warm golden trophy glow illuminating the scene, "
        "no faces visible, no text, no watermark, portrait 9:16"
    ),
    "trophy_spotlight": (
        "Animated movie style illustration, basketball art, "
        "dark charcoal and black background, "
        "a glowing gold NBA championship trophy standing tall in the center "
        "bathed in a single dramatic cone of golden light from above, "
        "a basketball player silhouette kneeling in awe in front of the trophy, "
        "colorful confetti raining down, four-pointed sparkle glints, "
        "deep shadows frame the edges, warm golden glow radiates from the trophy, "
        "no letters, no words, no text, portrait orientation"
    ),

    # ── Light / bright backgrounds ────────────────────────────────────────
    "sunny_outdoor": (
        "Flat vector illustration, animated movie style, "
        "solid warm cream or soft ivory background, "
        "outdoor basketball court on a bright sunny day, "
        "player silhouette mid-air doing a layup, basketball hoop visible, "
        "long clean shadow on the court, four-pointed sparkle stars in the sky, "
        "warm golden yellow sun high up, minimal geometric clouds, "
        "no faces visible, no text, no watermark, portrait 9:16"
    ),
    "golden_arena": (
        "Digital painting, basketball scene, warm golden afternoon light, "
        "a basketball player silhouette jumping for a dunk inside a large gymnasium, "
        "sunlight pouring through tall windows on the side walls, "
        "golden and amber atmosphere, wooden floor, empty bleachers, "
        "dust particles glowing in the light shafts, "
        "four-pointed light sparkles, warm yellow and orange color palette, "
        "no writing, no letters, no text anywhere, vertical portrait image"
    ),
    "sunset_court": (
        "Flat vector illustration, animated movie style, "
        "solid warm coral or terracotta orange background, "
        "outdoor basketball court at golden hour sunset, "
        "large glowing sun low on the horizon behind the hoop, "
        "player silhouette shooting a jump shot, long shadows on court, "
        "four-pointed sparkle stars scattered across the warm sky, "
        "no faces visible, no text, no watermark, portrait 9:16"
    ),
    "morning_fog": (
        "Flat vector illustration, animated movie style, "
        "solid soft powder blue or pale sky background, "
        "outdoor basketball court in the early morning mist, "
        "soft diffused light, gentle fog rolling across the court, "
        "player silhouette dribbling alone, basketball hoop visible, "
        "four-pointed sparkle stars still faintly visible in the pale sky, "
        "calm serene mood, no faces, no text, no watermark, portrait 9:16"
    ),
}


def generate_background(name: str, prompt: str, overwrite: bool = False) -> Path:
    out_path = OUTPUT_DIR / f"{name}.png"
    if out_path.exists() and not overwrite:
        print(f"  Skipping {name} (already exists)")
        return out_path

    print(f"  Generating: {name}...")
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            output_mime_type="image/png",
        ),
    )
    img = response.generated_images[0]
    out_path.write_bytes(img.image.image_bytes)
    print(f"  Saved: {out_path}")
    return out_path


def generate_all(overwrite: bool = False):
    print(f"Generating {len(BACKGROUNDS)} backgrounds...\n")
    results = {}
    for name, prompt in BACKGROUNDS.items():
        try:
            path = generate_background(name, prompt, overwrite)
            results[name] = str(path)
        except Exception as e:
            print(f"  ERROR on {name}: {e}")
    print(f"\nDone. {len(results)}/{len(BACKGROUNDS)} generated.")
    return results


if __name__ == "__main__":
    import sys
    overwrite = "--overwrite" in sys.argv
    generate_all(overwrite=overwrite)
