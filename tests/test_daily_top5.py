import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import tempfile
from generate_card import generate_card, load_players

def test_generate_card_with_game_stats_runs_without_error():
    """generate_card() with game_stats should produce a PNG without crashing."""
    players = load_players()
    pid = players[0]["id"]

    game_stats = {
        pid: {"pts": 38, "reb": 14, "ast": 9, "stl": 2, "blk": 1}
    }

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name

    generate_card(
        queries=[str(pid)],
        title="TEST CARD",
        subtitle="GAME STATS",
        output_path=out,
        game_stats=game_stats,
    )

    assert os.path.exists(out)
    assert os.path.getsize(out) > 10_000


def test_generate_card_feed_format_produces_correct_dimensions():
    """generate_card() with card_format='feed' must produce 1080x1350 PNG."""
    import tempfile
    from pathlib import Path
    from PIL import Image

    players = ["LeBron James", "Michael Jordan", "Kobe Bryant", "Magic Johnson", "Larry Bird"]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name

    generate_card(players, card_format="feed", output_path=out)
    img = Image.open(out)
    assert img.size == (1080, 1350), f"Expected (1080, 1350), got {img.size}"
    Path(out).unlink()


def test_fetch_top5_returns_five_players():
    """fetch_top5_scorers() should return exactly 5 player dicts with required keys."""
    from daily_top5 import fetch_top5_scorers
    from datetime import date

    test_date = date(2025, 3, 1)
    players = fetch_top5_scorers(game_date=test_date)

    assert len(players) == 5
    for p in players:
        assert "id" in p
        assert "name" in p
        assert "team" in p
        assert "pts" in p
        assert "reb" in p
        assert "ast" in p
        assert "stl" in p
        assert "blk" in p
        assert isinstance(p["pts"], int)


def test_fetch_top5_scorers_sorted_by_pts():
    """Players should be sorted by PTS descending."""
    from daily_top5 import fetch_top5_scorers
    from datetime import date

    test_date = date(2025, 3, 1)
    players = fetch_top5_scorers(game_date=test_date)

    pts_values = [p["pts"] for p in players]
    assert pts_values == sorted(pts_values, reverse=True)


def test_generate_daily_card_creates_output_files(tmp_path):
    """generate_daily_card() should write card.png and caption.txt to the output dir."""
    from daily_top5 import generate_daily_card
    from datetime import date

    test_date = date(2025, 3, 1)
    out_dir = tmp_path / "2025-03-01"

    generate_daily_card(game_date=test_date, output_dir=out_dir)

    assert (out_dir / "card.png").exists()
    assert (out_dir / "card.png").stat().st_size > 50_000

    assert (out_dir / "caption.txt").exists()
    caption = (out_dir / "caption.txt").read_text(encoding="utf-8")
    assert "Top Performers" in caption
    assert "rushmore.app" in caption
    assert "PTS" in caption
