# Share Modal Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix X share (desktop), Instagram ratio (mobile), and redesign the share modal for a clean device-aware UX.

**Architecture:** Add a `card_format` param (`story` | `feed`) through the full stack (backend → API → frontend). Redesign `CardPreview` to show a mobile-first native share flow and a desktop download+X flow, with a Story/Feed toggle that re-generates the card.

**Tech Stack:** Python/Pillow (backend), FastAPI (server), TypeScript/React/Tailwind (frontend)

---

## File Map

| File | Change |
|------|--------|
| `tools/generate_card.py` | Add `card_format` param; parameterize canvas height + row height |
| `tools/server.py` | Add `format` field to `GenerateRequest`; pass to `generate_card()` |
| `web/src/lib/api.ts` | Add `format` param to `generateCard()` |
| `web/src/components/builder/CardPreview.tsx` | Full redesign: device-aware layout, format toggle, re-generation |
| `web/src/app/freestyle/page.tsx` | Pass `regenerate` prop to `CardPreview` |
| `web/src/components/categories/SplitCategoryPage.tsx` | Pass `regenerate` prop to `CardPreview` |
| `web/src/app/build/page.tsx` | Pass `regenerate` prop to `CardPreview` |

---

## Task 1: Backend — Parameterize card height in `generate_card.py`

**Files:**
- Modify: `tools/generate_card.py`

- [ ] **Step 1: Update `_load_background` to accept an optional height**

In `tools/generate_card.py`, find the `_load_background` function (around line 107). Change its signature and replace all internal uses of `HEIGHT` with the `height` parameter:

```python
def _load_background(background: str, height: int = HEIGHT) -> Image.Image:
    ...
    # Inside the function, replace every occurrence of HEIGHT with height:
    # e.g.:
    #   new_h = height
    #   new_h = int(WIDTH / img_ratio)  (this line is fine, no HEIGHT)
    #   return img.crop((left, top, left + WIDTH, top + height))
    #   fallback = Image.new("RGB", (WIDTH, height), (8, 12, 24))
    #   for y in range(height):
    #       t = y / height
    #       draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    #   return fallback
```

Read the full `_load_background` function body first, then make these replacements. The function currently uses `HEIGHT` in: the size of the fallback image, the loop range, the `t = y / HEIGHT` normalizer, and the final crop.

- [ ] **Step 2: Add `card_format` param and local dimension vars to `generate_card()`**

In the `generate_card()` function signature (line 225), add `card_format: str = "story"` as the last param:

```python
def generate_card(
    queries,
    title="MY TOP 5",
    subtitle="ALL-TIME GREATS",
    output_path="card.png",
    background="night_court_outdoor",
    extra_players=None,
    game_stats=None,
    card_format: str = "story",
):
```

Then, immediately after the docstring/first line of the function body, add:

```python
    canvas_h = 1350 if card_format == "feed" else HEIGHT
    _row_area = canvas_h - TITLE_H - FOOTER_H
    _row_h = _row_area // ROW_COUNT
    _photo_size = int(_row_h * 0.70)
```

- [ ] **Step 3: Replace HEIGHT/ROW_H usages inside `generate_card()`**

Find and replace the following in the function body (do NOT change module-level constants):

| Find | Replace with |
|------|-------------|
| `_load_background(background)` | `_load_background(background, height=canvas_h)` |
| `canvas.alpha_composite(bot_grad, (0, HEIGHT - 160))` | `canvas.alpha_composite(bot_grad, (0, canvas_h - 160))` |
| `PHOTO_SIZE = int(ROW_H * 0.70)` | `PHOTO_SIZE = _photo_size` |
| `row_y  = TITLE_H + i * ROW_H + ROW_GAP // 2` | `row_y  = TITLE_H + i * _row_h + ROW_GAP // 2` |
| `row_h  = ROW_H - ROW_GAP` | `row_h  = _row_h - ROW_GAP` |
| `iy = HEIGHT - FOOTER_H + (FOOTER_H - icon_h) // 2` | `iy = canvas_h - FOOTER_H + (FOOTER_H - icon_h) // 2` |

- [ ] **Step 4: Smoke-test the feed format locally**

```bash
cd tools
python generate_card.py feed
```

Then open the output file and verify it's 1080×1350 with all 5 players visible. (The `__main__` block at the bottom of generate_card.py already runs a test generation — temporarily add `card_format="feed"` to it for this check, then revert.)

- [ ] **Step 5: Add a regression test**

In `tests/test_daily_top5.py`, add:

```python
def test_generate_card_feed_format_produces_correct_dimensions():
    """generate_card() with card_format='feed' must produce 1080x1350 PNG."""
    import tempfile
    from pathlib import Path
    from PIL import Image
    from generate_card import generate_card

    players = ["LeBron James", "Michael Jordan", "Kobe Bryant", "Magic Johnson", "Larry Bird"]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name

    generate_card(players, card_format="feed", output_path=out)
    img = Image.open(out)
    assert img.size == (1080, 1350), f"Expected (1080, 1350), got {img.size}"
    Path(out).unlink()
```

Run it:
```bash
cd tools
python -m pytest ../tests/test_daily_top5.py::test_generate_card_feed_format_produces_correct_dimensions -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/generate_card.py tests/test_daily_top5.py
git commit -m "feat: add card_format param to generate_card (story/feed)"
```

---

## Task 2: Backend — Expose `format` in the API endpoint

**Files:**
- Modify: `tools/server.py`

- [ ] **Step 1: Add `format` field to `GenerateRequest`**

Find `class GenerateRequest(BaseModel):` (around line 320) and add the field:

```python
class GenerateRequest(BaseModel):
    player_ids: List[int]
    title: str = "MY MT. RUSHMORE"
    subtitle: str = "ALL-TIME GREATEST"
    background: str = "night_court_outdoor"
    format: str = "story"
```

- [ ] **Step 2: Pass `format` to `generate_card()` in the `/api/generate` endpoint**

Find the `generate()` function (around line 392). Update the `generate_card()` call:

```python
generate_card(
    queries,
    title=req.title,
    subtitle=req.subtitle,
    output_path=output_path,
    background=background,
    extra_players=get_live_players(),
    card_format=req.format,
)
```

- [ ] **Step 3: Restart server and test with curl**

```bash
curl -s -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"player_ids":[2544,201939,203954,1629029,203999],"title":"TEST","format":"feed"}' \
  --output /tmp/test_feed.png && python3 -c "
from PIL import Image
img = Image.open('/tmp/test_feed.png')
print('Size:', img.size)
assert img.size == (1080, 1350), f'Wrong size: {img.size}'
print('OK')
"
```
Expected output: `Size: (1080, 1350)` and `OK`

- [ ] **Step 4: Commit**

```bash
git add tools/server.py
git commit -m "feat: expose format param in /api/generate endpoint"
```

---

## Task 3: Frontend — Add `format` param to `generateCard()` API function

**Files:**
- Modify: `web/src/lib/api.ts`

- [ ] **Step 1: Update `generateCard()` signature**

Find `generateCard` (line 96) and add `format` param:

```typescript
export async function generateCard(
  playerIds: number[],
  title?: string,
  subtitle?: string,
  background?: string,
  format: "story" | "feed" = "story"
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player_ids: playerIds,
      title: title || "MY MT. RUSHMORE",
      subtitle: subtitle || "",
      format,
      ...(background && { background }),
    }),
  });
  return res.blob();
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd web
npx tsc --noEmit
```
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add web/src/lib/api.ts
git commit -m "feat: add format param to generateCard API function"
```

---

## Task 4: Frontend — Redesign `CardPreview` component

**Files:**
- Modify: `web/src/components/builder/CardPreview.tsx`

- [ ] **Step 1: Rewrite `CardPreview.tsx` completely**

Replace the entire file with:

```typescript
"use client";

import { useEffect, useState } from "react";
import { Download, Copy, Check, X, Share2 } from "lucide-react";

type CardFormat = "story" | "feed";

interface CardPreviewProps {
  url: string;
  onClose: () => void;
  regenerate?: (format: CardFormat) => Promise<Blob>;
}

function XLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.261 5.632L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z" />
    </svg>
  );
}

export function CardPreview({ url, onClose, regenerate }: CardPreviewProps) {
  const [currentUrl, setCurrentUrl] = useState(url);
  const [format, setFormat] = useState<CardFormat>("story");
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);
  const canNativeShare = typeof navigator !== "undefined" && !!navigator.share;
  const canCopyImage =
    typeof navigator !== "undefined" && !!navigator.clipboard?.write;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const handleFormatChange = async (newFormat: CardFormat) => {
    if (newFormat === format || !regenerate || regenerating) return;
    setRegenerating(true);
    try {
      const blob = await regenerate(newFormat);
      const newUrl = URL.createObjectURL(blob);
      if (currentUrl !== url) URL.revokeObjectURL(currentUrl);
      setCurrentUrl(newUrl);
      setFormat(newFormat);
    } finally {
      setRegenerating(false);
    }
  };

  const handleSave = () => {
    const a = document.createElement("a");
    a.href = currentUrl;
    a.download = `rushmore-${format}.png`;
    a.click();
  };

  const handleCopy = async () => {
    try {
      const res = await fetch(currentUrl);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      handleSave();
    }
  };

  const handleNativeShare = async () => {
    try {
      const res = await fetch(currentUrl);
      const blob = await res.blob();
      const file = new File([blob], `rushmore-${format}.png`, { type: "image/png" });
      await navigator.share({ files: [file], title: "My NBA Rushmore" });
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    } catch {
      // cancelled or not supported
    }
  };

  const handleXShare = () => {
    handleSave();
    const text = encodeURIComponent("My NBA Mount Rushmore 🏀 — built on rushmore.gg");
    window.open(`https://x.com/intent/tweet?text=${text}`, "_blank");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-black/90 backdrop-blur-sm"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 shrink-0">
        <span className="text-sm font-semibold text-white/80">Your Card</span>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-white/60 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Image */}
      <div className="flex-1 min-h-0 flex items-center justify-center px-4 py-2 overflow-hidden">
        {regenerating ? (
          <div className="flex flex-col items-center gap-3 text-white/60">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white/80" />
            <span className="text-sm">Generating…</span>
          </div>
        ) : (
          <img
            src={currentUrl}
            alt="Your Top 5 card"
            className="max-h-full max-w-full rounded-xl object-contain shadow-2xl"
          />
        )}
      </div>

      {/* Controls */}
      <div className="shrink-0 px-4 pt-3 pb-5 flex flex-col gap-3">

        {/* Format toggle — only shown if regenerate is available */}
        {regenerate && (
          <div className="flex items-center justify-center">
            <div className="flex rounded-lg border border-white/15 overflow-hidden text-xs font-semibold">
              <button
                onClick={() => handleFormatChange("story")}
                className={`px-4 py-1.5 transition-colors ${
                  format === "story"
                    ? "bg-white/15 text-white"
                    : "text-white/40 hover:text-white/70"
                }`}
              >
                Story
              </button>
              <button
                onClick={() => handleFormatChange("feed")}
                className={`px-4 py-1.5 transition-colors ${
                  format === "feed"
                    ? "bg-white/15 text-white"
                    : "text-white/40 hover:text-white/70"
                }`}
              >
                Feed Post
              </button>
            </div>
          </div>
        )}

        {/* Mobile: native share as hero action */}
        {canNativeShare ? (
          <div className="flex flex-col gap-2">
            <button
              onClick={handleNativeShare}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-3.5 text-sm font-bold text-black hover:bg-white/90 transition-colors"
            >
              {shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}
              {shared ? "Shared!" : "Share"}
            </button>
            <button
              onClick={handleSave}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/20 py-3 text-sm font-semibold text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            >
              <Download className="h-4 w-4" />
              Save to Device
            </button>
          </div>
        ) : (
          /* Desktop: download + X */
          <div className="flex flex-col gap-2">
            <button
              onClick={handleSave}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-3.5 text-sm font-bold text-black hover:bg-white/90 transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              onClick={handleXShare}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/20 py-3 text-sm font-semibold text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            >
              <XLogo className="h-4 w-4" />
              Post on X
            </button>
            <p className="text-center text-xs text-white/30">
              Image saves automatically — attach it to your post in X
            </p>
            {canCopyImage && (
              <button
                onClick={handleCopy}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2.5 text-xs text-white/40 hover:text-white/70 transition-colors"
              >
                {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? "Copied!" : "Copy to clipboard"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd web
npx tsc --noEmit
```
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add web/src/components/builder/CardPreview.tsx
git commit -m "feat: redesign CardPreview with device-aware share flow and format toggle"
```

---

## Task 5: Frontend — Wire `regenerate` prop in parent pages

**Files:**
- Modify: `web/src/app/freestyle/page.tsx`
- Modify: `web/src/components/categories/SplitCategoryPage.tsx`
- Modify: `web/src/app/build/page.tsx`

### freestyle/page.tsx

- [ ] **Step 1: Add `regenerate` callback to `CardPreview` in `freestyle/page.tsx`**

In `web/src/app/freestyle/page.tsx`, find where `generateCard` is called to build the card (around line 88–100). Note the variables used: `playerIds`, `cardTitle`, `background`.

Find the `CardPreview` usage (line 200–202) and update it:

```tsx
{previewUrl && (
  <CardPreview
    url={previewUrl}
    onClose={() => setPreviewUrl(null)}
    regenerate={async (format) => {
      const title = cardTitle.trim() || "MY TOP 5";
      return generateCard(playerIds, title.toUpperCase(), "FREESTYLE", randomBackground(), format);
    }}
  />
)}
```

Note: `playerIds` needs to be in scope. Check if it's a local const inside the build handler. If so, lift it to component state (add `const [lastPlayerIds, setLastPlayerIds] = useState<number[]>([])`) and update it when building:

```typescript
const ids = slots.filter(Boolean).map((p) => (p as Player).id);
setLastPlayerIds(ids);
// ... existing generateCard call uses `ids`
```

Then use `lastPlayerIds` in `regenerate`.

- [ ] **Step 2: Update `SplitCategoryPage.tsx`**

In `web/src/components/categories/SplitCategoryPage.tsx`, find the build handler (around line 95–117). Add state for last player IDs:

```typescript
const [lastPlayerIds, setLastPlayerIds] = useState<number[]>([]);
```

In the build handler, after computing player IDs, save them:
```typescript
const ids = slots.filter(Boolean).map((p) => (p as Player).id);
setLastPlayerIds(ids);
```

Update the `CardPreview` usage (line 197–199):

```tsx
{previewUrl && (
  <CardPreview
    url={previewUrl}
    onClose={() => setPreviewUrl(null)}
    regenerate={async (format) => {
      return generateCard(
        lastPlayerIds,
        data?.title || "MY TOP 5",
        data?.subtitle || "",
        randomBackground(),
        format
      );
    }}
  />
)}
```

Check that `generateCard` is imported in `SplitCategoryPage.tsx`. If not, add it:
```typescript
import { generateCard, type Player } from "@/lib/api";
```

`randomBackground` is already defined as a local function in `SplitCategoryPage.tsx` (line 30) — no import needed.

- [ ] **Step 3: Update `build/page.tsx`**

In `web/src/app/build/page.tsx`, apply the same pattern as freestyle. Add `lastPlayerIds` state, save IDs when building, pass `regenerate` to `CardPreview`:

```tsx
{previewUrl && (
  <CardPreview
    url={previewUrl}
    onClose={() => setPreviewUrl(null)}
    regenerate={async (format) => {
      return generateCard(lastPlayerIds, "MY TOP 5", undefined, undefined, format);
    }}
  />
)}
```

- [ ] **Step 4: Verify TypeScript compiles**

```bash
cd web
npx tsc --noEmit
```
Expected: no errors

- [ ] **Step 5: Commit**

```bash
git add web/src/app/freestyle/page.tsx web/src/components/categories/SplitCategoryPage.tsx web/src/app/build/page.tsx
git commit -m "feat: wire regenerate prop for format toggle in card builder pages"
```

---

## Task 6: End-to-End Verification + Deploy

- [ ] **Step 1: Start backend and frontend**

```bash
# Terminal 1
cd tools && /usr/bin/python3 server.py

# Terminal 2
cd web && npm run dev
```

- [ ] **Step 2: Test Story format (default)**
  - Open http://localhost:3000/freestyle
  - Add 5 players, click "Build Your Card"
  - Modal opens — verify: Share button (mobile) or Download button (desktop) is prominent
  - Verify no format toggle visible on team pages (they don't pass `regenerate`)

- [ ] **Step 3: Test Feed format**
  - Click "Feed Post" toggle in the modal
  - Spinner shows, then image updates
  - Right-click image → "Inspect" or save and check dimensions: should be 1080×1350

- [ ] **Step 4: Test X share (desktop)**
  - Click "Post on X"
  - Image should auto-download
  - X tweet window opens with pre-filled text
  - Hint text "Image saves automatically — attach it to your post in X" is visible

- [ ] **Step 5: Test native share (mobile or mobile simulation)**
  - Open Chrome DevTools → toggle device toolbar
  - The "Share" hero button triggers the system share sheet
  - "Save to Device" is the secondary option

- [ ] **Step 6: Commit and push**

```bash
git push
```
