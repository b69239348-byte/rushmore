"""
Patch players.json: add main_team = team the player played the most games for.
Only makes NBA API calls for players with multiple teams.
Run once: python tools/patch_main_team.py
"""
import json
import time
from pathlib import Path

from nba_api.stats.endpoints import playercareerstats

DB_PATH = Path(__file__).parent.parent / "players.json"
DELAY = 0.7  # seconds between API calls


def get_main_team(player_id: int):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    seasons = career.season_totals_regular_season.get_dict()
    gp_by_team: dict[str, int] = {}
    for row in seasons["data"]:
        d = dict(zip(seasons["headers"], row))
        team = d.get("TEAM_ABBREVIATION", "")
        gp = d.get("GP", 0) or 0
        if team and team != "TOT":  # skip "TOT" (total) rows for traded players
            gp_by_team[team] = gp_by_team.get(team, 0) + gp
    if not gp_by_team:
        return None
    return max(gp_by_team, key=lambda t: gp_by_team[t])


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        players = json.load(f)

    total = len(players)
    api_calls = 0

    for i, p in enumerate(players, 1):
        teams = p.get("teams", [])

        if len(teams) <= 1:
            p["main_team"] = teams[0] if teams else None
            print(f"[{i}/{total}] {p['name']}: {p['main_team']} (single team)")
        else:
            try:
                mt = get_main_team(p["id"])
                p["main_team"] = mt
                api_calls += 1
                print(f"[{i}/{total}] {p['name']}: {mt}  (from {teams})")
                time.sleep(DELAY)
            except Exception as e:
                fallback = teams[0]
                p["main_team"] = fallback
                print(f"[{i}/{total}] {p['name']}: ERROR — {e} → fallback {fallback}")
                time.sleep(1.5)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {api_calls} API calls made. players.json updated.")


if __name__ == "__main__":
    main()
