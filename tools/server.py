"""
Rushmore MVP — FastAPI Backend
Serves player data and generates card images.
"""
import hmac
import json
import os
import time
import tempfile
from pathlib import Path
from typing import List, Literal, Optional

import re

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator

from generate_card import generate_card, load_players
from generate_team_card import generate_team_card
from generate_bracket_card import generate_bracket_card
from categories import (
    list_categories, all_time, by_position, by_team, by_era,
    champions, mvp_race, current_season, active_players, team_ranking, TEAM_NAMES,
    by_award, list_awards, AWARD_DEFS,
)
from live_data import (
    fetch_current_mvp_race, fetch_current_dpoy_race,
    fetch_current_roy_race, fetch_current_mip_race, fetch_all_nba_tier, fetch_team_stats,
    _detect_season,
)

app = FastAPI(title="Rushmore API")

_INTERNAL_KEY_HEADER = APIKeyHeader(name="X-Internal-Key", auto_error=False)
_INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")


def _require_internal_key(key: Optional[str] = Security(_INTERNAL_KEY_HEADER)):
    if not _INTERNAL_API_KEY or not hmac.compare_digest(key or "", _INTERNAL_API_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")


_ALLOWED_ORIGINS = [
    "https://rushmore.cards",
    "https://www.rushmore.cards",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Internal-Key"],
)

# Cache player DB in memory
_player_db = None
_live_players = None
_jersey_by_id = None
_position_by_id = None

# In-memory TTL cache for live NBA API responses
_api_cache: dict = {}
_API_CACHE_TTL = 6 * 3600  # 6 hours


def _get_cached(key: str):
    if key in _api_cache:
        data, ts = _api_cache[key]
        if time.time() - ts < _API_CACHE_TTL:
            return data
    return None


def _set_cached(key: str, data):
    _api_cache[key] = (data, time.time())


def get_db():
    global _player_db
    if _player_db is None:
        _player_db = load_players()
    return _player_db


def _get_jersey_lookup() -> dict:
    global _jersey_by_id
    if _jersey_by_id is None:
        _jersey_by_id = {p["id"]: p.get("jersey") for p in get_db() if p.get("jersey")}
    return _jersey_by_id


def _get_position_lookup() -> dict:
    global _position_by_id
    if _position_by_id is None:
        path = DATA_DIR / "player_positions.json"
        if path.exists():
            raw = json.loads(path.read_text())
            # Keys are stored as strings in JSON
            _position_by_id = {int(k): v for k, v in raw.items()}
        else:
            _position_by_id = {p["id"]: p.get("position", "") for p in get_db()}
    return _position_by_id


def _enrich_jersey(players: list) -> list:
    """Add jersey number and position to live-fetched players that don't have them yet."""
    jersey_lookup = _get_jersey_lookup()
    pos_lookup = _get_position_lookup()
    for p in players:
        if not p.get("jersey"):
            jersey = jersey_lookup.get(p.get("id"))
            if jersey:
                p["jersey"] = jersey
        if not p.get("position"):
            pos = pos_lookup.get(p.get("id"), "")
            if pos:
                p["position"] = pos
    return players


DATA_DIR = Path(__file__).parent / "data"


def _fallback(key: str) -> list:
    """Load pre-fetched fallback JSON when NBA API is unavailable."""
    path = DATA_DIR / f"{key}_fallback.json"
    if path.exists():
        return json.loads(path.read_text())
    return []


def get_live_players():
    """Lazy-load current season leaders (top 200) for card generation."""
    global _live_players
    if _live_players is None:
        try:
            from live_data import fetch_season_leaders
            _live_players = fetch_season_leaders(limit=200)
        except Exception:
            print("[WARN] fetch_season_leaders failed, using fallback")
            _live_players = _fallback("season_leaders")
    return _live_players


# --- API Routes ---


_VALID_SORT = {"total_points", "ppg", "rpg", "apg", "spg", "bpg", "total_rebounds", "total_assists"}


@app.get("/api/players")
def search_players(q: str = Query("", min_length=0), limit: int = Query(20, ge=1, le=600)):
    """Search players by name. Empty query returns all legends + current season players."""
    db = get_db()
    live_players = get_live_players()
    live_by_id = {p["id"]: p for p in live_players}
    db_ids = {p["id"] for p in db}

    if not q.strip():
        # All legends + current season players not already in legends DB
        current_only = [p for p in live_players if p["id"] not in db_ids]
        results = db + current_only
    else:
        q_lower = q.lower()
        db_results = [p for p in db if q_lower in p["name"].lower()]
        live_results = [p for p in live_players if q_lower in p["name"].lower() and p["id"] not in db_ids]
        results = db_results + live_results

    results = results[:limit] if limit else results

    out = []
    for p in results:
        entry = {
            "id": p["id"],
            "name": p["name"],
            "position": p.get("position", ""),
            "teams": p.get("teams", [])[:3],
            "main_team": p.get("main_team"),
            "jersey": p.get("jersey", ""),
            "ppg": p.get("ppg"),
            "rpg": p.get("rpg"),
            "apg": p.get("apg"),
            "spg": p.get("spg"),
            "bpg": p.get("bpg"),
            "from_year": p.get("from_year"),
            "to_year": p.get("to_year"),
            "awards": p.get("awards", {}),
        }
        if p["id"] in live_by_id:
            live = live_by_id[p["id"]]
            entry["current_ppg"] = live.get("ppg")
            entry["current_rpg"] = live.get("rpg")
            entry["current_apg"] = live.get("apg")
            entry["current_spg"] = live.get("spg")
            entry["current_bpg"] = live.get("bpg")
            if live.get("team"):
                entry["team"] = live["team"]
        out.append(entry)
    return out


HEADSHOT_DIR = Path(__file__).parent.parent / "assets" / "headshots"
# NBA CDN serves this exact byte size for all silhouette placeholders (verified 2025-04).
# If this breaks: re-download a known placeholder and run: wc -c <file>
SILHOUETTE_SIZE = 12430


@app.get("/api/headshot/{player_id}")
def get_headshot(player_id: int):
    """Serve local headshot if it's a real photo. 404 for silhouettes."""
    for ext in ("jpg", "jpeg", "png"):
        path = HEADSHOT_DIR / f"{player_id}.{ext}"
        if path.exists():
            if path.stat().st_size == SILHOUETTE_SIZE:
                raise HTTPException(status_code=404, detail="No real headshot")
            return FileResponse(path, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Headshot not found")


# --- Category Routes ---


@app.get("/api/categories")
def get_categories():
    """List all available categories with metadata."""
    return list_categories()


@app.get("/api/categories/all-time")
def get_all_time(limit: int = Query(5, ge=1, le=300), sort_by: str = "total_points"):
    """Top N players all-time."""
    if sort_by not in _VALID_SORT:
        raise HTTPException(status_code=422, detail=f"Invalid sort_by. Valid: {sorted(_VALID_SORT)}")
    return all_time(limit, sort_by)


@app.get("/api/categories/position/{position_code}")
def get_by_position(position_code: str, limit: int = Query(5, ge=1, le=300), sort_by: str = "total_points"):
    """Top players by position (G, F, C)."""
    position_code = position_code.upper()
    if position_code not in ("G", "F", "C"):
        raise HTTPException(status_code=422, detail="Position must be G, F, or C")
    if sort_by not in _VALID_SORT:
        raise HTTPException(status_code=422, detail=f"Invalid sort_by. Valid: {sorted(_VALID_SORT)}")
    return by_position(position_code, limit, sort_by)


@app.get("/api/categories/team/{team_code}")
def get_by_team(team_code: str, limit: int = Query(5, ge=1, le=300), sort_by: str = "total_points"):
    """Top players for a franchise."""
    team_code = team_code.upper()
    if team_code not in TEAM_NAMES:
        raise HTTPException(status_code=404, detail=f"Unknown team: {team_code}")
    if sort_by not in _VALID_SORT:
        raise HTTPException(status_code=422, detail=f"Invalid sort_by. Valid: {sorted(_VALID_SORT)}")
    return by_team(team_code, limit, sort_by)


@app.get("/api/categories/era/{decade}")
def get_by_era(decade: int, limit: int = Query(5, ge=1, le=300), sort_by: str = "ppg"):
    """Top players of a decade (e.g. 1990)."""
    if decade < 1950 or decade > 2020 or decade % 10 != 0:
        raise HTTPException(status_code=422, detail="Decade must be 1950-2020 in steps of 10")
    if sort_by not in _VALID_SORT:
        raise HTTPException(status_code=422, detail=f"Invalid sort_by. Valid: {sorted(_VALID_SORT)}")
    return by_era(decade, limit, sort_by)


@app.get("/api/categories/champions")
def get_champions(limit: int = 5):
    """Players ranked by championship count."""
    return champions(limit)


@app.get("/api/categories/mvps")
def get_mvps(limit: int = 5):
    """Players ranked by MVP count."""
    return mvp_race(limit)


@app.get("/api/categories/awards")
def get_awards():
    """List available award categories."""
    return list_awards()


@app.get("/api/categories/awards/{slug}")
def get_award(slug: str, limit: int = Query(10, ge=1, le=50)):
    """Players ranked by a specific award."""
    if slug not in AWARD_DEFS:
        raise HTTPException(status_code=404, detail=f"Unknown award: {slug}", headers={"X-Available": ",".join(AWARD_DEFS.keys())})
    return by_award(slug, limit)


@app.get("/api/categories/current-season")
def get_current_season(limit: int = Query(200, ge=1, le=500)):
    """Current season leaders (live data, cached)."""
    return current_season(limit)


@app.get("/api/categories/active")
def get_active_players(limit: int = Query(200, ge=1, le=500)):
    try:
        return active_players(limit)
    except Exception:
        players = _fallback("active_players")[:limit]
        return {"title": f"TOP {limit} ACTIVE PLAYERS", "subtitle": "Current Season Best by PPG", "players": players}


# --- Current Season Award Races ---

@app.get("/api/categories/current-mvp")
def get_current_mvp(limit: int = 5):
    season = _detect_season()
    cached = _get_cached("current_mvp")
    if cached is not None:
        return cached
    try:
        players = fetch_current_mvp_race(limit)
    except Exception:
        players = _fallback("mvp_race")[:limit]
    result = {"title": "MVP RACE", "subtitle": f"{season} — Top Candidates by Efficiency", "players": _enrich_jersey(players)}
    _set_cached("current_mvp", result)
    return result


@app.get("/api/categories/current-dpoy")
def get_current_dpoy(limit: int = 5):
    season = _detect_season()
    cached = _get_cached("current_dpoy")
    if cached is not None:
        return cached
    try:
        players = fetch_current_dpoy_race(limit)
    except Exception:
        players = _fallback("dpoy_race")[:limit]
    result = {"title": "DPOY RACE", "subtitle": f"{season} — Top Defensive Players", "players": _enrich_jersey(players)}
    _set_cached("current_dpoy", result)
    return result


@app.get("/api/categories/current-roy")
def get_current_roy(limit: int = 5):
    season = _detect_season()
    cached = _get_cached("current_roy")
    if cached is not None:
        return cached
    try:
        players = fetch_current_roy_race(limit)
    except Exception:
        players = _fallback("roy_race")[:limit]
    result = {"title": "ROOKIE OF THE YEAR", "subtitle": f"{season} — Top Rookies", "players": _enrich_jersey(players)}
    _set_cached("current_roy", result)
    return result


@app.get("/api/categories/current-mip")
def get_current_mip(limit: int = 5):
    season = _detect_season()
    cached = _get_cached("current_mip")
    if cached is not None:
        return cached
    try:
        players = fetch_current_mip_race(limit)
    except Exception:
        players = _fallback("mip_race")[:limit]
    result = {"title": "MOST IMPROVED", "subtitle": f"{season} — Biggest PPG Jump", "players": _enrich_jersey(players)}
    _set_cached("current_mip", result)
    return result


@app.get("/api/categories/all-nba/{tier}")
def get_all_nba_tier(tier: int, limit: int = Query(5, ge=1, le=15)):
    if tier not in (1, 2, 3):
        raise HTTPException(status_code=422, detail="Tier must be 1, 2, or 3")
    season = _detect_season()
    ordinals = {1: "First", 2: "Second", 3: "Third"}
    cache_key = f"all_nba_{tier}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    try:
        players = fetch_all_nba_tier(tier, limit)
    except Exception:
        players = _fallback(f"all_nba_{tier}")[:limit]
    result = {"title": f"ALL-NBA {ordinals[tier].upper()} TEAM", "subtitle": f"{season} — {ordinals[tier]} Team", "players": _enrich_jersey(players)}
    _set_cached(cache_key, result)
    return result


class GenerateRequest(BaseModel):
    player_ids: List[int]
    title: str = Field("MY MT. RUSHMORE", max_length=120)
    subtitle: str = Field("ALL-TIME GREATEST", max_length=120)
    background: str = ""
    format: Literal["story", "feed"] = "story"

    @field_validator("background")
    @classmethod
    def validate_background(cls, v: str) -> str:
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            return ""
        return v


class GenerateTeamsRequest(BaseModel):
    team_codes: List[str]
    title: str = Field("MY TOP 5 TEAMS", max_length=120)
    tier_labels: List[str] = []


class GenerateBracketRequest(BaseModel):
    slots: List[Optional[str]]
    title: str = Field("MY PLAYOFF BRACKET", max_length=120)


@app.post("/api/generate-bracket")
def generate_bracket(req: GenerateBracketRequest, background_tasks: BackgroundTasks, _: None = Depends(_require_internal_key)):
    """Generate a playoff bracket card image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name
    generate_bracket_card(req.slots, title=req.title, output_path=output_path)
    background_tasks.add_task(os.unlink, output_path)
    return FileResponse(output_path, media_type="image/png", filename="rushmore-bracket.png", background=background_tasks)


@app.post("/api/generate-teams")
def generate_teams(req: GenerateTeamsRequest, background_tasks: BackgroundTasks, _: None = Depends(_require_internal_key)):
    """Generate a team ranking card and return it."""
    if not req.team_codes or len(req.team_codes) > 5:
        raise HTTPException(status_code=422, detail="Provide 1-5 team codes")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    try:
        stats = fetch_team_stats()
    except Exception as e:
        print(f"[WARN] fetch_team_stats failed: {e}, using fallback")
        fallback = Path(__file__).parent / "data" / "team_stats_fallback.json"
        stats = json.loads(fallback.read_text()) if fallback.exists() else {}
    generate_team_card(
        req.team_codes,
        title=req.title,
        output_path=output_path,
        team_stats=stats,
        tier_labels=req.tier_labels,
    )
    background_tasks.add_task(os.unlink, output_path)
    return FileResponse(output_path, media_type="image/png", filename="rushmore-teams.png", background=background_tasks)


_ILLUSTRATED_POOL = [
    "illustrated_court_teal",
    "illustrated_court_orange",
    "illustrated_dunk_purple",
    "illustrated_dunk_sunburst",
    "illustrated_shooter_green",
    "illustrated_pass_gradient",
]

_GENERAL_POOL = _ILLUSTRATED_POOL + [
    "night_court_outdoor",
    "indoor_arena",
    "rooftop_city",
]


def _pick_background(subtitle: str, explicit: str) -> str:
    """Pick background based on theme if not explicitly set."""
    import random
    if explicit:
        return explicit
    s = subtitle.lower()
    if any(x in s for x in ["champion", "finals"]):
        return random.choice(["trophy_celebration", "illustrated_dunk_sunburst"])
    if any(x in s for x in ["mvp", "dpoy", "roy", "mip", "all-nba", "award"]):
        return random.choice(["trophy_spotlight", "illustrated_dunk_purple", "illustrated_dunk_sunburst"])
    if any(x in s for x in ["season", "current", "active"]):
        return random.choice(["indoor_arena", "illustrated_court_teal", "illustrated_court_orange"])
    if any(x in s for x in ["freestyle", "custom", "own"]):
        return random.choice(["rooftop_city", "illustrated_pass_gradient", "illustrated_shooter_green"])
    if any(x in s for x in ["all-time", "greatest", "goat", "legend"]):
        return random.choice(["golden_arena", "illustrated_dunk_purple", "illustrated_court_teal"])
    if any(x in s for x in ["team", "bracket", "tier"]):
        return random.choice(["night_court_outdoor", "illustrated_court_orange", "illustrated_pass_gradient"])
    return random.choice(_GENERAL_POOL)


@app.post("/api/generate")
def generate(req: GenerateRequest, background_tasks: BackgroundTasks, _: None = Depends(_require_internal_key)):
    """Generate a card image and return it."""
    if not req.player_ids or len(req.player_ids) > 5:
        raise HTTPException(status_code=422, detail="Provide 1-5 player IDs")

    queries = [str(pid) for pid in req.player_ids]
    bg = _pick_background(req.subtitle, req.background)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    generate_card(queries, title=req.title, subtitle=req.subtitle, output_path=output_path, background=bg, extra_players=get_live_players(), card_format=req.format, db=get_db())
    background_tasks.add_task(os.unlink, output_path)
    return FileResponse(output_path, media_type="image/png", filename="rushmore.png", background=background_tasks)


# --- Serve Frontend ---

frontend_dir = Path(__file__).parent.parent / "frontend"


@app.get("/")
def serve_index():
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not built")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


# Static files (CSS, JS)
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
