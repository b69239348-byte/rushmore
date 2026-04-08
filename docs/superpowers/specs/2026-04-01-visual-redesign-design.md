# Visual Redesign — Design Spec
**Date:** 2026-04-01

## Overview

Full visual redesign of the Rushmore NBA app. Three areas: color system, generated card image, frontend components + UX flow.

---

## 1. Color System

Replace the current gold accent (`#c9a84c`) with basketball orange throughout the app.

| Token | Old | New |
|---|---|---|
| `--color-gold` | `#c9a84c` | `#E8540A` |
| `--color-gold-dim` | `#a08838` | `#b8420a` |
| `--color-gold-bright` | `#dfc06a` | `#ff6b30` |

**Scope:** `web/src/app/globals.css` only. All components inherit via `text-gold`, `bg-gold`, `border-gold` Tailwind classes — no per-component changes needed for the color swap.

Typography adjustments (sizes, weights, letter-spacing) are deferred — they don't affect architecture and can be tuned once the structure is in place.

---

## 2. Generated Card (Python/PIL)

`tools/generate_card.py` is rewritten from scratch. The current implementation is not structured for the new layout.

### Layout (1080×1920px, 9:16)

```
┌──────────────────────────┐
│                          │
│    MY TOP 5         [top]│
│    subtitle (category)   │
│                          │
│ ┌────────────────────┐   │
│ │ 01  [photo]  NAME  │ ← row 1 (highlighted, orange border-left)
│ │          #15       │
│ │  27.9 · 12.9 · 10.8│
│ └────────────────────┘   │
│ ┌────────────────────┐   │
│ │ 02  [photo]  NAME  │ ← rows 2–5 (same structure, dimmer orange)
│ │  ...               │
│ └────────────────────┘   │
│   ...                    │
│                          │
│         RUSHMORE.APP [footer]
└──────────────────────────┘
```

### Per-row elements
- **Rank:** `01`–`05`, monospace, bold, orange (`#E8540A`) for rank 1, dimmer for 2–5
- **Photo:** circular crop from `assets/headshots/{player_id}.jpg`. Fallback: orange circle with player initials
- **Name:** uppercase, white, bold
- **Jersey number:** `#15` in orange, same line as name
- **Stats:** `27.9 · 12.9 · 10.8` (PPG · RPG · APG), small, gray

### Title / Subtitle
- **Title:** user-defined, default `MY TOP 5`
- **Subtitle:** comes from category — e.g. `ALL-TIME GREATS`, `MVP RACE`, `FIRST TEAM ALL-NBA`
- Both in English. No German strings anywhere in the card.

### API compatibility
The `POST /api/generate` endpoint signature is unchanged — same request body (`player_ids`, `title`, `subtitle`), same PNG response. Only the visual output changes.

### Background
- Dark gradient (`#0a0a12` → `#080810`)
- Decorative elements (court lines, ball silhouettes, glow) deferred to a later polish sprint

### Fallback (no headshot)
- Orange filled circle with player initials (max 2 chars), white text

---

## 3. Frontend Components

### 3a. Color update (automatic)
All components already use `text-gold` / `bg-gold` / `border-gold` Tailwind classes. The color token change in globals.css propagates everywhere without per-file edits.

### 3b. PlayerList
- Rank badge color: `bg-gold` → stays, inherits orange automatically
- No structural changes needed

### 3c. CardModal (new component)
**File:** `web/src/components/builder/CardModal.tsx`

- Triggered by `Build Your Card` button (in both CardBuilderPanel and SelectionBar)
- Full-screen overlay with dark backdrop
- Center: card preview image (9:16 aspect ratio, max ~360px wide)
- Buttons below preview: `Save` (download PNG), `Copy` (clipboard), `×` close
- Loading state: spinner while card is generating (`Cooking…`)
- Error state: retry button

### 3d. CardBuilderPanel (updated)
- Remove embedded card preview (`cardUrl` state and image rendering)
- Keep: slot list, reorder, remove buttons
- Change: `Karte erstellen` button → `Build Your Card`, opens CardModal
- Button active as soon as ≥ 1 slot filled (not just when all 5 filled)

### 3e. SelectionBar (mobile, updated)
- Add `Build Your Card` button, visible as soon as ≥ 1 slot filled
- Button opens CardModal
- All German strings → English basketball slang (see below)

### 3f. UI Text — English Basketball Slang

| German | English |
|---|---|
| Karte erstellen | Build Your Card |
| Wird erstellt… | Cooking… |
| Noch 3 Spieler auswählen | 3 spots left |
| Dein Top 5 | Your Starting 5 |
| Spieler auswählen | Add a baller |
| Neu starten | Reset |
| Download | Save |
| Kopieren | Copy |
| Fehler beim Erstellen | Failed to generate — try again |

**Scope:** `CardBuilderPanel.tsx`, `SelectionBar.tsx`, any other component with hardcoded German strings.

---

## 4. Out of Scope (deferred)

- Background graphics on the card (court lines, ball silhouettes, glow effects)
- Typography tuning (font sizes, weights, letter-spacing)
- Homepage hero / stats bar changes
- Any new categories or data sources
