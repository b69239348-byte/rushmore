"""
Generate player silhouettes using Gemini image generation.
Creates a black silhouette for each player in the database.
Output: assets/silhouettes/{player_id}.png
"""

import json
import time
import sys
from pathlib import Path
from PIL import Image, ImageOps
import io

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash-image"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "silhouettes"
DB_PATH = Path(__file__).parent.parent / "players.json"
REQUEST_DELAY = 4  # seconds between API calls to stay within rate limits

# Signature poses for well-known players
SIGNATURE_POSES = {
    "Michael Jordan": "fadeaway jump shot with tongue out",
    "LeBron James": "powerful two-handed dunk",
    "Kobe Bryant": "fadeaway jump shot leaning back",
    "Kareem Abdul-Jabbar": "sky hook shot with one arm extended high",
    "Magic Johnson": "no-look pass",
    "Larry Bird": "shooting a three-pointer",
    "Shaquille O'Neal": "powerful one-handed dunk",
    "Tim Duncan": "bank shot mid-range jumper",
    "Stephen Curry": "shooting a deep three-pointer with follow-through",
    "Kevin Durant": "pull-up jump shot over defender",
    "Hakeem Olajuwon": "dream shake post move",
    "Wilt Chamberlain": "finger roll layup reaching very high",
    "Bill Russell": "blocking a shot with one hand",
    "Julius Erving": "soaring through the air for a dunk from the free throw line",
    "Oscar Robertson": "driving to the basket with the ball",
    "Karl Malone": "posting up with power",
    "Charles Barkley": "rebounding with elbows out",
    "Allen Iverson": "crossover dribble low to the ground",
    "Dirk Nowitzki": "one-legged fadeaway shot",
    "Dwyane Wade": "eurostep layup",
    "Kevin Garnett": "intense fist pump celebration",
    "Patrick Ewing": "turnaround jump shot in the post",
    "David Robinson": "running the fast break",
    "Isiah Thomas": "driving layup through traffic",
    "John Stockton": "throwing a bounce pass",
    "Dennis Rodman": "diving for a loose ball",
    "Scottie Pippen": "fast break dunk",
    "Gary Payton": "defensive stance guarding",
    "James Harden": "step-back three-pointer",
    "Russell Westbrook": "explosive dunk in transition",
    "Giannis Antetokounmpo": "eurostep dunk with long stride",
    "Kawhi Leonard": "mid-range pull-up jumper",
    "Nikola Jokić": "no-look pass from the post",
    "Luka Dončić": "step-back three-pointer",
    "Jayson Tatum": "pulling up for a jump shot",
    "Joel Embiid": "post fadeaway",
    "Chris Paul": "mid-range floater",
    "Carmelo Anthony": "jab step jump shot",
    "Paul Pierce": "step-back jumper",
    "Ray Allen": "catch and shoot three-pointer",
    "Vince Carter": "windmill dunk",
    "Tracy McGrady": "one-legged fadeaway",
    "Steve Nash": "running the pick and roll with the ball",
    "Jason Kidd": "throwing a full-court pass",
    "Pete Maravich": "behind-the-back pass",
    "Walt Frazier": "smooth pull-up jumper",
    "Ben Wallace": "shot block rejection",
    "Dikembe Mutombo": "finger wag after blocking a shot",
    "Tony Parker": "teardrop floater in the lane",
    "Manu Ginobili": "eurostep layup",
}


def get_prompt(player_name, position=""):
    """Build the image generation prompt for a player."""
    if player_name in SIGNATURE_POSES:
        pose = SIGNATURE_POSES[player_name]
    else:
        # Generic pose based on position
        pose_map = {
            "Guard": "dribbling the basketball in a crossover move",
            "Forward": "shooting a jump shot",
            "Center": "going up for a dunk",
            "Forward-Guard": "driving to the basket",
            "Guard-Forward": "pulling up for a jump shot",
            "Forward-Center": "posting up with the ball",
            "Center-Forward": "going up for a hook shot",
        }
        pose = pose_map.get(position, "playing basketball in an athletic stance")

    return (
        f"Generate a solid black silhouette of a basketball player {pose}. "
        f"The silhouette should be completely filled in black with no internal details. "
        f"Plain white background. No text, no shadows, no other elements. "
        f"Only the player figure — no basketball hoop, no backboard, no court, no other objects. "
        f"The figure should be centered and fill most of the frame. "
        f"Clean minimal vector-style silhouette."
    )


def process_silhouette(image_data):
    """Process the generated image: ensure clean black silhouette on transparent bg."""
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")

    # Make white pixels transparent
    data = img.getdata()
    new_data = []
    for r, g, b, a in data:
        # If pixel is close to white, make it transparent
        if r > 200 and g > 200 and b > 200:
            new_data.append((0, 0, 0, 0))
        else:
            # Make dark pixels fully black
            new_data.append((0, 0, 0, 255))

    img.putdata(new_data)
    return img


def generate_silhouette(client, player, output_path):
    """Generate a single silhouette and save it."""
    prompt = get_prompt(player["name"], player.get("position", ""))

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            img = process_silhouette(part.inline_data.data)
            img.save(str(output_path), "PNG")
            return True

    return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(DB_PATH, "r", encoding="utf-8") as f:
        players = json.load(f)

    # Check which silhouettes already exist
    existing = {int(p.stem) for p in OUTPUT_DIR.glob("*.png")}
    to_generate = [p for p in players if p["id"] not in existing]

    # Optional: limit to top N players
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(to_generate)
    to_generate = to_generate[:limit]

    print(f"Generating silhouettes: {len(to_generate)} players ({len(existing)} already exist)")

    client = genai.Client(api_key=API_KEY)
    success = 0
    errors = []

    for i, player in enumerate(to_generate, 1):
        output_path = OUTPUT_DIR / f"{player['id']}.png"
        print(f"  [{i}/{len(to_generate)}] {player['name']}...", end=" ", flush=True)

        try:
            ok = generate_silhouette(client, player, output_path)
            if ok:
                print("OK")
                success += 1
            else:
                print("NO IMAGE")
                errors.append(player["name"])
        except Exception as e:
            err_msg = str(e)[:80]
            print(f"ERROR: {err_msg}")
            errors.append(player["name"])
            time.sleep(5)  # extra delay on error

        time.sleep(REQUEST_DELAY)

    print(f"\nDone! Generated {success}/{len(to_generate)} silhouettes.")
    if errors:
        print(f"Errors ({len(errors)}): {', '.join(errors[:10])}")


if __name__ == "__main__":
    main()
