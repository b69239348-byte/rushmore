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


_PLAYOFFS_START = date(2026, 4, 18)  # update each season

_CARD_COLORS = [
    "yellow/orange",
    "cyan/blue",
    "pink/magenta",
    "orange/red",
    "purple/violet",
]


def _composite_score(row) -> float:
    """Impact score: PTS + 0.7·REB + 1.5·AST + 2·STL + 2·BLK + efficiency bonus.

    Efficiency bonus: up to +3 pts for FG% above 50% (scales with attempts),
    weighted by FGA so low-volume players don't unfairly benefit.
    """
    base = (
        row["PTS"]
        + 0.7 * row["REB"]
        + 1.5 * row["AST"]
        + 2.0 * row["STL"]
        + 2.0 * row["BLK"]
    )
    fga = row.get("FGA", 0)
    fg_pct = row.get("FG_PCT", 0)
    # Only apply bonus when player took meaningful shots (>=8 FGA)
    if fga >= 8 and fg_pct > 0.50:
        efficiency_bonus = min(3.0, (fg_pct - 0.50) * fga)
    else:
        efficiency_bonus = 0.0
    return base + efficiency_bonus


def fetch_top5_scorers(game_date: Optional[date] = None) -> list[dict]:
    """Return the top 5 performers for a given date, ranked by composite impact score.

    Each dict has: id, name, team, pts, reb, ast, stl, blk
    """
    if game_date is None:
        game_date = date.today() - timedelta(days=1)

    from nba_api.stats.endpoints import leaguegamelog
    from live_data import _season_for_date

    date_str = game_date.strftime("%m/%d/%Y")
    season = _season_for_date(game_date)
    season_type = "Playoffs" if game_date >= _PLAYOFFS_START else "Regular Season"

    logs = leaguegamelog.LeagueGameLog(
        season=season,
        season_type_all_star=season_type,
        date_from_nullable=date_str,
        date_to_nullable=date_str,
        player_or_team_abbreviation="P",
        timeout=60,
    )
    df = logs.get_data_frames()[0]

    if df.empty:
        raise ValueError(f"No game data found for {game_date.isoformat()}")

    df["_score"] = df.apply(_composite_score, axis=1)
    df = df.sort_values(["_score", "PTS"], ascending=False)

    top5 = df.head(5)
    if len(top5) < 5:
        print(f"[WARN] Only {len(top5)} player rows for {game_date.isoformat()}, expected 5 — continuing with fewer")

    players = []
    for _, row in top5.iterrows():
        players.append({
            "id":      int(row["PLAYER_ID"]),
            "name":    str(row["PLAYER_NAME"]),
            "team":    str(row.get("TEAM_ABBREVIATION", "")),
            "pts":     int(row["PTS"]),
            "reb":     int(row["REB"]),
            "ast":     int(row["AST"]),
            "stl":     int(row["STL"]),
            "blk":     int(row["BLK"]),
            "fgm":     int(row.get("FGM", 0)),
            "fga":     int(row.get("FGA", 0)),
            "fg_pct":  round(float(row.get("FG_PCT", 0)) * 100, 1),
            "fg3m":    int(row.get("FG3M", 0)),
            "fg3a":    int(row.get("FG3A", 0)),
            "fg3_pct": round(float(row.get("FG3_PCT", 0)) * 100, 1),
            "wl":      str(row.get("WL", "")),
        })

    # Fetch jersey numbers
    import time
    from nba_api.stats.endpoints import commonplayerinfo
    for p in players:
        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=p["id"], timeout=30)
            row = info.get_data_frames()[0].iloc[0]
            p["jersey"] = str(row["JERSEY"])
            p["team_full"] = f"{row['TEAM_CITY']} {row['TEAM_NAME']}"
        except Exception:
            p["jersey"] = ""
            p["team_full"] = p["team"]
        time.sleep(0.3)

    return players


# ── Card + caption generation ─────────────────────────────────────────────────

def _build_captions(players: list[dict], game_date: date) -> dict[str, str]:
    """Build platform-specific captions for TikTok, Instagram, X."""
    def last_name(p: dict) -> str:
        parts = p["name"].split()
        return parts[-2] if parts[-1] in ("Jr.", "Sr.", "II", "III", "IV") else parts[-1]

    def short(p: dict) -> str:
        return f"{last_name(p)} {p['pts']}/{p['reb']}/{p['ast']}"

    highlights = " · ".join(short(p) for p in players[:3])
    leader = players[0]
    leader_name = last_name(leader)
    leader_pts = leader["pts"]

    is_playoffs = game_date >= _PLAYOFFS_START
    playoff_night = (game_date - _PLAYOFFS_START).days + 1

    if is_playoffs:
        context_line = f"Playoffs Night {playoff_night} 🏆"
        hashtags_5 = "#NBA #NBAPlayoffs #Playoffs2026 #NBAHighlights #rushmore"
        x_suffix = "#NBA #NBAPlayoffs"
    else:
        context_line = "Last night's top performers 🔥"
        hashtags_5 = "#NBA #Basketball #TopPerformers #NBAHighlights #rushmore"
        x_suffix = "#NBA #Basketball"

    # Win/loss hook for the leader
    leader_wl = leader.get("wl", "")
    if leader_wl == "L":
        leader_hook = f"{leader_name} dropped {leader_pts} — but the {leader['team']} still lost."
    elif leader_wl == "W":
        leader_hook = f"{leader_name} dropped {leader_pts} in the W 🔥"
    else:
        leader_hook = f"{leader_name} dropped {leader_pts} 🔥"

    # TikTok: hook first, then stats, then engagement question (max 5 hashtags)
    tiktok = (
        f"{context_line}\n"
        f"\n"
        f"{leader_hook}\n"
        f"\n"
        f"{highlights}\n"
        f"\n"
        f"Who's your surprise performer? 🏀\n"
        f"{hashtags_5}"
    )

    # Instagram: editorial, max 5 hashtags
    instagram = (
        f"{context_line}\n"
        f"\n"
        f"{highlights}\n"
        f"\n"
        f"{leader_hook} Who impressed you most?\n"
        f"Build your own Mt. Rushmore 👉 rushmore.cards\n"
        f"\n"
        f"{hashtags_5}"
    )

    # X: punchy, no name repeat, under 280
    rest = " · ".join(short(p) for p in players[1:3])
    wl_note = " (L)" if leader_wl == "L" else ""
    x_text = f"{leader_name} drops {leader_pts}{wl_note} 🔥 {rest} — who's your Top 5? {x_suffix}"
    if len(x_text) > 280:
        x_text = x_text[:277] + "..."

    return {"tiktok": tiktok, "instagram": instagram, "x": x_text}


def _build_player_card_prompts(players: list[dict], card_title: str) -> str:
    """Build 5 individual Midjourney prompts for the slideshow player cards."""
    blocks = []
    for i, p in enumerate(players):
        color = _CARD_COLORS[i]
        name_upper = p["name"].upper()
        jersey = p.get("jersey", "?")
        team_full = p.get("team_full", p.get("team", ""))
        block = (
            f"=== PLAYER {i + 1}: {p['name']} ===\n"
            f"\n"
            f"Create a dynamic comic-book trading card in the exact same style as the \"{card_title}\" collage.\n"
            f"Use the Jalen Johnson single card as secondary style reference for quality, line work, energy, color intensity and branding.\n"
            f"\n"
            f"Player: {p['name']} (#{jersey} {team_full})\n"
            f"Stats:\n"
            f"- PTS: {p['pts']}\n"
            f"- REB: {p['reb']}\n"
            f"- AST: {p['ast']}\n"
            f"\n"
            f"Requirements:\n"
            f"- Explosive comic background with speed lines and star bursts — use strong {color} tones\n"
            f"- \"{card_title}\" title at the very top in the exact same font and style\n"
            f"- Stats box in the bottom-left corner (white box, bold black text) like in the collage\n"
            f"- Large bold player name \"{name_upper}\" at the bottom center\n"
            f"- Bottom right corner: \"RUSHMORE.CARDS • BUILD YOURS\" in the exact same font, size and position\n"
            f"- Vintage paper texture, worn edges, halftone dots, strong black outlines\n"
            f"- High energy action pose (dribble or drive to the basket)\n"
            f"\n"
            f"Make it look like it perfectly belongs in the same series as the big collage.\n"
            f"\n"
            f"--ref1: [manga collage]\n"
            f"--ref2: [Jalen Johnson Einzelbild]\n"
            f"--stylize: 700"
        )
        blocks.append(block)
    return ("\n\n" + "-" * 60 + "\n\n").join(blocks)


def generate_daily_card(
    game_date: Optional[date] = None,
    output_dir: Optional[Path] = None,
    background: Optional[str] = None,
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
        background=background or "night_court_outdoor",
        extra_players=extra_players,
        game_stats=game_stats,
    )

    # Story (1080×1920)
    story_path = top5_dir / "story.png"
    generate_card(**shared_args, output_path=str(story_path), card_format="story")

    # Captions
    captions = _build_captions(players, game_date)
    for platform, text in captions.items():
        (top5_dir / f"caption_{platform}.txt").write_text(text, encoding="utf-8")

    # Higgsfield prompt
    is_playoffs = game_date >= _PLAYOFFS_START
    playoff_night = (game_date - _PLAYOFFS_START).days + 1
    card_title = f"PLAYOFFS NIGHT {playoff_night}" if is_playoffs else f"TOP 5 — {date_label}"
    player_lines = "\n".join(
        f"- {p['name']} (#{p.get('jersey', '?')} {p.get('team_full', p['team'])}): PTS {p['pts']}, REB {p['reb']}, AST {p['ast']}"
        for p in players
    )
    higgsfield_prompt = (
        f"Japanese manga anime style NBA card, 5 basketball players\n"
        f"in diamond/pentagon layout, each in dynamic action pose,\n"
        f"bold manga ink lines, screen tone shading,\n"
        f"dramatic speed lines in background,\n"
        f"each panel different color: gold, cyan, pink, orange, purple,\n"
        f"large manga style title at top: \"{card_title}\",\n"
        f"stats in manga caption boxes per player — exactly 3 stats each: PTS, REB, AST,\n"
        f"bottom label: \"RUSHMORE.CARDS · BUILD YOURS\",\n"
        f"players:\n"
        f"{player_lines}\n"
        f"vertical 9:16 format\n"
        f"\n"
        f"(Style reference: karte_gptimage2.PNG)"
    )
    (top5_dir / "higgsfield_prompt.txt").write_text(higgsfield_prompt, encoding="utf-8")

    # Individual player card prompts for Midjourney slideshow
    player_card_prompts = _build_player_card_prompts(players, card_title)
    (top5_dir / "player_card_prompts.txt").write_text(player_card_prompts, encoding="utf-8")

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
    parser.add_argument(
        "--background", "-b",
        help="Background name to use (overrides default)",
    )
    args = parser.parse_args()

    if args.date:
        from datetime import datetime
        game_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    else:
        game_date = date.today() - timedelta(days=1)

    print(f"Fetching top performers for {game_date.isoformat()}...")
    top5_dir = generate_daily_card(game_date=game_date, background=args.background)

    print(f"\n✓ story.png            → {top5_dir / 'story.png'}")
    print(f"✓ caption_tiktok       → {top5_dir / 'caption_tiktok.txt'}")
    print(f"✓ caption_instagram    → {top5_dir / 'caption_instagram.txt'}")
    print(f"✓ caption_x            → {top5_dir / 'caption_x.txt'}")
    print(f"✓ higgsfield_prompt    → {top5_dir / 'higgsfield_prompt.txt'}")
    print(f"✓ player_card_prompts  → {top5_dir / 'player_card_prompts.txt'}")

    print(f"\n--- Caption X ---")
    print((top5_dir / "caption_x.txt").read_text(encoding="utf-8"))
    print(f"\n--- Caption Instagram ---")
    print((top5_dir / "caption_instagram.txt").read_text(encoding="utf-8"))
    print(f"\n--- Caption TikTok ---")
    print((top5_dir / "caption_tiktok.txt").read_text(encoding="utf-8"))
    print(f"\n--- Higgsfield Prompt ---")
    print((top5_dir / "higgsfield_prompt.txt").read_text(encoding="utf-8"))
