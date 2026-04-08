# Workflow: MVP Build

## Ziel
Ersten funktionierenden Prototyp bauen: User kann eine Top-5-Liste erstellen und als Bild exportieren.

## Schritte

1. **Spielerdatenbank aufbauen** → `tools/build_player_db.py`
   - Top 200 All-Time Spieler scrapen (basketball-reference-web-scraper)
   - Felder: Name, Position, Teams, Career PPG/RPG/APG, Ringe, MVPs, All-Stars
   - Output: `players.json` oder SQLite-Datenbank

2. **Bild-Generator bauen** → `tools/generate_card.py`
   - Input: Liste von 5 Spieler-IDs + Format-Typ
   - Output: 9:16 PNG (1080×1920)
   - Design: Teamfarben, Silhouette/Fallback, Name, Stats

3. **Einfaches Web-UI** (Next.js oder statisches HTML für den Start)
   - Spieler suchen / browsen
   - 5 Plätze befüllen
   - "Exportieren" → Bild generieren → Download

## Edge Cases
- Spieler ohne Silhouette → Jersey + Nummer als Fallback
- Fehlende Stats → "N/A" anzeigen, kein Crash

## Output
- `output/rushmore_TIMESTAMP.png`
