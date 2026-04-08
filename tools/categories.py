"""
Category system for Rushmore.
Filters and ranks players from players.json by various criteria.
Returns lists ready for card generation.
"""

import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "players.json"

# Map compound positions to canonical ones
POSITION_MAP = {
    "Guard": "G",
    "Guard-Forward": "G",
    "Forward-Guard": "G",
    "Forward": "F",
    "Forward-Center": "F",
    "Center-Forward": "C",
    "Center": "C",
}

# Canonical position labels
POSITION_LABELS = {
    "G": "Guards",
    "F": "Forwards",
    "C": "Centers",
}

# More specific position mapping for 5-position system
POSITION_5_MAP = {
    "Guard": ["PG", "SG"],
    "Guard-Forward": ["SG"],
    "Forward-Guard": ["SG", "SF"],
    "Forward": ["SF", "PF"],
    "Forward-Center": ["PF"],
    "Center-Forward": ["PF", "C"],
    "Center": ["C"],
}

# Map historical/relocated teams to current franchise
FRANCHISE_MAP = {
    # Current teams map to themselves
    "ATL": "ATL", "BOS": "BOS", "BKN": "BKN", "CHA": "CHA",
    "CHI": "CHI", "CLE": "CLE", "DAL": "DAL", "DEN": "DEN",
    "DET": "DET", "GSW": "GSW", "HOU": "HOU", "IND": "IND",
    "LAC": "LAC", "LAL": "LAL", "MEM": "MEM", "MIA": "MIA",
    "MIL": "MIL", "MIN": "MIN", "NOP": "NOP", "NYK": "NYK",
    "OKC": "OKC", "ORL": "ORL", "PHI": "PHI", "PHX": "PHX",
    "POR": "POR", "SAC": "SAC", "SAS": "SAS", "TOR": "TOR",
    "UTA": "UTA", "WAS": "WAS",
    # Historical → current franchise
    "NJN": "BKN", "NYN": "BKN",           # Nets
    "CHH": "CHA", "CHZ": "CHA",           # Hornets (original)
    "SEA": "OKC",                          # SuperSonics → Thunder
    "VAN": "MEM",                          # Vancouver → Memphis
    "NOH": "NOP", "NOK": "NOP", "NOJ": "NOP",  # New Orleans history
    "SDC": "LAC", "BUF": "LAC",           # Clippers history
    "KCK": "SAC",                          # Kings history
    "SFW": "GSW", "GOS": "GSW", "PHW": "GSW",  # Warriors history
    "STL": "ATL",                          # Hawks history
    "CIN": "SAC", "ROC": "SAC",           # Kings deep history
    "SYR": "PHI",                          # 76ers history
    "MNL": "LAL",                          # Minneapolis Lakers
    "SAN": "SAS",                          # Spurs
    "SDR": "HOU",                          # Rockets history
    "BLT": "WAS", "CAP": "WAS",           # Wizards history
    "CHP": "CHI",                          # Chicago Packers
    "PHL": "PHI",                          # Philly variant
    "MIH": "MIL",                          # Milwaukee variant
    "UTH": "UTA",                          # Utah variant
}

# Friendly team names
TEAM_NAMES = {
    "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
    "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
    "LAC": "LA Clippers", "LAL": "Los Angeles Lakers", "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
}

DECADE_LABELS = {
    1950: "1950s", 1960: "1960s", 1970: "1970s", 1980: "1980s",
    1990: "1990s", 2000: "2000s", 2010: "2010s", 2020: "2020s",
}


def load_players():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _rank_by(players, key, limit=5, reverse=True):
    """Sort players by a key and return top N."""
    sorted_p = sorted(players, key=lambda p: p.get(key, 0) or 0, reverse=reverse)
    return sorted_p[:limit]


# --- Core Categories ---

def all_time(limit=5, sort_by="total_points"):
    """All-time greatest players."""
    players = load_players()
    return {
        "title": f"ALL-TIME TOP {limit}",
        "subtitle": "Greatest Players Ever",
        "players": _rank_by(players, sort_by, limit),
    }


def by_position(position_code, limit=5, sort_by="total_points"):
    """Top players by position (G, F, C)."""
    players = load_players()
    filtered = [p for p in players if POSITION_MAP.get(p.get("position", "")) == position_code]
    label = POSITION_LABELS.get(position_code, position_code)
    return {
        "title": f"TOP {limit} {label.upper()}",
        "subtitle": "All-Time Best",
        "players": _rank_by(filtered, sort_by, limit),
    }


def _team_affinity(player, team_code):
    """Score how strongly a player is associated with a franchise.

    Heuristic based on:
    - Position in teams list (earlier = more time spent, typically)
    - Number of total teams (fewer = more loyal)
    - Whether it's their only/primary team

    Returns a score between 0 and 1 that multiplies with total_points.
    """
    teams = player.get("teams", [])
    franchises = [FRANCHISE_MAP.get(t, t) for t in teams]
    num_teams = len(franchises)

    if team_code not in franchises:
        return 0

    # Find earliest position of this franchise in career
    idx = next(i for i, f in enumerate(franchises) if f == team_code)

    # Count how many of their team entries map to this franchise
    # (e.g. someone who played for LAL twice counts double)
    franchise_entries = sum(1 for f in franchises if f == team_code)

    if num_teams == 1:
        # One-team player — maximum affinity
        return 1.0
    elif num_teams == 2 and idx == 0:
        # Two teams, this was their first — strong association
        return 0.9
    elif idx == 0:
        # First team in a longer career — likely where they built their name
        return 0.75
    elif franchise_entries >= 2:
        # Came back to this team — strong connection
        return 0.7
    elif idx == num_teams - 1 and num_teams >= 3:
        # Last stop in a long career — weakest association (ring chasing, farewell tour)
        return 0.3
    elif idx == 1 and num_teams <= 3:
        # Second team, short career — decent association
        return 0.6
    else:
        # Middle of a longer journey
        return 0.45


def by_team(team_code, limit=5, sort_by="total_points"):
    """Top players for a franchise, weighted by franchise affinity."""
    players = load_players()
    scored = []
    for p in players:
        affinity = _team_affinity(p, team_code)
        if affinity > 0:
            score = (p.get("total_points", 0) or 0) * affinity
            p["_team_score"] = score
            scored.append(p)

    scored.sort(key=lambda p: p["_team_score"], reverse=True)
    team_name = TEAM_NAMES.get(team_code, team_code)
    return {
        "title": f"TOP {limit} {team_code}",
        "subtitle": team_name,
        "players": scored[:limit],
    }


def by_era(decade_start, limit=5, sort_by="ppg"):
    """Top players whose prime overlapped with a decade."""
    players = load_players()
    decade_end = decade_start + 9
    filtered = []
    for p in players:
        from_y = p.get("from_year", 0) or 0
        to_y = p.get("to_year", 0) or 0
        # Player's career overlaps with the decade
        if from_y <= decade_end and to_y >= decade_start:
            # Bonus: calculate how much of their career was in this decade
            overlap_start = max(from_y, decade_start)
            overlap_end = min(to_y, decade_end)
            p["_decade_years"] = overlap_end - overlap_start + 1
            filtered.append(p)
    label = DECADE_LABELS.get(decade_start, f"{decade_start}s")
    return {
        "title": f"TOP {limit} OF THE {label.upper()}",
        "subtitle": f"Best Players {decade_start}-{decade_start + 9}",
        "players": _rank_by(filtered, sort_by, limit),
    }


def champions(limit=5):
    """Players ranked by championship count."""
    players = load_players()
    with_rings = [p for p in players if p.get("awards", {}).get("championships", 0) > 0]
    sorted_p = sorted(with_rings, key=lambda p: (
        p["awards"]["championships"],
        p.get("awards", {}).get("finals_mvps", 0),
        p.get("total_points", 0),
    ), reverse=True)
    return {
        "title": f"TOP {limit} CHAMPIONS",
        "subtitle": "Most Rings All-Time",
        "players": sorted_p[:limit],
    }


def mvp_race(limit=5):
    """Players ranked by MVP count."""
    players = load_players()
    with_mvps = [p for p in players if p.get("awards", {}).get("mvps", 0) > 0]
    sorted_p = sorted(with_mvps, key=lambda p: (
        p["awards"]["mvps"],
        p.get("awards", {}).get("championships", 0),
        p.get("total_points", 0),
    ), reverse=True)
    return {
        "title": f"TOP {limit} MVPs",
        "subtitle": "Most Valuable Players",
        "players": sorted_p[:limit],
    }


# --- Award Categories ---

# Award definitions: slug → (award_key, title, subtitle)
AWARD_DEFS = {
    "mvp": ("mvps", "MVP AWARD WINNERS", "Most Valuable Player"),
    "all-nba": ("all_nba", "ALL-NBA SELECTIONS", "Most All-NBA Selections"),
    "roy": ("rookie_of_the_year", "ROOKIE OF THE YEAR", "ROY Award Winners"),
    "dpoy": ("dpoy", "DEFENSIVE PLAYER OF THE YEAR", "Best Defenders All-Time"),
    "all-star": ("all_star", "ALL-STAR SELECTIONS", "Most All-Star Appearances"),
    "all-defensive": ("all_defensive", "ALL-DEFENSIVE TEAM", "Most All-Defensive Selections"),
    "scoring-champion": ("scoring_champion", "SCORING CHAMPIONS", "Most Scoring Titles"),
    "finals-mvp": ("finals_mvps", "FINALS MVP", "Most Finals MVP Awards"),
}


def by_award(slug, limit=10):
    """Players ranked by a specific award count."""
    if slug not in AWARD_DEFS:
        return {"error": f"Unknown award: {slug}", "available": list(AWARD_DEFS.keys())}

    award_key, title, subtitle = AWARD_DEFS[slug]
    players = load_players()

    # Filter players who have this award at least once
    with_award = [p for p in players if p.get("awards", {}).get(award_key, 0) > 0]

    # Sort by award count (desc), then by total points as tiebreaker
    sorted_p = sorted(with_award, key=lambda p: (
        p["awards"][award_key],
        p.get("total_points", 0),
    ), reverse=True)

    return {
        "title": title,
        "subtitle": subtitle,
        "players": sorted_p[:limit],
    }


def list_awards():
    """Return available award categories."""
    return {slug: {"title": title, "subtitle": subtitle} for slug, (_, title, subtitle) in AWARD_DEFS.items()}


# --- Live Categories (Tier 2) ---

def current_season(limit=30):
    """Current season leaders by total points scored."""
    from live_data import fetch_season_leaders, _detect_season
    season = _detect_season()
    players = fetch_season_leaders(season=season, limit=limit)
    return {
        "title": f"TOP {limit} THIS SEASON",
        "subtitle": f"{season} Season Leaders",
        "players": players,
    }


def active_players(limit=10):
    """Top active players by PPG this season."""
    from live_data import fetch_active_players, _detect_season
    season = _detect_season()
    players = fetch_active_players(limit=limit)
    return {
        "title": f"TOP {limit} ACTIVE PLAYERS",
        "subtitle": f"{season} Best by PPG",
        "players": players,
    }


def team_ranking(limit=30):
    """Rank all 30 teams by their current season talent.

    Aggregates total points scored by each team's players in the season.
    """
    from live_data import fetch_season_leaders, _detect_season
    from collections import defaultdict

    season = _detect_season()
    leaders = fetch_season_leaders(season=season, limit=200)

    team_stats = defaultdict(lambda: {"pts": 0, "players": 0, "top_player": None, "ppg_sum": 0})
    for p in leaders:
        t = p.get("team", "???")
        team_stats[t]["pts"] += p.get("total_points_season", 0)
        team_stats[t]["ppg_sum"] += p.get("ppg", 0)
        team_stats[t]["players"] += 1
        if team_stats[t]["top_player"] is None:
            team_stats[t]["top_player"] = p["name"]

    ranked = sorted(team_stats.items(), key=lambda x: x[1]["pts"], reverse=True)

    teams = []
    for rank, (code, stats) in enumerate(ranked[:limit], 1):
        name = TEAM_NAMES.get(code, code)
        teams.append({
            "rank": rank,
            "code": code,
            "name": name,
            "total_points": stats["pts"],
            "players_in_top": stats["players"],
            "top_player": stats["top_player"],
            "avg_ppg": round(stats["ppg_sum"] / stats["players"], 1) if stats["players"] else 0,
        })

    return {
        "title": "TEAM POWER RANKING",
        "subtitle": f"{season} — By Total Scoring Talent",
        "teams": teams,
    }


# --- Utility ---

def list_categories():
    """Return all available categories with metadata."""
    players = load_players()

    # Collect teams that have enough players
    team_counts = {}
    for p in players:
        for t in p.get("teams", []):
            franchise = FRANCHISE_MAP.get(t, t)
            if franchise in TEAM_NAMES:
                team_counts[franchise] = team_counts.get(franchise, 0) + 1

    # Collect decades with players
    decades = set()
    for p in players:
        from_y = p.get("from_year", 0) or 0
        to_y = p.get("to_year", 0) or 0
        for d in range(1950, 2030, 10):
            if from_y <= d + 9 and to_y >= d:
                decades.add(d)

    return {
        "all_time": {"label": "All-Time Greatest", "sort_options": ["total_points", "ppg", "total_rebounds", "total_assists"]},
        "positions": {code: POSITION_LABELS[code] for code in ["G", "F", "C"]},
        "teams": {code: TEAM_NAMES[code] for code in sorted(team_counts.keys()) if team_counts[code] >= 3},
        "eras": {d: DECADE_LABELS[d] for d in sorted(decades) if d in DECADE_LABELS},
        "champions": {"label": "Most Championships"},
        "mvps": {"label": "Most MVPs"},
        "current_season": {"label": "Current Season Leaders"},
        "active": {"label": "Top Active Players"},
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Available categories:")
        cats = list_categories()
        print(f"\n  all_time [limit]")
        print(f"  position <G|F|C> [limit]")
        print(f"  team <CODE> [limit]")
        print(f"  era <DECADE> [limit]  (e.g. 1990)")
        print(f"  champions [limit]")
        print(f"  mvps [limit]")
        print(f"  season [limit]     (current season leaders, live)")
        print(f"  active [limit]     (top active players, live)")
        print(f"\n  Teams: {', '.join(sorted(cats['teams'].keys()))}")
        print(f"  Eras: {', '.join(str(d) for d in sorted(cats['eras'].keys()))}")
        sys.exit(0)

    cmd = sys.argv[1]
    limit = 5

    if cmd == "all_time":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = all_time(limit)
    elif cmd == "position":
        pos = sys.argv[2].upper() if len(sys.argv) > 2 else "G"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        result = by_position(pos, limit)
    elif cmd == "team":
        team = sys.argv[2].upper() if len(sys.argv) > 2 else "LAL"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        result = by_team(team, limit)
    elif cmd == "era":
        decade = int(sys.argv[2]) if len(sys.argv) > 2 else 1990
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        result = by_era(decade, limit)
    elif cmd == "champions":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        result = champions(limit)
    elif cmd == "mvps":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        result = mvp_race(limit)
    elif cmd == "season":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        result = current_season(limit)
    elif cmd == "active":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = active_players(limit)
    else:
        print(f"Unknown category: {cmd}")
        sys.exit(1)

    print(f"\n{result['title']}")
    print(f"{result['subtitle']}")
    print("-" * 50)
    for i, p in enumerate(result["players"], 1):
        awards = p.get("awards", {})
        rings = awards.get("championships", 0)
        mvps = awards.get("mvps", 0)
        badge = ""
        if rings:
            badge += f" | {rings}x Champ"
        if mvps:
            badge += f" | {mvps}x MVP"
        print(f"  {i}. {p['name']:25s} {p.get('ppg',0):5.1f} PPG  {p.get('rpg',0):5.1f} RPG  {p.get('apg',0):5.1f} APG{badge}")
