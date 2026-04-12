"""Unit tests for caption_templates.py (TDD)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from caption_templates import get_captions  # noqa: E402

PLAYERS_TOP5 = [
    {"name": "Nikola Jokic", "ppg": 27.4, "eff": 34.1},
    {"name": "Shai Gilgeous-Alexander", "ppg": 25.8, "eff": 30.2},
    {"name": "Giannis Antetokounmpo", "ppg": 29.1, "eff": 31.8},
    {"name": "Luka Doncic", "ppg": 28.7, "eff": 29.5},
    {"name": "Joel Embiid", "ppg": 26.1, "eff": 28.3},
]


def test_top5_captions_have_all_platforms():
    result = get_captions("top5", players=PLAYERS_TOP5, date="2026-04-12")
    assert set(result.keys()) == {"tiktok", "instagram", "x"}
    assert result["tiktok"]
    assert result["instagram"]
    assert result["x"]


def test_top5_tiktok_contains_hook():
    result = get_captions("top5", players=PLAYERS_TOP5, date="2026-04-12")
    assert "#NBA" in result["tiktok"]


def test_mvp_race_captions():
    players = [{"name": "Nikola Jokic", "ppg": 27.4, "eff": 34.1}]
    result = get_captions("mvp_race", players=players)
    tiktok = result["tiktok"].lower()
    assert "mvp" in tiktok


def test_debate_captions():
    result = get_captions("debate", title="Is Jokic the GOAT PG?")
    assert len(result["x"]) <= 280
    assert "rushmore.cards" in result["instagram"]


def test_award_captions():
    players = [{"name": "Herb Jones", "ppg": 11.2}]
    result = get_captions("award", players=players, award_type="mip")
    assert result["tiktok"]  # non-empty


def test_playoff_matchup_captions():
    matchup = {
        "home_team": "Denver Nuggets",
        "away_team": "LA Lakers",
        "home_wins": 2,
        "away_wins": 1,
    }
    result = get_captions("playoff_matchup", matchup=matchup)
    assert "Nuggets" in result["x"] or "Lakers" in result["x"] or "Denver" in result["x"] or "LA" in result["x"]


def test_top5_injects_player_name():
    players = [{"name": "Nikola Jokic", "ppg": 27.4, "team": "DEN"}]
    result = get_captions("top5", players=players, date="2026-04-12")
    assert "Nikola Jokic" in result["tiktok"]
    assert "27.4" in result["tiktok"]


def test_award_injects_player_name():
    players = [{"name": "Herb Jones", "ppg": 11.2, "team": "NOP"}]
    result = get_captions("award", players=players, award_type="dpoy")
    assert "Herb Jones" in result["tiktok"]
    assert "DPOY" in result["tiktok"]


def test_mvp_race_injects_efficiency():
    players = [{"name": "Nikola Jokic", "ppg": 27.4, "eff": 34.1, "team": "DEN"}]
    result = get_captions("mvp_race", players=players)
    assert "Nikola Jokic" in result["tiktok"]
    assert "34.1" in result["tiktok"]


def test_x_caption_trim_at_280():
    long_title = "A" * 300
    result = get_captions("debate", title=long_title)
    assert len(result["x"]) <= 280
    assert result["x"].endswith("...")


def test_fetch_playoff_bracket_returns_list():
    """fetch_playoff_bracket returns a list — empty during regular season is fine."""
    from live_data import fetch_playoff_bracket
    bracket = fetch_playoff_bracket()
    assert isinstance(bracket, list)
    # During regular season: empty list is valid
    for matchup in bracket:
        assert "home_team" in matchup
        assert "away_team" in matchup
        assert "home_wins" in matchup
        assert "away_wins" in matchup
        assert "conference" in matchup
