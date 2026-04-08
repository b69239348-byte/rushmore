"""
Download NBA player headshots from the official CDN.
Caches locally in assets/headshots/{player_id}.png.
Skips players that already have a headshot downloaded.
"""

import json
import time
import sys
from pathlib import Path
import urllib.request
import urllib.error

DB_PATH = Path(__file__).parent.parent / "players.json"
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "headshots"
CDN_URL = "https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
REQUEST_DELAY = 0.3  # seconds between requests to be polite


def download_by_ids(player_ids, names=None):
    """Download headshots for a list of player IDs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = {int(p.stem) for p in OUTPUT_DIR.glob("*.png")}
    to_download = [pid for pid in player_ids if pid not in existing]

    if not to_download:
        print("All headshots already cached.")
        return 0, []

    print(f"Downloading headshots: {len(to_download)} players ({len(existing)} already cached)")
    names = names or {}
    success = 0
    missing = []

    for i, pid in enumerate(to_download, 1):
        url = CDN_URL.format(player_id=pid)
        out_path = OUTPUT_DIR / f"{pid}.png"
        label = names.get(pid, str(pid))
        print(f"  [{i}/{len(to_download)}] {label}...", end=" ", flush=True)

        try:
            urllib.request.urlretrieve(url, out_path)
            size = out_path.stat().st_size
            if size < 1000:
                out_path.unlink()
                print(f"SKIP (placeholder, {size}B)")
                missing.append(label)
            else:
                print("OK")
                success += 1
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}")
            missing.append(label)
        except Exception as e:
            print(f"ERROR: {str(e)[:60]}")
            missing.append(label)

        time.sleep(REQUEST_DELAY)

    print(f"\nDone! Downloaded {success}/{len(to_download)} headshots.")
    if missing:
        print(f"Missing ({len(missing)}): {', '.join(missing[:20])}")
    return success, missing


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Mode: --live downloads headshots for current season leaders not in players.json
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        from live_data import fetch_season_leaders
        leaders = fetch_season_leaders(limit=50)
        with open(DB_PATH, "r", encoding="utf-8") as f:
            existing_db_ids = {p["id"] for p in json.load(f)}
        new_ids = [p["id"] for p in leaders if p["id"] not in existing_db_ids]
        names = {p["id"]: p["name"] for p in leaders}
        print(f"Live mode: {len(new_ids)} players not in players.json")
        download_by_ids(new_ids, names)
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        players = json.load(f)

    # Skip already downloaded
    existing = {int(p.stem) for p in OUTPUT_DIR.glob("*.png")}
    to_download = [p for p in players if p["id"] not in existing]

    # Optional limit
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(to_download)
    to_download = to_download[:limit]

    print(f"Downloading headshots: {len(to_download)} players ({len(existing)} already cached)")

    success = 0
    missing = []

    for i, player in enumerate(to_download, 1):
        url = CDN_URL.format(player_id=player["id"])
        out_path = OUTPUT_DIR / f"{player['id']}.png"
        print(f"  [{i}/{len(to_download)}] {player['name']}...", end=" ", flush=True)

        try:
            urllib.request.urlretrieve(url, out_path)
            # Check if we got a valid image (not a tiny placeholder/error)
            size = out_path.stat().st_size
            if size < 1000:
                out_path.unlink()
                print(f"SKIP (placeholder, {size}B)")
                missing.append(player["name"])
            else:
                print("OK")
                success += 1
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}")
            missing.append(player["name"])
        except Exception as e:
            print(f"ERROR: {str(e)[:60]}")
            missing.append(player["name"])

        time.sleep(REQUEST_DELAY)

    print(f"\nDone! Downloaded {success}/{len(to_download)} headshots.")
    if missing:
        print(f"Missing ({len(missing)}): {', '.join(missing[:20])}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")


if __name__ == "__main__":
    main()
