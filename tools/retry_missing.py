"""
Retry fetching players that failed during the initial build.
Adds them to the existing players.json.
"""

import json
import time
from pathlib import Path

from build_player_db import fetch_career_stats, fetch_awards, fetch_player_info

REQUEST_DELAY = 1.0  # slightly more conservative

# Players to retry: (id, name)
MISSING_PLAYERS = [
    (1628369, "Jayson Tatum"),
    (203954, "Joel Embiid"),
    (23, "Dennis Rodman"),
    (1112, "Ben Wallace"),
    (87, "Dikembe Mutombo"),
    (78450, "Bill Walton"),
    (76462, "Dave Cowens"),
    (77626, "Sidney Moncrief"),
    (200784, "Bobby Jones"),
    (1629029, "Luka Dončić"),
    (203999, "Nikola Jokić"),
    # Additional important missing players
    (101150, "Kevin Johnson"),
    (2546, "Carmelo Anthony"),  # verify if missing
    (201566, "DeMarcus Cousins"),
    (2738, "Andre Iguodala"),
    (101125, "Peja Stojakovic"),
    (76925, "Billy Cunningham"),
    (2449, "Jermaine O'Neal"),
    (200826, "Deron Williams"),
    (1628, "Metta World Peace"),
    (101127, "Baron Davis"),
    (201143, "Carlos Boozer"),
    (200755, "David West"),
    (201567, "Kevin Love"),
    (201599, "Khris Middleton"),
    (1629630, "Jaylen Brown"),
]

DB_PATH = Path(__file__).parent.parent / "players.json"


def main():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        players = json.load(f)

    existing_ids = {p["id"] for p in players}
    added = 0

    for pid, name in MISSING_PLAYERS:
        if pid in existing_ids:
            print(f"  SKIP (already exists): {name}")
            continue

        print(f"  Fetching {name}...", end=" ", flush=True)
        try:
            stats = fetch_career_stats(pid)
            time.sleep(REQUEST_DELAY)
            awards = fetch_awards(pid)
            time.sleep(REQUEST_DELAY)
            info = fetch_player_info(pid)
            time.sleep(REQUEST_DELAY)

            if not stats or not info:
                print("SKIP (no data)")
                continue

            player = {
                "id": pid,
                "name": name,
                **info,
                **stats,
                "awards": awards,
            }
            players.append(player)
            added += 1
            print("OK")

        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(3)

    # Re-sort by total points
    players.sort(key=lambda p: p["total_points"], reverse=True)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Added {added} players. Total: {len(players)}")


if __name__ == "__main__":
    main()
