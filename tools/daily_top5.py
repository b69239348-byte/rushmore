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
        timeout=60,
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

def _build_captions(players: list[dict], game_date: date) -> dict[str, str]:
    """Build platform-specific captions for TikTok, Instagram, X."""
    def short(p: dict) -> str:
        parts = p["name"].split()
        last = parts[-2] if parts[-1] in ("Jr.", "Sr.", "II", "III", "IV") else parts[-1]
        return f"{last} {p['pts']}/{p['reb']}/{p['ast']}"

    highlights = " · ".join(short(p) for p in players[:3])
    leader = players[0]
    leader_last = short(leader).split()[0]
    date_str = game_date.strftime("%b %-d")

    tiktok = (
        f"Top Performers — {date_str} 🔥\n"
        f"\n"
        f"{highlights}\n"
        f"\n"
        f"Would any of them make your Mt. Rushmore?\n"
        f"#NBA #Basketball #TopPerformers #NBAHighlights #rushmore"
    )

    instagram = (
        f"Top Performers — {date_str} 🔥\n"
        f"\n"
        f"{highlights}\n"
        f"\n"
        f"Who stood out to you last night? Build your own Top 5 👉 rushmore.cards\n"
        f"\n"
        f"#NBA #Basketball #TopPerformers #NBAStats #NBAHighlights #HoopsTalk #rushmore"
    )

    x_text = f"{leader_last} leads last night's Top 5 — {highlights} 🔥 #NBA #Basketball"
    if len(x_text) > 280:
        x_text = x_text[:277] + "..."

    return {"tiktok": tiktok, "instagram": instagram, "x": x_text}


def generate_daily_card(
    game_date: Optional[date] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Fetch top 5 scorers for game_date, generate story + feed cards + captions.

    Outputs to output_dir/top5/ subfolder.
    Returns the top5 subfolder path.
    Default output_dir: output/YYYY-MM-DD/ relative to project root.
    """
    if game_date is None:
        game_date = date.today() - timedelta(days=1)

    project_root = Path(__file__).parent.parent
    if output_dir is None:
        output_dir = project_root / "output" / game_date.isoformat()

    top5_dir = Path(output_dir) / "top5"
    top5_dir.mkdir(parents=True, exist_ok=True)

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

    extra_players = [
        {"id": p["id"], "name": p["name"], "team": p["team"]}
        for p in players
    ]

    date_label = f"{game_date.strftime('%b')} {game_date.day}, {game_date.year}".upper()
    shared_args = dict(
        queries=queries,
        title="TOP PERFORMERS",
        subtitle=date_label,
        background="night_court_outdoor",
        extra_players=extra_players,
        game_stats=game_stats,
    )

    # Story (1080×1920)
    story_path = top5_dir / "story.png"
    generate_card(**shared_args, output_path=str(story_path), card_format="story")

    # Feed (1080×1080)
    feed_path = top5_dir / "feed.png"
    generate_card(**shared_args, output_path=str(feed_path), card_format="feed")

    # Captions
    captions = _build_captions(players, game_date)
    for platform, text in captions.items():
        (top5_dir / f"caption_{platform}.txt").write_text(text, encoding="utf-8")

    return top5_dir


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
    top5_dir = generate_daily_card(game_date=game_date)

    print(f"\n✓ story.png       → {top5_dir / 'story.png'}")
    print(f"✓ feed.png        → {top5_dir / 'feed.png'}")
    print(f"✓ caption_tiktok  → {top5_dir / 'caption_tiktok.txt'}")
    print(f"✓ caption_instagram → {top5_dir / 'caption_instagram.txt'}")
    print(f"✓ caption_x       → {top5_dir / 'caption_x.txt'}")
    print(f"\n--- TikTok Caption ---")
    print((top5_dir / "caption_tiktok.txt").read_text(encoding="utf-8"))
