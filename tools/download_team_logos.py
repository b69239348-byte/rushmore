"""Download NBA team logo PNGs from ESPN CDN for local use in generate_card.py."""

import time
import urllib.request
from pathlib import Path

LOGO_DIR = Path(__file__).parent.parent / "assets" / "team_logos"

# NBA abbreviation → ESPN abbreviation (mostly lowercase, some exceptions)
ESPN_ABBRS = {
    "ATL": "atl", "BOS": "bos", "BKN": "bkn",
    "CHA": "cha", "CHI": "chi", "CLE": "cle",
    "DAL": "dal", "DEN": "den", "DET": "det",
    "GSW": "gs",  "HOU": "hou", "IND": "ind",
    "LAC": "lac", "LAL": "lal", "MEM": "mem",
    "MIA": "mia", "MIL": "mil", "MIN": "min",
    "NOP": "no",  "NYK": "ny",  "OKC": "okc",
    "ORL": "orl", "PHI": "phi", "PHX": "phx",
    "POR": "por", "SAC": "sac", "SAS": "sa",
    "TOR": "tor", "UTA": "utah","WAS": "wsh",
}


def download_logos():
    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    ok, skipped, failed = 0, 0, []
    for nba_abbr, espn_abbr in ESPN_ABBRS.items():
        path = LOGO_DIR / f"{nba_abbr}.png"
        if path.exists():
            print(f"  {nba_abbr}: skip (exists)")
            skipped += 1
            continue
        url = f"https://a.espncdn.com/i/teamlogos/nba/500/{espn_abbr}.png"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                path.write_bytes(resp.read())
            print(f"  {nba_abbr}: ok")
            ok += 1
            time.sleep(0.2)
        except Exception as e:
            print(f"  {nba_abbr}: FAILED — {e}")
            failed.append(nba_abbr)
    print(f"\nFertig: {ok} geladen, {skipped} übersprungen, {len(failed)} fehlgeschlagen")
    if failed:
        print(f"Fehlgeschlagen: {failed}")


if __name__ == "__main__":
    print(f"Lade 30 Team-Logos nach {LOGO_DIR}\n")
    download_logos()
