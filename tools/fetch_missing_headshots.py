"""
Fetch real headshots for players that only have silhouette placeholders.
Source: Wikipedia/Wikimedia Commons (CC-licensed, free to use).
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

HEADSHOT_DIR = Path(__file__).parent.parent / "assets" / "headshots"
DB_PATH = Path(__file__).parent.parent / "players.json"
SILHOUETTE_SIZE = 12430

HEADERS = {"User-Agent": "Rushmore/1.0 (fan app; headshot fetch)"}


def get_missing_players():
    """Return players with silhouette OR no headshot file at all."""
    with open(DB_PATH) as f:
        players = json.load(f)

    missing = []
    for p in players:
        pid = p["id"]
        files = list(HEADSHOT_DIR.glob(f"{pid}.*"))
        if not files:
            missing.append(p)
        elif any(f.stat().st_size == SILHOUETTE_SIZE for f in files):
            missing.append(p)
    return missing


def fetch_wikipedia_image(name: str):
    """Return direct image URL from Wikipedia for a player name, or None."""
    # Step 1: search Wikipedia for the player
    search_url = (
        "https://en.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(name + ' basketball NBA')}"
        "&srlimit=1&format=json"
    )
    req = urllib.request.Request(search_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("query", {}).get("search", [])
        if not results:
            return None
        title = results[0]["title"]
    except Exception as e:
        print(f"  Search error: {e}")
        return None

    # Step 2: get thumbnail image (not original — avoids Wikimedia rate limits)
    img_url = (
        "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages"
        f"&titles={urllib.parse.quote(title)}&piprop=thumbnail&pithumbsize=500&format=json"
    )
    req = urllib.request.Request(img_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            thumb = page.get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception as e:
        print(f"  Image fetch error: {e}")
    return None


def download_image(url: str, dest: Path) -> bool:
    """Download image to dest. Returns True if successful and non-silhouette."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        if len(data) < 5000:
            return False  # too small, likely not a real photo
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def main():
    players = get_missing_players()
    print(f"Players needing real headshots: {len(players)}\n")

    success, failed = [], []

    for p in players:
        pid = p["id"]
        name = p["name"]
        print(f"[{pid}] {name} ...", end=" ", flush=True)

        img_url = fetch_wikipedia_image(name)
        if not img_url:
            print("❌ no Wikipedia image found")
            failed.append(name)
            time.sleep(1.5)
            continue

        # Determine extension from URL
        ext = "jpg"
        url_lower = img_url.lower()
        if ".png" in url_lower:
            ext = "png"
        elif ".gif" in url_lower:
            print("❌ GIF skipped")
            failed.append(name)
            time.sleep(1.5)
            continue

        dest = HEADSHOT_DIR / f"{pid}.{ext}"
        # Remove old silhouette if present
        for old in HEADSHOT_DIR.glob(f"{pid}.*"):
            if old.stat().st_size == SILHOUETTE_SIZE:
                old.unlink()

        if download_image(img_url, dest):
            size = dest.stat().st_size
            print(f"✅ {size // 1024}KB")
            success.append(name)
        else:
            print("❌ download failed or too small")
            failed.append(name)

        time.sleep(1.5)  # polite rate limiting

    print(f"\n✅ Success: {len(success)}")
    print(f"❌ Failed:  {len(failed)}")
    if failed:
        print("\nStill missing:")
        for n in failed:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
