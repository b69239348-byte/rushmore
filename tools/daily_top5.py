"""
Daily Top 5 Performers — fetches yesterday's NBA top scorers
and generates a shareable card + caption.

Usage:
    python3 tools/daily_top5.py              # uses yesterday
    python3 tools/daily_top5.py 2025-03-01   # specific date
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# generate_card lives in the same tools/ directory
sys.path.insert(0, str(Path(__file__).parent))
from generate_card import generate_card  # noqa: E402


def fetch_top5_scorers(game_date: Optional[date] = None) -> list[dict]:
    """Return the top 5 scorers for a given date, sorted by PTS descending.

    Each dict has: id, name, team, pts, reb, ast, stl, blk
    """
    if game_date is None:
        game_date = date.today() - timedelta(days=1)

    from nba_api.stats.endpoints import leaguegamelog

    date_str = game_date.strftime("%m/%d/%Y")

    from live_data import _season_for_date
    season = _season_for_date(game_date)

    logs = leaguegamelog.LeagueGameLog(
        season=season,
        date_from_nullable=date_str,
        date_to_nullable=date_str,
        player_or_team_abbreviation="P",
        sorter="PTS",
        direction="DESC",
    )
    df = logs.get_data_frames()[0]

    if df.empty:
        raise ValueError(f"No game data found for {game_date.isoformat()}")

    top5 = df.head(5)
    if len(top5) < 5:
        raise ValueError(
            f"Only {len(top5)} player rows for {game_date.isoformat()}, expected 5"
        )

    players = []
    for _, row in top5.iterrows():
        players.append({
            "id":   int(row["PLAYER_ID"]),
            "name": str(row["PLAYER_NAME"]),
            "team": str(row.get("TEAM_ABBREVIATION", "")),
            "pts":  int(row["PTS"]),
            "reb":  int(row["REB"]),
            "ast":  int(row["AST"]),
            "stl":  int(row["STL"]),
            "blk":  int(row["BLK"]),
        })

    return players


# ── Card + caption generation ─────────────────────────────────────────────────

def _build_caption(players: list[dict], game_date: date) -> str:
    """Build ready-to-paste social media caption."""
    # Top 3 as compact "name pts/reb/ast" highlights
    def short(p: dict) -> str:
        parts = p["name"].split()
        last = parts[-2] if parts[-1] in ("Jr.", "Sr.", "II", "III", "IV") else parts[-1]
        return f"{last} {p['pts']}/{p['reb']}/{p['ast']}"

    highlights = " · ".join(short(p) for p in players[:3])

    lines = [
        f"Top Performers last night 🔥",
        "",
        highlights,
        "",
        "Would any of them make your Mt. Rushmore?",
        "Build your list 👉 rushmore.app",
        "",
        "#NBA #Basketball #Rushmore",
    ]
    return "\n".join(lines)


def generate_daily_card(
    game_date: Optional[date] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Fetch top 5 scorers for game_date, generate card + caption, write to output_dir.

    Returns the output directory path.
    Default output_dir: ~/Desktop/rushmore/YYYY-MM-DD/
    """
    if game_date is None:
        game_date = date.today() - timedelta(days=1)

    if output_dir is None:
        output_dir = Path.home() / "Desktop" / "rushmore" / game_date.isoformat()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch data
    players = fetch_top5_scorers(game_date=game_date)

    # Download missing headshots from NBA CDN
    from download_headshots import download_by_ids
    player_ids = [p["id"] for p in players]
    names = {p["id"]: p["name"] for p in players}
    download_by_ids(player_ids, names)

    # Build player queries + game_stats override for generate_card()
    queries = [str(p["id"]) for p in players]
    game_stats = {
        p["id"]: {
            "pts": p["pts"], "reb": p["reb"], "ast": p["ast"],
            "stl": p["stl"], "blk": p["blk"],
        }
        for p in players
    }

    # Enrich with live team info
    # Provides team abbreviation override for generate_card's live_by_id lookup.
    # Players missing from the local DB will render without a headshot.
    extra_players = [
        {"id": p["id"], "name": p["name"], "team": p["team"]}
        for p in players
    ]

    date_label = f"{game_date.strftime('%b')} {game_date.day}, {game_date.year}".upper()
    card_path = output_dir / "card.png"

    generate_card(
        queries=queries,
        title="TOP PERFORMERS",
        subtitle=date_label,
        output_path=str(card_path),
        background="night_court_outdoor",
        extra_players=extra_players,
        game_stats=game_stats,
    )

    # Write caption
    caption = _build_caption(players, game_date)
    caption_path = output_dir / "caption.txt"
    caption_path.write_text(caption, encoding="utf-8")

    return output_dir


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Rushmore Daily Top 5 card")
    parser.add_argument(
        "date",
        nargs="?",
        help="Game date in YYYY-MM-DD format (default: yesterday)",
    )
    args = parser.parse_args()

    if args.date:
        from datetime import datetime
        game_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        game_date = date.today() - timedelta(days=1)

    print(f"Fetching top performers for {game_date.isoformat()}...")
    out_dir = generate_daily_card(game_date=game_date)

    print(f"\n✓ Card saved to:    {out_dir / 'card.png'}")
    print(f"✓ Caption saved to: {out_dir / 'caption.txt'}")
    print(f"\n--- Caption preview ---")
    print((out_dir / "caption.txt").read_text(encoding="utf-8"))
