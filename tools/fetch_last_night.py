"""
Fetch yesterday's top 5 NBA scorers and save to tools/data/last_night.json.
Runs as a local cron job at 5:45 AM before the CCR agent picks it up at 6:00 AM.
"""
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = DATA_DIR / "last_night.json"

# Log to file so we can debug cron runs
LOG_FILE = REPO_ROOT / ".tmp" / "fetch_last_night.log"


def log(msg: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def fetch_top5():
    from nba_api.stats.endpoints.scoreboardv2 import ScoreboardV2
    from nba_api.live.nba.endpoints.boxscore import BoxScore

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%m/%d/%Y")
    date_label = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log(f"Fetching games for {yesterday}")

    board = ScoreboardV2(game_date=yesterday, timeout=30)
    games_df = board.game_header.get_data_frame()

    if games_df.empty:
        log("No games yesterday.")
        return {"date": date_label, "games": False, "players": []}

    game_ids = games_df["GAME_ID"].tolist()
    log(f"Found {len(game_ids)} games: {game_ids}")

    all_players = []
    for gid in game_ids:
        try:
            time.sleep(0.6)
            box = BoxScore(gid)
            data = box.get_dict()
            game = data["game"]
            for team_key in ("homeTeam", "awayTeam"):
                team = game[team_key]
                for p in team["players"]:
                    s = p["statistics"]
                    minutes = s.get("minutesCalculated", "PT0M")
                    if minutes and minutes not in ("PT00M00.00S", "PT0M"):
                        all_players.append({
                            "player_id": int(p["personId"]),
                            "player_name": p["name"],
                            "team": team["teamTricode"],
                            "pts": int(s.get("points", 0)),
                            "reb": int(s.get("reboundsTotal", 0)),
                            "ast": int(s.get("assists", 0)),
                            "stl": int(s.get("steals", 0)),
                            "blk": int(s.get("blocks", 0)),
                        })
        except Exception as e:
            log(f"Error fetching boxscore for {gid}: {e}")
            continue

    top5 = sorted(all_players, key=lambda p: p["pts"], reverse=True)[:5]
    log(f"Top 5: {[(p['player_name'], p['pts']) for p in top5]}")

    # Auto-add any missing players to players.json
    db_path = REPO_ROOT / "players.json"
    db = json.loads(db_path.read_text())
    db_ids = {p["id"] for p in db}
    added = []
    for p in top5:
        if p["player_id"] not in db_ids:
            log(f"Missing player: {p['player_name']} ({p['player_id']}) — fetching from NBA API")
            entry = _fetch_player_info(p["player_id"], p["player_name"], p["team"])
            if entry:
                db.append(entry)
                db_ids.add(p["player_id"])
                added.append(p["player_name"])
                log(f"Added {p['player_name']} to players.json")
        p["in_db"] = True  # always true now — either was there or just added

    if added:
        db_path.write_text(json.dumps(db, indent=2, ensure_ascii=False))
        log(f"players.json updated with: {added}")

    return {"date": date_label, "games": True, "players": top5}


def _fetch_player_info(player_id: int, name: str, team: str) -> dict:
    """Fetch basic player info from NBA API and return a players.json-compatible entry."""
    try:
        from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
        time.sleep(0.6)
        info = CommonPlayerInfo(player_id=player_id, timeout=30)
        df = info.common_player_info.get_data_frame()
        if df.empty:
            raise ValueError("Empty response")
        row = df.iloc[0]
        return {
            "id": player_id,
            "name": name,
            "position": str(row.get("POSITION", "Guard")),
            "height": str(row.get("HEIGHT", "")),
            "weight": str(row.get("WEIGHT", "")),
            "country": str(row.get("COUNTRY", "USA")),
            "draft_year": str(row.get("DRAFT_YEAR", "")),
            "draft_round": str(row.get("DRAFT_ROUND", "")),
            "draft_number": str(row.get("DRAFT_NUMBER", "")),
            "from_year": int(row.get("FROM_YEAR", 2020)),
            "to_year": int(row.get("TO_YEAR", 2026)),
            "greatest_75": False,
            "games_played": 0,
            "ppg": 0.0,
            "rpg": 0.0,
            "apg": 0.0,
            "spg": 0.0,
            "bpg": 0.0,
            "fg_pct": 0.0,
            "ft_pct": 0.0,
            "total_points": 0,
            "total_rebounds": 0,
            "total_assists": 0,
            "teams": [team],
            "awards": {
                "championships": 0, "mvps": 0, "finals_mvps": 0,
                "all_star": 0, "all_nba": 0, "all_defensive": 0,
                "scoring_champion": 0, "rookie_of_the_year": 0, "dpoy": 0
            },
            "main_team": team,
            "jersey": str(row.get("JERSEY", "")),
        }
    except Exception as e:
        log(f"Could not fetch info for {name} ({player_id}): {e}")
        return None


def main():
    log("=== fetch_last_night.py started ===")
    try:
        result = fetch_top5()
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    log(f"Saved to {OUTPUT_FILE}")

    # Commit and push
    import subprocess
    date_label = result["date"]
    cmds = [
        ["git", "-C", str(REPO_ROOT), "add", str(OUTPUT_FILE), str(REPO_ROOT / "players.json")],
        ["git", "-C", str(REPO_ROOT), "commit", "-m", f"data: last night top5 {date_label}"],
        ["git", "-C", str(REPO_ROOT), "push"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            log(f"CMD FAILED: {' '.join(cmd)}\n{r.stderr}")
        else:
            log(f"OK: {' '.join(cmd)}")

    log("=== done ===")


if __name__ == "__main__":
    main()
