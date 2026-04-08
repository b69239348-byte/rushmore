"""Quick smoke test — run after rewriting generate_card.py"""
import tempfile, os
from pathlib import Path
from generate_card import generate_card

with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    out = tmp.name

# Use real player IDs from players.json
generate_card(
    queries=["203999", "1629029", "1629627", "1629029", "203507"],
    title="MY TOP 5",
    subtitle="ALL-TIME GREATS",
    output_path=out,
)

from PIL import Image
img = Image.open(out)
assert img.size == (1080, 1920), f"Wrong size: {img.size}"
assert img.mode in ("RGB", "RGBA"), f"Wrong mode: {img.mode}"
print(f"✓ Card generated: {img.size}, {img.mode}, {os.path.getsize(out)//1024}KB → {out}")
