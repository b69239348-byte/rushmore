"""
Add specific missing players to players.json without rebuilding the full DB.
Only fetches players not already in the file.
Run: python3 tools/add_missing_players.py
"""
import json
import time
from pathlib import Path

from nba_api.stats.static import players as static_players
from nba_api.stats.endpoints import playercareerstats, playerawards, commonplayerinfo

DB_PATH = Path(__file__).parent.parent / "players.json"
DELAY = 0.7

TARGET_PLAYERS = [
    "Ja Morant",
    "Zion Williamson",
    "Trae Young",
    "Shai Gilgeous-Alexander",
    "Tyrese Haliburton",
    "Victor Wembanyama",
    "Paolo Banchero",
    "Cade Cunningham",
    "Evan Mobley",
    "Anthony Edwards",
    "Franz Wagner",
    "LaMelo Ball",
    "Jalen Brunson",
    "Darius Garland",
    "Scottie Barnes",
    "Dejounte Murray",
    "Josh Giddey",
    "Alperen Sengun",
    "OG Anunoby",
    "Mikal Bridges",
    "Jaren Jackson Jr.",
    "Desmond Bane",
    "Tyrese Maxey",
    "Jordan Poole",
    "Immanuel Quickley",
    "Keyonte George",
    "Ausar Thompson",
    "Amen Thompson",
]


def fetch_career_stats(player_id):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    totals = career.career_totals_regular_season.get_dict()
    if not totals["data"]:
        return None
    t = dict(zip(totals["headers"], totals["data"][0]))
    gp = t["GP"] or 1

    seasons = career.season_totals_regular_season.get_dict()
    teams = list(dict.fromkeys(
        dict(zip(seasons["headers"], row))["TEAM_ABBREVIATION"]
        for row in seasons["data"]
        if dict(zip(seasons["headers"], row))["TEAM_ABBREVIATION"]
    ))
    gp_by_team = {}
    for row in seasons["data"]:
        d = dict(zip(seasons["headers"], row))
        team = d.get("TEAM_ABBREVIATION", "")
        gp_val = d.get("GP", 0) or 0
        if team and team != "TOT":
            gp_by_team[team] = gp_by_team.get(team, 0) + gp_val
    main_team = max(gp_by_team, key=lambda t: gp_by_team[t]) if gp_by_team else (teams[0] if teams else None)

    return {
        "games_played": t["GP"],
        "ppg": round(t["PTS"] / gp, 1),
        "rpg": round(t["REB"] / gp, 1),
        "apg": round(t["AST"] / gp, 1),
        "spg": round(t["STL"] / gp, 1) if t.get("STL") else None,
        "bpg": round(t["BLK"] / gp, 1) if t.get("BLK") else None,
        "fg_pct": round(t["FG_PCT"] * 100, 1) if t.get("FG_PCT") else None,
        "ft_pct": round(t["FT_PCT"] * 100, 1) if t.get("FT_PCT") else None,
        "total_points": t["PTS"],
        "total_rebounds": t["REB"],
        "total_assists": t["AST"],
        "teams": teams,
        "main_team": main_team,
    }


def fetch_awards(player_id):
    awards_data = playerawards.PlayerAwards(player_id=player_id)
    rows = awards_data.player_awards.get_dict()
    counts = {k: 0 for k in ["championships", "mvps", "finals_mvps", "all_star",
                               "all_nba", "all_defensive", "scoring_champion",
                               "rookie_of_the_year", "dpoy"]}
    mapping = {
        "NBA Champion": "championships", "NBA Most Valuable Player": "mvps",
        "NBA Finals Most Valuable Player": "finals_mvps", "NBA All-Star": "all_star",
        "All-NBA": "all_nba", "All-Defensive Team": "all_defensive",
        "NBA Scoring Champion": "scoring_champion",
        "NBA Rookie of the Year": "rookie_of_the_year",
        "NBA Defensive Player of the Year": "dpoy",
    }
    for row in rows["data"]:
        desc = row[4]
        for key, award_key in mapping.items():
            if key in desc:
                counts[award_key] += 1
                break
    return counts


def fetch_player_info(player_id):
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    data = info.common_player_info.get_dict()
    if not data["data"]:
        return None
    d = dict(zip(data["headers"], data["data"][0]))
    return {
        "position": d.get("POSITION", ""),
        "height": d.get("HEIGHT", ""),
        "weight": d.get("WEIGHT", ""),
        "country": d.get("COUNTRY", ""),
        "draft_year": d.get("DRAFT_YEAR"),
        "draft_round": d.get("DRAFT_ROUND"),
        "draft_number": d.get("DRAFT_NUMBER"),
        "from_year": d.get("FROM_YEAR"),
        "to_year": d.get("TO_YEAR"),
        "greatest_75": d.get("GREATEST_75_FLAG", "") == "Y",
    }


def main():
    with open(DB_PATH, encoding="utf-8") as f:
        players = json.load(f)

    existing_names = {p["name"].lower() for p in players}
    all_nba_players = static_players.get_players()
    lookup = {p["full_name"]: p["id"] for p in all_nba_players}

    added = 0
    for name in TARGET_PLAYERS:
        if name.lower() in existing_names:
            print(f"SKIP (exists): {name}")
            continue
        pid = lookup.get(name)
        if not pid:
            print(f"NOT FOUND in NBA API: {name}")
            continue

        print(f"Fetching {name}...", end=" ", flush=True)
        try:
            stats = fetch_career_stats(pid)
            time.sleep(DELAY)
            awards = fetch_awards(pid)
            time.sleep(DELAY)
            info = fetch_player_info(pid)
            time.sleep(DELAY)

            if not stats or not info:
                print("SKIP (no data)")
                continue

            players.append({"id": pid, "name": name, **info, **stats, "awards": awards})
            added += 1
            print("OK")
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(2)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Added {added} players. Total: {len(players)}")


if __name__ == "__main__":
    main()
