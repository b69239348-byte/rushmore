"""Tests that live NBA endpoints use in-memory cache."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from fastapi.testclient import TestClient


def _make_players(n=3):
    return [{"id": i, "name": f"Player {i}", "ppg": 20.0, "rpg": 5.0, "apg": 3.0} for i in range(n)]


def test_current_mvp_caches_after_first_call():
    """Second call must not hit NBA API again."""
    import server
    server._api_cache.clear()

    players = _make_players()
    with patch("server.fetch_current_mvp_race", return_value=players) as mock_fetch:
        client = TestClient(server.app)
        client.get("/api/categories/current-mvp")
        client.get("/api/categories/current-mvp")
        assert mock_fetch.call_count == 1, "NBA API should only be called once"


def test_current_dpoy_caches_after_first_call():
    import server
    server._api_cache.clear()

    players = _make_players()
    with patch("server.fetch_current_dpoy_race", return_value=players) as mock_fetch:
        client = TestClient(server.app)
        client.get("/api/categories/current-dpoy")
        client.get("/api/categories/current-dpoy")
        assert mock_fetch.call_count == 1


def test_current_roy_caches_after_first_call():
    import server
    server._api_cache.clear()

    players = _make_players()
    with patch("server.fetch_current_roy_race", return_value=players) as mock_fetch:
        client = TestClient(server.app)
        client.get("/api/categories/current-roy")
        client.get("/api/categories/current-roy")
        assert mock_fetch.call_count == 1


def test_current_mip_caches_after_first_call():
    import server
    server._api_cache.clear()

    players = _make_players()
    with patch("server.fetch_current_mip_race", return_value=players) as mock_fetch:
        client = TestClient(server.app)
        client.get("/api/categories/current-mip")
        client.get("/api/categories/current-mip")
        assert mock_fetch.call_count == 1


def test_all_nba_tier_caches_per_tier():
    import server
    server._api_cache.clear()

    players = _make_players()
    with patch("server.fetch_all_nba_tier", return_value=players) as mock_fetch:
        client = TestClient(server.app)
        client.get("/api/categories/all-nba/1")
        client.get("/api/categories/all-nba/1")
        client.get("/api/categories/all-nba/2")
        # tier 1 cached (1 call), tier 2 fresh (1 call) = 2 total
        assert mock_fetch.call_count == 2
