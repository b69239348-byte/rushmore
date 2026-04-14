# Share Modal Redesign + Format Toggle

**Date:** 2026-04-10  
**Status:** Approved

---

## Problem

1. **X share (Desktop):** Opens Twitter intent with text only — image not attached. Twitter web intent doesn't support file attachments via URL.
2. **Instagram ratio (Mobile):** Card is 1080×1920 (9:16 Story format). Instagram Feed posts require 4:5 max (1080×1350) — rejected as too large.
3. **Polish:** 4 buttons in 2 rows, no clear hierarchy, no guidance for the user.

---

## Design

### Format Toggle (before/after card generation)

A small two-option toggle shown in the share modal (or builder panel):

- **Story** (default) — 1080×1920, 9:16 — current format
- **Feed Post** — 1080×1350, 4:5 — backend crops vertically from top

Implementation: pass a `format` query param (`story` | `feed`) to the `/generate-card` API endpoint. Backend crops the canvas to 1350px height before returning.

### Share Modal — Mobile (native share available)

Single primary button: **"Share"** — triggers `navigator.share({ files: [file] })`.  
This passes the image correctly to X, Instagram, WhatsApp, etc. via the system sheet.

Secondary, smaller: **"Save"** (download).

No X button, no Instagram button, no Copy button — native share covers everything better.

### Share Modal — Desktop (no native share)

Two buttons only:

- **"Download"** (primary) — saves the PNG
- **"Post on X"** (secondary) — auto-downloads + opens Twitter intent. Helper text below: *"Image auto-saves — attach it in X"*

No Instagram button (no desktop web API exists).  
Copy to clipboard available as tertiary link if clipboard API is available.

### Button Layout

```
Mobile:
┌─────────────────────────┐
│  [ Share ← primary    ] │
│  [ Save  ← secondary  ] │
└─────────────────────────┘

Desktop:
┌─────────────────────────┐
│  [ Download ← primary ] │
│  [ Post on X          ] │
│  "Image auto-saves →    │
│   attach it in X"       │
│  Copy image (tertiary)  │
└─────────────────────────┘
```

Format toggle sits above the buttons, always visible:

```
[ Story · Feed Post ]
```

---

## Scope

**Frontend (`CardPreview.tsx`):**
- Detect `canNativeShare` and render mobile vs desktop layout
- Add format state (`story` | `feed`), pass to `generateCard()` call
- Redesign button layout per spec above
- Add helper text for X on desktop

**Frontend (`ExportButton.tsx` / `CardBuilderPanel.tsx`):**
- Pass `format` param through to the API call
- Re-generate card when format toggle changes (or show toggle in modal, regenerate on switch)

**Backend (`server.py` + `generate_card.py`):**
- Accept optional `format` param (`story` | `feed`) in `/generate-card` endpoint
- In `generate_card.py`: after canvas is composed at 1080×1920, if `format=feed`, crop to 1080×1350

---

## Out of Scope

- TikTok / Instagram direct API integration (planned for later native app)
- Multiple card sizes beyond Story + Feed
- Server-side image hosting for X card previews
