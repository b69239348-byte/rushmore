"""
Rushmore Daily Content Pipeline — Orchestrator.

Usage:
    python3 tools/daily_pipeline.py
    python3 tools/daily_pipeline.py --date 2026-04-14   # override date
    python3 tools/daily_pipeline.py --dry-run           # skip Telegram
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml

# Allow imports from tools/
sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Card-type → award_type mapping
# ---------------------------------------------------------------------------

CARD_TYPE_TO_AWARD: dict[str, str] = {
    "roty":          "roty",
    "mip":           "mip",
    "scoring_title": "scoring",
    "all_nba":       "all_nba",
    "all_rookie":    "all_rookie",
    "mvp":           "mvp",
    "dpoy":          "dpoy",
}

# Calendar card_type → caption card_type (usually 1:1, but award needs mapping)
_CAPTION_TYPE_MAP: dict[str, str] = {
    "scoring_title":   "scoring_title",
    "mvp_race":        "mvp_race",
    "roty":            "roty",
    "all_nba":         "all_nba",
    "all_rookie":      "all_rookie",
    "debate":          "debate",
    "award":           "award",
    "playoff_matchup": "playoff_matchup",
}


# ---------------------------------------------------------------------------
# 1. Calendar loading
# ---------------------------------------------------------------------------

def _load_calendar() -> list[dict]:
    """Read content/calendar.yaml and return the list of day entries."""
    calendar_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    with open(calendar_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("days", [])


def _find_today(days: list[dict], today_str: str) -> dict | None:
    """Find the calendar entry for today_str (YYYY-MM-DD)."""
    for day in days:
        if str(day.get("date", "")) == today_str:
            return day
    return None


# ---------------------------------------------------------------------------
# 2. Output directory
# ---------------------------------------------------------------------------

def _output_dir(today_str: str) -> Path:
    """Create and return output/YYYY-MM-DD/."""
    out = Path(__file__).parent.parent / "output" / today_str
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# 3. Caption writing
# ---------------------------------------------------------------------------

def _write_captions(captions: dict[str, str], out_dir: Path) -> None:
    """Write tiktok.txt, instagram.txt, x.txt to out_dir/captions/."""
    captions_dir = out_dir / "captions"
    captions_dir.mkdir(parents=True, exist_ok=True)
    for platform, text in captions.items():
        (captions_dir / f"{platform}.txt").write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# 4. Top 5 generation
# ---------------------------------------------------------------------------

def _generate_top5(today_str: str, out_dir: Path) -> list[str]:
    """Call generate_daily_card and copy PNGs into out_dir.

    Returns list of descriptions like 'Top 5 Last Night — Points leaders'.
    """
    from daily_top5 import generate_daily_card

    game_date = datetime.strptime(today_str, "%Y-%m-%d").date()

    # generate_daily_card returns the directory it wrote files to
    tmp_dir = out_dir / "_top5_tmp"
    result = generate_daily_card(game_date=game_date, output_dir=tmp_dir)
    result_dir = Path(result)

    copied = []
    # The main card is named 'card.png' — copy as top5_story.png
    card_png = result_dir / "card.png"
    if card_png.exists():
        shutil.copy2(card_png, out_dir / "top5_story.png")
        copied.append(str(out_dir / "top5_story.png"))

    # If a feed variant exists (card_feed.png or any *feed*.png)
    for candidate in result_dir.glob("*feed*.png"):
        shutil.copy2(candidate, out_dir / "top5_feed.png")
        copied.append(str(out_dir / "top5_feed.png"))
        break

    # Also copy any other PNGs that aren't already handled
    for png in result_dir.glob("*.png"):
        if png.name not in ("card.png",) and "feed" not in png.name:
            dest = out_dir / f"top5_{png.name}"
            shutil.copy2(png, dest)
            copied.append(str(dest))

    return ["Top 5 Last Night — Points leaders"]


# ---------------------------------------------------------------------------
# 5. Planned card generation
# ---------------------------------------------------------------------------

def _generate_planned(planned: dict, today_str: str, out_dir: Path) -> list[str]:
    """Dispatch to the correct generator based on planned.card_type.

    Returns list of descriptions.
    """
    card_type: str = planned.get("card_type", "")
    title: str = planned.get("title", "")
    subtitle: str = planned.get("subtitle", "")

    descriptions: list[str] = []

    # Generate story and feed variants
    for fmt in ("story", "feed"):
        suffix = f"{card_type}_{fmt}.png"
        output_path = str(out_dir / suffix)

        try:
            if card_type == "debate":
                from generate_debate_card import generate_debate_card
                items = planned.get("items", [])
                generate_debate_card(
                    title=title,
                    subtitle=subtitle,
                    items=items,
                    output_path=output_path,
                    card_format=fmt,
                    bg=planned.get("bg"),
                )

            elif card_type == "mvp_race":
                from generate_mvp_race_card import generate_mvp_race_card
                generate_mvp_race_card(
                    output_path=output_path,
                    card_format=fmt,
                )

            elif card_type in CARD_TYPE_TO_AWARD:
                # award, scoring_title, roty, all_nba, all_rookie, mip, dpoy, mvp
                from generate_award_card import generate_award_card
                award_type = planned.get("award_type") or CARD_TYPE_TO_AWARD[card_type]
                items = planned.get("items")  # may be None for auto_data cards
                auto_data = planned.get("auto_data", True)
                generate_award_card(
                    award_type=award_type,
                    items=items,
                    auto_data=auto_data,
                    output_path=output_path,
                    card_format=fmt,
                )

            elif card_type == "award":
                from generate_award_card import generate_award_card
                award_type = planned.get("award_type", "")
                items = planned.get("items")
                auto_data = planned.get("auto_data", True)
                generate_award_card(
                    award_type=award_type,
                    items=items,
                    auto_data=auto_data,
                    output_path=output_path,
                    card_format=fmt,
                )

            elif card_type == "playoff_matchup":
                from generate_playoff_card import generate_playoff_card
                matchup_index = planned.get("matchup_index", 0)
                generate_playoff_card(
                    matchup_index=matchup_index,
                    output_path=output_path,
                    card_format=fmt,
                )

            else:
                print(f"  [WARN] Unknown card_type '{card_type}' — skipping {fmt}")
                continue

            print(f"  [OK] {suffix}")

        except Exception as exc:
            print(f"  [ERROR] Failed to generate {suffix}: {exc}")
            continue

    if card_type:
        descriptions.append(f"{title} — {subtitle}" if subtitle else title)

    return descriptions


# ---------------------------------------------------------------------------
# 6. Telegram
# ---------------------------------------------------------------------------

def _send_telegram(
    story_paths: list[str],
    message: str,
    dry_run: bool = False,
) -> None:
    """Send a text summary + photos to Telegram."""
    if dry_run:
        print("\n[DRY RUN] Telegram message:")
        print(message)
        print("\n[DRY RUN] Would send photos:")
        for p in story_paths:
            print(f"  {p}")
        return

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("[WARN] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — skipping Telegram")
        return

    import requests

    base_url = f"https://api.telegram.org/bot{token}"

    # Send text summary
    resp = requests.post(
        f"{base_url}/sendMessage",
        json={"chat_id": chat_id, "text": message},
        timeout=30,
    )
    if not resp.ok:
        print(f"  [ERROR] sendMessage failed: {resp.status_code} {resp.text}")
    else:
        print("  [OK] Telegram message sent")

    # Send each story PNG
    for path in story_paths:
        p = Path(path)
        if not p.exists():
            print(f"  [WARN] Image not found: {path}")
            continue
        with open(p, "rb") as photo_file:
            resp = requests.post(
                f"{base_url}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": photo_file},
                timeout=60,
            )
        if not resp.ok:
            print(f"  [ERROR] sendPhoto failed for {p.name}: {resp.status_code} {resp.text}")
        else:
            print(f"  [OK] Sent photo: {p.name}")


# ---------------------------------------------------------------------------
# 7. Main run function
# ---------------------------------------------------------------------------

def run(today_str: str, dry_run: bool = False) -> list[str]:
    """Run the full daily pipeline. Returns list of generated file paths."""
    print(f"\n=== Rushmore Daily Pipeline — {today_str} ===\n")

    # Create output directory
    out_dir = _output_dir(today_str)
    print(f"Output directory: {out_dir}\n")

    all_descriptions: list[str] = []
    all_story_paths: list[str] = []

    # Step 1: Generate Top 5 card
    print("--- Step 1: Top 5 Card ---")
    try:
        descs = _generate_top5(today_str, out_dir)
        all_descriptions.extend(descs)
        story = out_dir / "top5_story.png"
        if story.exists():
            all_story_paths.append(str(story))
            print(f"  [OK] top5_story.png")
        else:
            print("  [WARN] top5_story.png not found after generation")
    except Exception as exc:
        print(f"  [ERROR] Top 5 generation failed: {exc}")

    # Step 2: Generate planned card from calendar
    print("\n--- Step 2: Planned Card ---")
    days = _load_calendar()
    day_entry = _find_today(days, today_str)

    planned_card_type = ""
    if day_entry is None:
        print(f"  [WARN] No calendar entry for {today_str} — skipping planned card")
    else:
        planned = day_entry.get("planned", {})
        planned_card_type = planned.get("card_type", "")
        if not planned_card_type:
            print("  [WARN] No card_type in calendar entry — skipping")
        else:
            print(f"  card_type: {planned_card_type}")
            try:
                descs = _generate_planned(planned, today_str, out_dir)
                all_descriptions.extend(descs)
                story = out_dir / f"{planned_card_type}_story.png"
                if story.exists():
                    all_story_paths.append(str(story))
            except Exception as exc:
                print(f"  [ERROR] Planned card generation failed: {exc}")

    # Step 3: Write captions
    print("\n--- Step 3: Captions ---")
    if day_entry and planned_card_type:
        planned = day_entry.get("planned", {})
        caption_card_type = _CAPTION_TYPE_MAP.get(planned_card_type, planned_card_type)
        try:
            from caption_templates import get_captions
            captions = get_captions(
                caption_card_type,
                date=today_str,
                title=planned.get("title", ""),
                award_type=planned.get("award_type", ""),
            )
            _write_captions(captions, out_dir)
            print(f"  [OK] Captions written to {out_dir / 'captions'}/")
        except Exception as exc:
            print(f"  [ERROR] Caption generation failed: {exc}")
    else:
        print("  [SKIP] No calendar entry — no captions to write")

    # Step 4: Telegram
    print("\n--- Step 4: Telegram ---")
    card_count = len(all_descriptions)
    card_list = "\n".join(
        f"{i + 1}. {desc}" for i, desc in enumerate(all_descriptions)
    )
    telegram_message = (
        f"📅 {today_str} — {card_count} card{'s' if card_count != 1 else ''} ready:\n\n"
        f"{card_list}"
    )

    _send_telegram(all_story_paths, telegram_message, dry_run=dry_run)

    print(f"\n=== Pipeline complete. {len(all_story_paths)} story images generated. ===\n")
    return all_story_paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Rushmore Daily Content Pipeline Orchestrator"
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Override date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip Telegram, just print what would be sent",
    )
    args = parser.parse_args()

    today_str = args.date or date.today().isoformat()

    run(today_str=today_str, dry_run=args.dry_run)
