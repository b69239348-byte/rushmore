"""
Live NBA data via nba_api with local file caching.
Fetches current season leaders and active player stats.
"""

import json
import time
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(__file__).parent.parent / ".tmp" / "cache"
CACHE_MAX_AGE = 6 * 3600  # 6 hours in seconds


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def _read_cache(key: str):
    """Read cached data if fresh enough, else return None."""
    path = _cache_path(key)
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > CACHE_MAX_AGE:
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_cache(key: str, data):
    """Write data to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_cache_path(key), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def _season_for_date(d: "date") -> str:
    """Return NBA season string for a given date (e.g. date(2025,3,1) → '2024-25')."""
    start_year = d.year if d.month >= 10 else d.year - 1
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _detect_season() -> str:
    """Return NBA season string for today's date."""
    from datetime import datetime
    return _season_for_date(datetime.now().date())


def fetch_season_leaders(season: Optional[str] = None, limit: int = 30) -> list[dict]:
    """Fetch current season leaders sorted by total points.

    Returns a list of player dicts compatible with our player format.
    """
    if season is None:
        season = _detect_season()

    cache_key = f"season_leaders_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    from nba_api.stats.endpoints import leagueleaders

    leaders = leagueleaders.LeagueLeaders(
        season=season,
        stat_category_abbreviation="PTS",
    )
    df = leaders.get_data_frames()[0]

    players = []
    for _, row in df.iterrows():
        gp = row["GP"] or 1
        players.append({
            "id": int(row["PLAYER_ID"]),
            "name": row["PLAYER"],
            "team": row["TEAM"],
            "gp": int(row["GP"]),
            "ppg": round(row["PTS"] / gp, 1),
            "rpg": round(row["REB"] / gp, 1),
            "apg": round(row["AST"] / gp, 1),
            "spg": round(row["STL"] / gp, 1),
            "bpg": round(row["BLK"] / gp, 1),
            "fgp": round(row["FG_PCT"] * 100, 1) if row["FG_PCT"] else 0,
            "fg3p": round(row["FG3_PCT"] * 100, 1) if row["FG3_PCT"] else 0,
            "ftp": round(row["FT_PCT"] * 100, 1) if row["FT_PCT"] else 0,
            "total_points_season": int(row["PTS"]),
            "total_rebounds_season": int(row["REB"]),
            "total_assists_season": int(row["AST"]),
            "eff": float(row["EFF"]),
        })

    _write_cache(cache_key, players)
    return players[:limit]


def fetch_active_players(limit: int = 10) -> list[dict]:
    """Fetch top active players by current season PPG.

    Uses season leaders data — anyone appearing there is active.
    """
    season = _detect_season()
    cache_key = f"active_top_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    # Get a broad set of season leaders (top 100 scorers are all active)
    all_leaders = fetch_season_leaders(season=season, limit=100)

    # Sort by PPG for the "best active" ranking
    sorted_by_ppg = sorted(all_leaders, key=lambda p: p["ppg"], reverse=True)

    _write_cache(cache_key, sorted_by_ppg)
    return sorted_by_ppg[:limit]


def fetch_current_mvp_race(limit: int = 5) -> list[dict]:
    """Top MVP candidates this season, sorted by efficiency rating."""
    season = _detect_season()
    cache_key = f"mvp_race_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    players = fetch_season_leaders(season=season, limit=50)
    sorted_p = sorted(players, key=lambda p: p.get("eff", 0), reverse=True)
    _write_cache(cache_key, sorted_p)
    return sorted_p[:limit]


def fetch_current_dpoy_race(limit: int = 5) -> list[dict]:
    """Top DPOY candidates this season, sorted by combined blocks + steals per game."""
    season = _detect_season()
    cache_key = f"dpoy_race_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    players = fetch_season_leaders(season=season, limit=100)
    for p in players:
        p["_def_score"] = round(p.get("bpg", 0) + p.get("spg", 0), 2)
    sorted_p = sorted(players, key=lambda p: p["_def_score"], reverse=True)
    _write_cache(cache_key, sorted_p)
    return sorted_p[:limit]


def fetch_current_roy_race(limit: int = 5) -> list[dict]:
    """Top ROY candidates - current season rookies sorted by PPG."""
    season = _detect_season()
    cache_key = f"roy_race_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    from nba_api.stats.endpoints import leaguedashplayerstats

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season,
        player_experience_nullable="Rookie",
        per_mode_detailed="PerGame",
    )
    df = stats.get_data_frames()[0]
    df = df[df["GP"] >= 10].sort_values("PTS", ascending=False)

    players = []
    for _, row in df.iterrows():
        players.append({
            "id": int(row["PLAYER_ID"]),
            "name": row["PLAYER_NAME"],
            "team": row.get("TEAM_ABBREVIATION", ""),
            "gp": int(row["GP"]),
            "ppg": round(float(row["PTS"]), 1),
            "rpg": round(float(row["REB"]), 1),
            "apg": round(float(row["AST"]), 1),
            "spg": round(float(row["STL"]), 1),
            "bpg": round(float(row["BLK"]), 1),
            "eff": round(float(row.get("PIE", 0) or 0) * 100, 1),
        })

    _write_cache(cache_key, players)
    return players[:limit]


def fetch_current_mip_race(limit: int = 5) -> list[dict]:
    """Most improved players - biggest PPG jump vs. last season."""
    season = _detect_season()
    cache_key = f"mip_race_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached[:limit]

    parts = season.split("-")
    start = int(parts[0]) - 1
    last_season = f"{start}-{str(start + 1)[-2:]}"

    current = {p["id"]: p for p in fetch_season_leaders(season=season, limit=100)}
    last = {p["id"]: p for p in fetch_season_leaders(season=last_season, limit=100)}

    improved = []
    for pid, p in current.items():
        if pid in last and p.get("gp", 0) >= 20:
            delta = round(p["ppg"] - last[pid]["ppg"], 1)
            if delta > 0:
                p["_improvement"] = delta
                improved.append(p)

    improved.sort(key=lambda p: p["_improvement"], reverse=True)
    _write_cache(cache_key, improved)
    return improved[:limit]


def fetch_all_nba_tier(tier: int = 1, limit: int = 50) -> list[dict]:
    """All-NBA candidates pool — top players by EFF. Same pool for all tiers."""
    season = _detect_season()
    cache_key = f"all_nba_{season}"
    cached = _read_cache(cache_key)
    if cached is None:
        players = fetch_season_leaders(season=season, limit=100)
        cached = sorted(players, key=lambda p: p.get("eff", 0), reverse=True)
        _write_cache(cache_key, cached)

    return cached[:limit]


_TEAM_NAME_TO_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
}


def fetch_team_stats(season: Optional[str] = None) -> dict:
    """Fetch current season team stats: W/L record + OFF/DEF/NET rating.
    Returns dict keyed by team abbreviation.
    """
    if season is None:
        season = _detect_season()

    cache_key = f"team_stats_{season}"
    cached = _read_cache(cache_key)
    if cached is not None:
        return cached

    from nba_api.stats.endpoints import leaguedashteamstats

    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season,
        measure_type_detailed_defense="Advanced",
    )
    df = stats.get_data_frames()[0]

    result = {}
    for _, row in df.iterrows():
        abbr = _TEAM_NAME_TO_ABBR.get(row["TEAM_NAME"])
        if abbr:
            result[abbr] = {
                "w":       int(row["W"]),
                "l":       int(row["L"]),
                "off_rtg": round(float(row["OFF_RATING"]), 1),
                "def_rtg": round(float(row["DEF_RATING"]), 1),
                "net_rtg": round(float(row["NET_RATING"]), 1),
            }

    _write_cache(cache_key, result)
    return result


def get_new_player_ids(limit: int = 30) -> list[int]:
    """Return player IDs from season leaders that aren't in players.json."""
    db_path = Path(__file__).parent.parent / "players.json"
    with open(db_path, "r", encoding="utf-8") as f:
        existing_ids = {p["id"] for p in json.load(f)}

    leaders = fetch_season_leaders(limit=limit)
    return [p["id"] for p in leaders if p["id"] not in existing_ids]


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "season"
    season = _detect_season()
    print(f"Season: {season}\n")

    if cmd == "season":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        players = fetch_season_leaders(limit=limit)
        print(f"Top {len(players)} Season Leaders:")
        for i, p in enumerate(players, 1):
            print(f"  {i:2d}. {p['name']:25s} {p['team']:4s} {p['ppg']:5.1f} PPG  {p['rpg']:4.1f} RPG  {p['apg']:4.1f} APG")
    elif cmd == "active":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        players = fetch_active_players(limit=limit)
        print(f"Top {len(players)} Active Players (by PPG):")
        for i, p in enumerate(players, 1):
            print(f"  {i:2d}. {p['name']:25s} {p['team']:4s} {p['ppg']:5.1f} PPG  {p['rpg']:4.1f} RPG  {p['apg']:4.1f} APG")
    elif cmd == "new":
        ids = get_new_player_ids()
        print(f"New player IDs (not in players.json): {ids}")
    else:
        print("Usage: live_data.py [season|active|new] [limit]")
