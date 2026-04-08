# Split-View Layout Design

**Date:** 2026-03-31
**Scope:** Legenden + Aktuell Seiten — neues Split-View Layout mit In-Page Kategorie-Wechsel und integriertem Card Builder

---

## Ziel

Nutzer sollen in einer einzigen View ihre Top-5-Karte zusammenstellen können: links durch Spieler scrollen, rechts sieht man die Karte entstehen. Kein Seitenwechsel, kein separater Builder-Flow.

---

## Routing & Sidebar

Die Sidebar wird von einem Baum auf 4 flache Einträge reduziert:

```
⛰ RUSHMORE
──────────
  Home
  Legenden      → /legenden
  Aktuell       → /aktuell
  Teams         → /categories/teams  (bleibt wie es ist)
```

Alle bestehenden `/categories/*` Routen bleiben erhalten aber sind nicht mehr direkt verlinkt.

---

## Neue Seiten

### `/legenden`

Kategorie-Pills (horizontal scrollbar):

| Pill | API-Pfad | Limit |
|---|---|---|
| All-Time | `all-time` | 5 |
| Guards | `position/G` | 5 |
| Forwards | `position/F` | 5 |
| Centers | `position/C` | 5 |
| MVP | `awards/mvp` | 5 |
| All-NBA | `awards/all-nba` | 5 |
| DPOY | `awards/dpoy` | 5 |
| ROY | `awards/roy` | 5 |
| Finals MVP | `awards/finals-mvp` | 5 |

Default: All-Time beim ersten Laden.

**Regel:** Legenden zeigt immer exakt 5 Spieler — der Nutzer ordnet diese in seine Reihenfolge.

### `/aktuell`

| Pill | API-Pfad | Limit |
|---|---|---|
| Diese Saison | `current-season` | 30 |
| Aktive Stars | `active` | 30 |

Default: Diese Saison beim ersten Laden.

**Regel:** Aktuell zeigt bis zu 30 Spieler — der Nutzer wählt seine Top 5 aus dem größeren Pool.

---

## Desktop Layout (md+)

```
┌──────────┬────────────────────────────┬──────────────────┐
│ Sidebar  │  Left Panel                │  Right Panel     │
│  56px    │  (flex-1, scrollable)      │  (w-80, sticky)  │
│          │                            │                  │
│  Home    │  [All-Time][Guards][...]   │  Dein Top 5      │
│  Legenden│  ──────────────────────    │  ─────────────── │
│  Aktuell │  1. LeBron James      ✓   │  1 LeBron James  │
│  Teams   │  2. Kareem            →   │  2 ─────────     │
│          │  3. Jordan            →   │  3 ─────────     │
│          │  4. Kobe              →   │  4 ─────────     │
│          │  5. Malone            →   │  5 ─────────     │
│          │  ...                      │                  │
│          │                            │  [Karte erstellen]│
└──────────┴────────────────────────────┴──────────────────┘
```

**Rechtes Panel — 3 Zustände:**

1. **Leer / Teilweise gefüllt:** Slots sichtbar (gefüllte gold, leere gestrichelt). Live-Vorschau des Karten-Layouts mit Platzhaltern für fehlende Spieler. Counter "Noch X Spieler auswählen".

2. **Alle 5 gefüllt:** "Karte erstellen" Button erscheint (gold). Slots bleiben sichtbar mit Hoch/Runter-Pfeilen zum Umsortieren und X zum Entfernen.

3. **Nach Generierung:** PNG erscheint inline im rechten Panel (9:16 Ratio). Darunter: "Download PNG" (gold) + "In Zwischenablage kopieren" (sekundär). Kleiner "Neu starten" Link setzt Slots zurück.

---

## Mobile Layout

Kein Split-View. Seite scrollt normal:
- Pills oben (horizontal scrollbar)
- Spielerliste darunter
- Bestehende Sticky Bottom Bar bleibt unverändert (SelectionBar Komponente)

---

## Komponenten

### Neu zu erstellen

**`SplitCategoryPage.tsx`** — Shared Component für Legenden + Aktuell
Props: `title`, `categories` (pills config Array)
State: aktive Kategorie, Spielerdaten, Slots (5x Player|null)
Desktop: zweispaltig. Mobile: einspaltig + SelectionBar.

**`CardBuilderPanel.tsx`** — Rechtes Panel (nur Desktop)
Props: `slots`, `onRemove`, `onReorder`, `categorySubtitle`
State: `generating`, `cardUrl`
Zeigt: Live-Slot-Übersicht → Generate Button → PNG inline + Actions

**`/legenden/page.tsx`** — Rendert `<SplitCategoryPage>` mit Legenden-Pills
**`/aktuell/page.tsx`** — Rendert `<SplitCategoryPage>` mit Aktuell-Pills

### Zu aktualisieren

**`Sidebar.tsx`** — Baum entfernen, 4 flache Links: Home / Legenden / Aktuell / Teams

### Unverändert

`PlayerList.tsx`, `SelectionBar.tsx`, `CategoryPage.tsx` (alte Routen), `api.ts`

---

## Datenfluss

```
Pill-Klick
  → fetchCategory(path, params)
  → PlayerList aktualisiert
  → Slots werden zurückgesetzt

Spieler-Klick (PlayerList)
  → Slot füllen (nächster freier)
  → CardBuilderPanel aktualisiert live

"Karte erstellen"
  → generateCard(playerIds, "MY MT. RUSHMORE", categorySubtitle)
  → cardUrl → img src im Panel

"Download"
  → <a download> click

"In Zwischenablage kopieren"
  → fetch(cardUrl) → blob → ClipboardItem → navigator.clipboard.write()

"Neu starten"
  → cardUrl = null, slots = [null×5]
```

---

## Out of Scope

- Share-to-Socials Buttons (Twitter/X deeplinks) — Post-Launch
- Drag & Drop Umsortierung (Pfeile reichen für jetzt)
- `/categories/teams/[code]` Route entfernen — separater Cleanup
- `/build` Seite entfernen — separater Cleanup
