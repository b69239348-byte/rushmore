"""
Rushmore MVP — FastAPI Backend
Serves player data and generates card images.
"""
import json
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache player DB in memory
_player_db = None
_live_players = None
_jersey_by_id = None
_position_by_id = None


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


@app.get("/api/players")
def search_players(q: str = Query("", min_length=0), limit: int = 20):
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
SILHOUETTE_SIZE = 12430  # all placeholder silhouettes are exactly this size


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
def get_all_time(limit: int = 5, sort_by: str = "total_points"):
    """Top N players all-time."""
    return all_time(limit, sort_by)


@app.get("/api/categories/position/{position_code}")
def get_by_position(position_code: str, limit: int = 5, sort_by: str = "total_points"):
    """Top players by position (G, F, C)."""
    position_code = position_code.upper()
    if position_code not in ("G", "F", "C"):
        return {"error": "Position must be G, F, or C"}
    return by_position(position_code, limit, sort_by)


@app.get("/api/categories/team/{team_code}")
def get_by_team(team_code: str, limit: int = 5, sort_by: str = "total_points"):
    """Top players for a franchise."""
    team_code = team_code.upper()
    if team_code not in TEAM_NAMES:
        return {"error": f"Unknown team: {team_code}"}
    return by_team(team_code, limit, sort_by)


@app.get("/api/categories/era/{decade}")
def get_by_era(decade: int, limit: int = 5, sort_by: str = "ppg"):
    """Top players of a decade (e.g. 1990)."""
    if decade < 1950 or decade > 2020 or decade % 10 != 0:
        return {"error": "Decade must be 1950-2020 in steps of 10"}
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
def get_award(slug: str, limit: int = 10):
    """Players ranked by a specific award."""
    if slug not in AWARD_DEFS:
        return {"error": f"Unknown award: {slug}", "available": list(AWARD_DEFS.keys())}
    return by_award(slug, limit)


@app.get("/api/categories/current-season")
def get_current_season(limit: int = 30):
    """Current season leaders (live data, cached)."""
    return current_season(limit)


@app.get("/api/categories/active")
def get_active_players(limit: int = 10):
    try:
        return active_players(limit)
    except Exception:
        players = _fallback("active_players")[:limit]
        return {"title": f"TOP {limit} ACTIVE PLAYERS", "subtitle": "Current Season Best by PPG", "players": players}


# --- Current Season Award Races ---

@app.get("/api/categories/current-mvp")
def get_current_mvp(limit: int = 5):
    season = _detect_season()
    try:
        players = fetch_current_mvp_race(limit)
    except Exception:
        players = _fallback("mvp_race")[:limit]
    return {"title": "MVP RACE", "subtitle": f"{season} — Top Candidates by Efficiency", "players": _enrich_jersey(players)}


@app.get("/api/categories/current-dpoy")
def get_current_dpoy(limit: int = 5):
    season = _detect_season()
    try:
        players = fetch_current_dpoy_race(limit)
    except Exception:
        players = _fallback("dpoy_race")[:limit]
    return {"title": "DPOY RACE", "subtitle": f"{season} — Top Defensive Players", "players": _enrich_jersey(players)}


@app.get("/api/categories/current-roy")
def get_current_roy(limit: int = 5):
    season = _detect_season()
    try:
        players = fetch_current_roy_race(limit)
    except Exception:
        players = _fallback("roy_race")[:limit]
    return {"title": "ROOKIE OF THE YEAR", "subtitle": f"{season} — Top Rookies", "players": _enrich_jersey(players)}


@app.get("/api/categories/current-mip")
def get_current_mip(limit: int = 5):
    season = _detect_season()
    try:
        players = fetch_current_mip_race(limit)
    except Exception:
        players = _fallback("mip_race")[:limit]
    return {"title": "MOST IMPROVED", "subtitle": f"{season} — Biggest PPG Jump", "players": _enrich_jersey(players)}


@app.get("/api/categories/all-nba/{tier}")
def get_all_nba_tier(tier: int, limit: int = 5):
    if tier not in (1, 2, 3):
        return {"error": "Tier must be 1, 2, or 3"}
    season = _detect_season()
    ordinals = {1: "First", 2: "Second", 3: "Third"}
    try:
        players = fetch_all_nba_tier(tier, limit)
    except Exception:
        players = _fallback(f"all_nba_{tier}")[:limit]
    return {"title": f"ALL-NBA {ordinals[tier].upper()} TEAM", "subtitle": f"{season} — {ordinals[tier]} Team", "players": _enrich_jersey(players)}


class GenerateRequest(BaseModel):
    player_ids: List[int]
    title: str = "MY MT. RUSHMORE"
    subtitle: str = "ALL-TIME GREATEST"
    background: str = "night_court_outdoor"
    format: str = "story"


class GenerateTeamsRequest(BaseModel):
    team_codes: List[str]
    title: str = "MY TOP 5 TEAMS"
    tier_labels: List[str] = []


class GenerateBracketRequest(BaseModel):
    slots: List[Optional[str]]
    title: str = "MY PLAYOFF BRACKET"


@app.post("/api/generate-bracket")
def generate_bracket(req: GenerateBracketRequest):
    """Generate a playoff bracket card image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name
    generate_bracket_card(req.slots, title=req.title, output_path=output_path)
    return FileResponse(output_path, media_type="image/png", filename="rushmore-bracket.png")


@app.post("/api/generate-teams")
def generate_teams(req: GenerateTeamsRequest):
    """Generate a team ranking card and return it."""
    if not req.team_codes or len(req.team_codes) > 5:
        return {"error": "Provide 1-5 team codes"}

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
    return FileResponse(output_path, media_type="image/png", filename="rushmore-teams.png")


def _pick_background(subtitle: str, explicit: str) -> str:
    """Pick background based on theme if not explicitly set."""
    if explicit:
        return explicit
    s = subtitle.lower()
    if any(x in s for x in ["champion", "finals"]):
        return "trophy_celebration"
    if any(x in s for x in ["mvp", "dpoy", "roy", "mip", "all-nba", "award"]):
        return "trophy_spotlight"
    if any(x in s for x in ["season", "current", "active"]):
        return "indoor_arena"
    if any(x in s for x in ["freestyle", "custom", "own"]):
        return "rooftop_city"
    if any(x in s for x in ["all-time", "greatest", "goat", "legend"]):
        return "golden_arena"
    if any(x in s for x in ["team", "bracket", "tier"]):
        return "night_court_outdoor"
    return "night_court_outdoor"


@app.post("/api/generate")
def generate(req: GenerateRequest):
    """Generate a card image and return it."""
    if not req.player_ids or len(req.player_ids) > 5:
        return {"error": "Provide 1-5 player IDs"}

    queries = [str(pid) for pid in req.player_ids]
    background = _pick_background(req.subtitle, req.background)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    generate_card(queries, title=req.title, subtitle=req.subtitle, output_path=output_path, background=background, extra_players=get_live_players(), card_format=req.format)
    return FileResponse(output_path, media_type="image/png", filename="rushmore.png")


# --- Serve Frontend ---

frontend_dir = Path(__file__).parent.parent / "frontend"


@app.get("/")
def serve_index():
    index_path = frontend_dir / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


# Static files (CSS, JS)
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
