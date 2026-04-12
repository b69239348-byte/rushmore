"""Caption template system for Rushmore social media posts.

Brand voice: Stats-first, opinion-second, English, confident tone. Never generic fluff.

Platform formats:
  TikTok:    Hook + stat/context + audience question + 4-5 hashtags
  Instagram: Slightly longer + context + CTA rushmore.cards + 6-8 hashtags
  X:         Stat-first, punchy, max 2 hashtags, MUST be under 280 chars
"""

from __future__ import annotations

__all__ = ["get_captions"]

# ---------------------------------------------------------------------------
# Award label lookup
# ---------------------------------------------------------------------------

_AWARD_META: dict[str, tuple[str, str]] = {
    "mvp":        ("MVP", "👑"),
    "roty":       ("ROTY", "🌟"),
    "mip":        ("MIP", "📈"),
    "dpoy":       ("DPOY", "🛡️"),
    "all_nba":    ("All-NBA", "🏆"),
    "all_rookie": ("All-Rookie", "🌟"),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_captions(
    card_type: str,
    *,
    players: list[dict] | None = None,
    date: str = "",
    title: str = "",
    award_type: str = "",
    matchup: dict | None = None,
) -> dict[str, str]:
    """Return {'tiktok': str, 'instagram': str, 'x': str}."""
    dispatch = {
        "top5":            _top5,
        "mvp_race":        _mvp_race,
        "scoring_title":   _scoring_title,
        "roty":            _roty,
        "debate":          _debate,
        "award":           _award,
        "playoff_matchup": _playoff_matchup,
        "playoff_bracket": _playoff_bracket,
        "all_nba":         _all_nba,
        "all_rookie":      _all_rookie,
    }
    fn = dispatch.get(card_type, _generic)
    return fn(
        players=players or [],
        date=date,
        title=title,
        award_type=award_type,
        matchup=matchup or {},
    )


# ---------------------------------------------------------------------------
# Card-type handlers
# ---------------------------------------------------------------------------

def _top5(*, players, date, title, award_type, matchup) -> dict[str, str]:
    p = players[0] if players else {}
    name = p.get("name", "the top scorer")
    ppg = p.get("ppg", 0)

    date_str = f" ({date})" if date else ""

    tiktok = (
        f"{name} leads last night's Top 5 — averaging {ppg} PPG this season 📊{date_str}\n"
        f"Here's your NBA Top 5 breakdown — who's running the league right now?\n"
        f"Do you agree with the ranking?\n"
        f"#NBA #Basketball #Top5 #NBAHighlights #rushmore"
    )

    instagram = (
        f"{name} is putting up {ppg} PPG and the rest of the Top 5 aren't far behind.{date_str}\n\n"
        f"Who's really the best player in the league right now? The numbers don't lie — "
        f"but stats only tell half the story.\n\n"
        f"Build your own Top 5 at rushmore.cards 👇\n\n"
        f"#NBA #Basketball #Top5 #NBAStats #HoopsTalk #BestInTheLeague #NBAHighlights #rushmore"
    )

    x = (
        f"{name} {ppg} PPG — your NBA Top 5{date_str}. "
        f"Agree with the rankings? #NBA #Top5"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": _trim_x(x)}


def _mvp_race(*, players, date, title, award_type, matchup) -> dict[str, str]:
    p = players[0] if players else {}
    name = p.get("name", "the frontrunner")
    eff = p.get("eff", "")
    eff_str = f" | {eff} EFF" if eff else ""

    tiktok = (
        f"👑 mvp race update — {name} is pulling away{eff_str}\n"
        f"Is the trophy already decided or is this still a real race?\n"
        f"Comment your MVP pick 👇\n"
        f"#NBA #MVP #NBAMvp #Basketball #rushmore"
    )

    instagram = (
        f"👑 The MVP race is heating up and {name} is setting the pace{eff_str}.\n\n"
        f"The efficiency numbers are hard to argue with — but does the regular season "
        f"narrative actually matter?\n\n"
        f"See the full race at rushmore.cards\n\n"
        f"#NBA #MVPRace #NBAMvp #Basketball #NBAStats #HoopsDebate #NBADebate #rushmore"
    )

    x = _trim_x(
        f"👑 MVP Race: {name}{eff_str}. Is it a lock? #NBA #MVPRace"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _scoring_title(*, players, date, title, award_type, matchup) -> dict[str, str]:
    p = players[0] if players else {}
    name = p.get("name", "the scoring leader")
    ppg = p.get("ppg", 0) or 0
    ppg_str = f" {ppg} PPG" if ppg else ""

    tiktok = (
        f"🎯 {name}{ppg_str} — the scoring title race is on\n"
        f"Who finishes #1 at the end of the season?\n"
        f"Drop your prediction 👇\n"
        f"#NBA #ScoringTitle #Basketball #NBAStats #rushmore"
    )

    instagram = (
        f"Scoring Title Race — final standings 🎯\n"
        f"{name} leads at {ppg:.1f} PPG. Full ranking on rushmore.cards\n"
        f"#NBA #ScoringTitle #NBAStats #Basketball #rushmore"
    )

    x = _trim_x(
        f"🎯 Scoring title race: {name}{ppg_str}. Who wins it? #NBA"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _roty(*, players, date, title, award_type, matchup) -> dict[str, str]:
    p = players[0] if players else {}
    name = p.get("name", "the top rookie")
    ppg = p.get("ppg", "")
    ppg_str = f" {ppg} PPG" if ppg else ""

    tiktok = (
        f"🌟 ROTY watch — {name}{ppg_str} is making a case\n"
        f"Is this the best rookie class in years?\n"
        f"Who gets your ROTY vote? 👇\n"
        f"#NBA #ROTY #NBADraft #Rookies #rushmore"
    )

    instagram = (
        f"🌟 {name}{ppg_str} — the ROTY race is wide open.\n\n"
        f"This rookie class has been electric. Who stands out to you?\n\n"
        f"Cast your vote at rushmore.cards\n\n"
        f"#NBA #ROTY #NBADraft #Rookies #NBAStats #Basketball #NBADebate #rushmore"
    )

    x = _trim_x(
        f"🌟 ROTY race: {name}{ppg_str}. Who gets your vote? #NBA #ROTY"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _debate(*, players, date, title, award_type, matchup) -> dict[str, str]:
    topic = title or "the biggest debate in basketball"

    tiktok = (
        f"{topic}\n"
        f"Agree or disagree? 👇\n"
        f"Drop your take in the comments — let's settle this\n"
        f"#NBA #HoopsDebate #Basketball #NBADebate #rushmore"
    )

    instagram = (
        f"{topic}\n\n"
        f"Some debates never get old — and this one is no different.\n"
        f"The comments section is always the best part.\n\n"
        f"Weigh in at rushmore.cards 👇\n\n"
        f"#NBA #HoopsDebate #Basketball #NBADebate #HotTake #NBATwitter #rushmore #HoopsTalk"
    )

    x = _trim_x(
        f"{topic} — agree or disagree? #NBA #HoopsDebate"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _award(*, players, date, title, award_type, matchup) -> dict[str, str]:
    label, emoji = _AWARD_META.get(award_type.lower(), ("Award", "🏆"))
    p = players[0] if players else {}
    name = p.get("name", "")
    name_str = f" — {name}" if name else ""

    tiktok = (
        f"{emoji} {label} race{name_str}\n"
        f"Is this the front-runner or is there still a real competition?\n"
        f"Who gets your {label} vote? 👇\n"
        f"#NBA #{label.replace('-', '').replace(' ', '')} #Basketball #NBADebate #rushmore"
    )

    instagram = (
        f"{emoji} The {label} race{name_str}.\n\n"
        f"These numbers make a strong case — but awards are never just about stats.\n\n"
        f"See the full breakdown at rushmore.cards\n\n"
        f"#NBA #{label.replace('-', '').replace(' ', '')} #NBAStats #Basketball #HoopsDebate #NBADebate #rushmore #HoopsTalk"
    )

    x = _trim_x(
        f"{emoji} {label}{name_str}. Who's your pick? #NBA"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _playoff_matchup(*, players, date, title, award_type, matchup) -> dict[str, str]:
    home = matchup.get("home_team", "Home Team")
    away = matchup.get("away_team", "Away Team")
    home_w = matchup.get("home_wins", 0)
    away_w = matchup.get("away_wins", 0)
    series = f"{away} {away_w}–{home_w} {home}"

    # Short team names for X
    home_short = home.split()[-1]
    away_short = away.split()[-1]

    tiktok = (
        f"🏆 Playoffs: {series}\n"
        f"Who closes this series out — and how many games?\n"
        f"Drop your prediction 👇\n"
        f"#NBA #NBAPlayoffs #Basketball #Playoffs #rushmore"
    )

    instagram = (
        f"🏆 {series}\n\n"
        f"Every game matters now. Who do you have advancing?\n\n"
        f"Track the bracket at rushmore.cards\n\n"
        f"#NBA #NBAPlayoffs #Playoffs #Basketball #NBABracket #HoopsTalk #NBADebate #rushmore"
    )

    x = _trim_x(
        f"🏆 {away_short} {away_w}–{home_w} {home_short}. Who advances? #NBA #NBAPlayoffs"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _playoff_bracket(*, players, date, title, award_type, matchup) -> dict[str, str]:
    tiktok = (
        f"🏆 NBA Playoff bracket update — who's left standing?\n"
        f"Drop your Final Four picks 👇\n"
        f"#NBA #NBAPlayoffs #Bracket #Basketball #rushmore"
    )

    instagram = (
        f"🏆 The NBA Playoff bracket is taking shape.\n\n"
        f"Every series tells a story — who do you have making a deep run?\n\n"
        f"Build your bracket at rushmore.cards\n\n"
        f"#NBA #NBAPlayoffs #Bracket #Basketball #NBABracket #HoopsTalk #Playoffs #rushmore"
    )

    x = _trim_x(
        f"🏆 NBA Playoff bracket update. Who's going all the way? #NBA #NBAPlayoffs"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _all_nba(*, players, date, title, award_type, matchup) -> dict[str, str]:
    tiktok = (
        f"🏆 All-NBA team reveal — did your guy make it?\n"
        f"Who got snubbed this year?\n"
        f"Comment your All-NBA picks 👇\n"
        f"#NBA #AllNBA #Basketball #NBADebate #rushmore"
    )

    instagram = (
        f"🏆 All-NBA teams are in.\n\n"
        f"Every year there's a snub. Every year the internet goes to war.\n"
        f"Who's missing from this list?\n\n"
        f"See the full team at rushmore.cards\n\n"
        f"#NBA #AllNBA #NBAStats #Basketball #HoopsDebate #NBADebate #Snubs #rushmore"
    )

    x = _trim_x(
        f"🏆 All-NBA teams revealed. Who got snubbed? #NBA #AllNBA"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _all_rookie(*, players, date, title, award_type, matchup) -> dict[str, str]:
    tiktok = (
        f"🌟 All-Rookie team — the next wave is here\n"
        f"Who's going to be a star in 3 years?\n"
        f"Drop your prediction 👇\n"
        f"#NBA #AllRookie #Rookies #NBADraft #rushmore"
    )

    instagram = (
        f"🌟 All-Rookie team is set.\n\n"
        f"The future of the NBA is on this list — who stands out to you?\n\n"
        f"See the full class at rushmore.cards\n\n"
        f"#NBA #AllRookie #Rookies #NBADraft #NBAStats #Basketball #NextUp #rushmore"
    )

    x = _trim_x(
        f"🌟 All-Rookie team revealed. Who's your future star? #NBA #AllRookie"
    )

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


def _generic(*, players, date, title, award_type, matchup) -> dict[str, str]:
    topic = title or "NBA update"

    tiktok = (
        f"{topic}\n"
        f"What's your take on this?\n"
        f"Drop your opinion below 👇\n"
        f"#NBA #Basketball #HoopsTalk #NBADebate #rushmore"
    )

    instagram = (
        f"{topic}\n\n"
        f"The league never slows down.\n\n"
        f"Explore more at rushmore.cards\n\n"
        f"#NBA #Basketball #HoopsTalk #NBADebate #NBAStats #Hoops #NBATwitter #rushmore"
    )

    x = _trim_x(f"{topic}. Thoughts? #NBA")

    return {"tiktok": tiktok, "instagram": instagram, "x": x}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trim_x(text: str) -> str:
    """Ensure X caption is within 280 characters, trimming if needed."""
    if len(text) <= 280:
        return text
    # Trim to 277 and add ellipsis
    return text[:277] + "..."
