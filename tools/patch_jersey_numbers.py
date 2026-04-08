"""
Add jersey field to players.json from NBA API commonplayerinfo.
Run once: python3 tools/patch_jersey_numbers.py
"""
import json
import time
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from nba_api.stats.endpoints import commonplayerinfo

DB_PATH = Path(__file__).parent.parent / "players.json"
DELAY = 0.6


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        players = json.load(f)

    total = len(players)
    for i, p in enumerate(players, 1):
        if "jersey" in p:
            print(f"[{i}/{total}] {p['name']}: #{p['jersey']} (cached)")
            continue
        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=p["id"])
            d = dict(zip(
                info.common_player_info.get_dict()["headers"],
                info.common_player_info.get_dict()["data"][0]
            ))
            jersey = d.get("JERSEY") or ""
            p["jersey"] = jersey
            print(f"[{i}/{total}] {p['name']}: #{jersey}")
            time.sleep(DELAY)
        except Exception as e:
            p["jersey"] = ""
            print(f"[{i}/{total}] {p['name']}: ERROR {e}")
            time.sleep(1.5)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=2, ensure_ascii=False)
    print(f"\nDone! Jersey numbers added to {total} players.")


if __name__ == "__main__":
    main()
