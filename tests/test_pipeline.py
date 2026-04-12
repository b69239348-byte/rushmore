"""Unit tests for caption_templates.py (TDD)."""

import sys
import yaml
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


def test_calendar_loads_20_days():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    assert len(data["days"]) == 20


def test_calendar_all_days_have_date_and_planned():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    for day in data["days"]:
        assert "date" in day, f"Missing date: {day}"
        assert "planned" in day, f"Missing planned: {day}"
        assert "card_type" in day["planned"], f"Missing card_type: {day}"


def test_calendar_debate_cards_have_5_items():
    cal_path = Path(__file__).parent.parent / "content" / "calendar.yaml"
    data = yaml.safe_load(cal_path.read_text())
    for day in data["days"]:
        planned = day["planned"]
        if planned["card_type"] == "debate":
            assert "items" in planned, f"Debate card missing items: {day['date']}"
            assert len(planned["items"]) == 5, f"Debate card needs 5 items: {day['date']}"


def test_all_card_types_produce_x_under_280_chars():
    """All caption types produce X captions under 280 characters."""
    test_cases = [
        ("top5",            {"players": [{"name": "Luka Doncic", "ppg": 32.4, "team": "DAL"}], "date": "2026-04-12"}),
        ("mvp_race",        {"players": [{"name": "SGA", "ppg": 31.2, "eff": 28.5, "team": "OKC"}], "date": "2026-04-12"}),
        ("debate",          {"title": "Regular Season Frauds", "date": "2026-04-17"}),
        ("playoff_matchup", {"matchup": {"home_team": "OKC Thunder", "away_team": "Dallas Mavericks", "home_wins": 2, "away_wins": 1}, "date": "2026-04-19"}),
        ("award",           {"players": [{"name": "Chet Holmgren", "team": "OKC", "ppg": 18.2}], "award_type": "mip", "date": "2026-04-24"}),
        ("scoring_title",   {"players": [{"name": "SGA", "ppg": 31.2, "team": "OKC"}], "date": "2026-04-12"}),
        ("roty",            {"players": [{"name": "Victor Wembanyama", "ppg": 27.0, "team": "SAS"}], "date": "2026-04-13"}),
    ]
    for card_type, kwargs in test_cases:
        captions = get_captions(card_type, **kwargs)
        assert len(captions["x"]) <= 280, f"X caption too long for {card_type}: {len(captions['x'])} chars\n{captions['x']}"
