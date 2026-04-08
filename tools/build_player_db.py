"""
Build the Rushmore top 200 all-time NBA player database.
Uses nba_api to fetch career stats, awards, and metadata.
Output: players.json
"""

import json
import time
import sys
from pathlib import Path

from nba_api.stats.static import players as static_players
from nba_api.stats.endpoints import (
    leagueleaders,
    playercareerstats,
    playerawards,
    commonplayerinfo,
)

REQUEST_DELAY = 0.6  # seconds between API calls

# Legends who may not rank high in total points but belong in the top 200
SUPPLEMENTAL_LEGENDS = [
    "Bill Russell",
    "Dennis Rodman",
    "Arvydas Sabonis",
    "Drazen Petrovic",
    "Pete Maravich",
    "Bob Cousy",
    "Jerry West",
    "Wilt Chamberlain",
    "Bill Walton",
    "Walt Frazier",
    "Willis Reed",
    "Dave DeBusschere",
    "Nate Thurmond",
    "Connie Hawkins",
    "Bob Pettit",
    "George Mikan",
    "Dolph Schayes",
    "Bob McAdoo",
    "Dave Cowens",
    "Tiny Archibald",
    "Earl Monroe",
    "Lenny Wilkens",
    "Sam Jones",
    "K.C. Jones",
    "Tom Heinsohn",
    "John Havlicek",
    "Bobby Jones",
    "Sidney Moncrief",
    "Ben Wallace",
    "Dikembe Mutombo",
    "Manu Ginobili",
    "Tony Parker",
    "Kawhi Leonard",
    "Nikola Jokic",
    "Giannis Antetokounmpo",
    "Luka Doncic",
    # Modern stars (post-2018 draft)
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
    "Jaren Jackson Jr.",
    "Desmond Bane",
    "Tyrese Maxey",
    "Mikal Bridges",
    "OG Anunoby",
    "Alperen Sengun",
]


def fetch_alltime_leaders(top_n=250):
    """Fetch top N all-time points leaders as our base player pool."""
    print(f"Fetching top {top_n} all-time points leaders...")
    leaders = leagueleaders.LeagueLeaders(
        season="All Time",
        stat_category_abbreviation="PTS",
        per_mode48="Totals",
    )
    rows = leaders.league_leaders.get_dict()
    headers = rows["headers"]
    data = rows["data"]

    player_ids = {}
    for row in data[:top_n]:
        d = dict(zip(headers, row))
        player_ids[d["PLAYER_ID"]] = d["PLAYER_NAME"]

    print(f"  Got {len(player_ids)} players from all-time leaders.")
    return player_ids


def add_supplemental_players(player_ids):
    """Add legends who might not be in the top N scorers."""
    all_players = static_players.get_players()
    lookup = {p["full_name"]: p["id"] for p in all_players}

    added = 0
    missing = []
    for name in SUPPLEMENTAL_LEGENDS:
        if name in lookup:
            pid = lookup[name]
            if pid not in player_ids:
                player_ids[pid] = name
                added += 1
        else:
            missing.append(name)

    if missing:
        print(f"  Warning: could not find these players: {missing}")
    print(f"  Added {added} supplemental legends. Total pool: {len(player_ids)}")
    return player_ids


def fetch_career_stats(player_id):
    """Fetch career totals and teams played for."""
    career = playercareerstats.PlayerCareerStats(player_id=player_id)

    # Career totals
    totals = career.career_totals_regular_season.get_dict()
    if not totals["data"]:
        return None

    t = dict(zip(totals["headers"], totals["data"][0]))
    gp = t["GP"] or 1

    # Teams from season-by-season data
    seasons = career.season_totals_regular_season.get_dict()
    teams = list(dict.fromkeys(
        dict(zip(seasons["headers"], row))["TEAM_ABBREVIATION"]
        for row in seasons["data"]
        if dict(zip(seasons["headers"], row))["TEAM_ABBREVIATION"]
    ))

    # Main team = team with most games played
    gp_by_team: dict = {}
    for row in seasons["data"]:
        d = dict(zip(seasons["headers"], row))
        team = d.get("TEAM_ABBREVIATION", "")
        gp = d.get("GP", 0) or 0
        if team and team != "TOT":
            gp_by_team[team] = gp_by_team.get(team, 0) + gp
    main_team = max(gp_by_team, key=lambda t: gp_by_team[t]) if gp_by_team else (teams[0] if teams else None)

    return {
        "games_played": t["GP"],
        "ppg": round(t["PTS"] / gp, 1),
        "rpg": round(t["REB"] / gp, 1),
        "apg": round(t["AST"] / gp, 1),
        "spg": round(t["STL"] / gp, 1) if t["STL"] else None,
        "bpg": round(t["BLK"] / gp, 1) if t["BLK"] else None,
        "fg_pct": round(t["FG_PCT"] * 100, 1) if t["FG_PCT"] else None,
        "ft_pct": round(t["FT_PCT"] * 100, 1) if t["FT_PCT"] else None,
        "total_points": t["PTS"],
        "total_rebounds": t["REB"],
        "total_assists": t["AST"],
        "teams": teams,
        "main_team": main_team,
    }


def fetch_awards(player_id):
    """Fetch player awards and count relevant accolades."""
    awards_data = playerawards.PlayerAwards(player_id=player_id)
    rows = awards_data.player_awards.get_dict()

    award_counts = {
        "championships": 0,
        "mvps": 0,
        "finals_mvps": 0,
        "all_star": 0,
        "all_nba": 0,
        "all_defensive": 0,
        "scoring_champion": 0,
        "rookie_of_the_year": 0,
        "dpoy": 0,
    }

    mapping = {
        "NBA Champion": "championships",
        "NBA Most Valuable Player": "mvps",
        "NBA Finals Most Valuable Player": "finals_mvps",
        "NBA All-Star": "all_star",
        "All-NBA": "all_nba",
        "All-Defensive Team": "all_defensive",
        "NBA Scoring Champion": "scoring_champion",
        "NBA Rookie of the Year": "rookie_of_the_year",
        "NBA Defensive Player of the Year": "dpoy",
    }

    for row in rows["data"]:
        desc = row[4]  # DESCRIPTION field
        for key, award_key in mapping.items():
            if key in desc:
                award_counts[award_key] += 1
                break

    return award_counts


def fetch_player_info(player_id):
    """Fetch player metadata."""
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
        "jersey": d.get("JERSEY", ""),
    }


def build_database():
    # Step 1: Build player pool
    player_ids = fetch_alltime_leaders(250)
    time.sleep(REQUEST_DELAY)
    player_ids = add_supplemental_players(player_ids)

    # Step 2: Enrich each player
    players = []
    total = len(player_ids)
    errors = []

    for i, (pid, name) in enumerate(player_ids.items(), 1):
        print(f"  [{i}/{total}] {name}...", end=" ", flush=True)

        try:
            # Fetch all three endpoints with delays
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
            print("OK")

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append({"name": name, "id": pid, "error": str(e)})
            time.sleep(2)  # extra delay after errors

    # Step 3: Sort by total points (descending) and trim to 200
    players.sort(key=lambda p: p["total_points"], reverse=True)
    # Keep all — we might want more than 200 later

    # Step 4: Save
    output_path = Path(__file__).parent.parent / "players.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(players, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Saved {len(players)} players to {output_path}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e['name']}: {e['error']}")

    return players


if __name__ == "__main__":
    build_database()
