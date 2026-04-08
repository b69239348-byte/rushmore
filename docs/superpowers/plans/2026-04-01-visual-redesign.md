# Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace gold with basketball orange (#E8540A), rewrite the generated card with the new layout, add Copy button to CardPreview, update all German strings to English basketball slang, and show "Build Your Card" whenever ≥1 player is selected.

**Architecture:** Color change propagates automatically via Tailwind token in globals.css. Card generator (Python/PIL) is rewritten in-place — same API endpoint, different visual output. Card generation state is lifted to SplitCategoryPage so both the desktop sidebar and mobile bar share one flow. CardPreview already exists as a modal — it just needs a Copy button.

**Tech Stack:** Next.js 14 App Router, Tailwind CSS v4 (CSS variable tokens), Python 3.9 + Pillow (PIL)

---

## File Map

| File | Action | Reason |
|---|---|---|
| `web/src/app/globals.css` | Modify | Change 3 color token values |
| `tools/generate_card.py` | Rewrite | New card layout (Option A) |
| `web/src/components/builder/CardPreview.tsx` | Modify | Add Copy button, update text |
| `web/src/components/builder/CardBuilderPanel.tsx` | Modify | Remove inline preview, add `onBuildCard` prop, update text |
| `web/src/components/builder/ExportButton.tsx` | Modify | Allow ≥1 slot, update text |
| `web/src/components/categories/SelectionBar.tsx` | Modify | Button at ≥1 slot, update text, remove inline generate |
| `web/src/components/categories/SplitCategoryPage.tsx` | Modify | Lift card generation state, pass `onBuildCard` to children |

---

## Task 1: Color Tokens

**Files:**
- Modify: `web/src/app/globals.css`

- [ ] **Step 1: Update the three token values**

In `globals.css`, replace:
```css
--color-gold: #c9a84c;
--color-gold-dim: #a08838;
--color-gold-bright: #dfc06a;
```
With:
```css
--color-gold: #E8540A;
--color-gold-dim: #b8420a;
--color-gold-bright: #ff6b30;
```

- [ ] **Step 2: Verify in browser**

Start the Next.js dev server if not running:
```bash
cd /Users/razor/projects/rushmore/web && npm run dev
```
Open http://localhost:3000 — all gold elements (rank badges, CTA buttons, active nav items) should now appear orange. No component files need changes.

- [ ] **Step 3: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/app/globals.css
git commit -m "feat: switch accent color from gold to basketball orange #E8540A"
```

---

## Task 2: Rewrite generate_card.py

**Files:**
- Modify: `tools/generate_card.py`

The current file is a full rewrite target. Keep the same public interface: `generate_card(queries, title, subtitle, output_path)` and `load_players()`.

- [ ] **Step 1: Write a quick smoke-test script**

Create `tools/_test_card.py`:
```python
"""Quick smoke test — run after rewriting generate_card.py"""
import tempfile, os
from pathlib import Path
from generate_card import generate_card

with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    out = tmp.name

# Use real player IDs from players.json
generate_card(
    queries=["203999", "1629029", "1629627", "1629029", "203507"],
    title="MY TOP 5",
    subtitle="ALL-TIME GREATS",
    output_path=out,
)

from PIL import Image
img = Image.open(out)
assert img.size == (1080, 1920), f"Wrong size: {img.size}"
assert img.mode in ("RGB", "RGBA"), f"Wrong mode: {img.mode}"
print(f"✓ Card generated: {img.size}, {img.mode}, {os.path.getsize(out)//1024}KB → {out}")
```

- [ ] **Step 2: Run smoke test against the OLD implementation to confirm it passes**
```bash
cd /Users/razor/projects/rushmore/tools && /usr/bin/python3 _test_card.py
```
Expected: `✓ Card generated: (1080, 1920), RGB, ...KB`

- [ ] **Step 3: Rewrite generate_card.py**

Replace the full file content:
```python
"""
Rushmore — Card Generator (v3, basketball orange redesign)
Layout: dark bg, orange rank numbers (01-05), circular headshot, name + jersey, stats line.
API: generate_card(queries, title, subtitle, output_path) — unchanged.
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

# --- Constants ---
WIDTH, HEIGHT = 1080, 1920
PAD = 60
ORANGE = "#E8540A"
ORANGE_DIM = "#b8420a"
BG_TOP = "#0a0a12"
BG_BOT = "#080810"
TEXT_WHITE = "#f0f0f0"
TEXT_GRAY = "#888899"
TEXT_MUTED = "#444455"

HEADSHOT_DIR = Path(__file__).parent.parent / "assets" / "headshots"
DB_PATH = Path(__file__).parent.parent / "players.json"

ROW_COUNT = 5
TITLE_H = 200
FOOTER_H = 90
ROW_AREA_H = HEIGHT - TITLE_H - FOOTER_H
ROW_H = ROW_AREA_H // ROW_COUNT
ROW_GAP = 10


def load_players():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def _find_player(db, query: str):
    """Find player by numeric ID string or name substring."""
    if query.isdigit():
        pid = int(query)
        return next((p for p in db if p["id"] == pid), None)
    q = query.lower()
    return next((p for p in db if q in p["name"].lower()), None)


def _load_headshot(player_id: int, size: int) -> Image.Image | None:
    """Load and crop headshot to a circle. Returns None if not found."""
    for ext in ("jpg", "jpeg", "png"):
        path = HEADSHOT_DIR / f"{player_id}.{ext}"
        if path.exists():
            img = Image.open(path).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            # Circular mask
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
            result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            result.paste(img, mask=mask)
            return result
    return None


def _initials_circle(name: str, size: int) -> Image.Image:
    """Orange circle with white initials — fallback when no headshot."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, size - 1, size - 1), fill=ORANGE)
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    font_size = size // 3
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) // 2, (size - th) // 2), initials, fill=TEXT_WHITE, font=font)
    return img


def _draw_gradient_bg(draw, width, height):
    """Vertical dark gradient background."""
    for y in range(height):
        t = y / height
        r = int(0x0a + t * (0x08 - 0x0a))
        g = int(0x0a + t * (0x08 - 0x0a))
        b = int(0x12 + t * (0x10 - 0x12))
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _hex(color: str):
    """'#RRGGBB' → (R, G, B)"""
    c = color.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))


def _font(size: int, bold=False):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_card(queries, title="MY TOP 5", subtitle="ALL-TIME GREATS", output_path="card.png"):
    db = load_players()
    players = []
    for q in queries[:5]:
        p = _find_player(db, str(q))
        if p:
            players.append(p)

    img = Image.new("RGB", (WIDTH, HEIGHT), _hex(BG_TOP))
    draw = ImageDraw.Draw(img)
    _draw_gradient_bg(draw, WIDTH, HEIGHT)

    # --- Title area ---
    title_font = _font(72, bold=True)
    sub_font = _font(36)

    title_bbox = draw.textbbox((0, 0), title.upper(), font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((WIDTH - title_w) // 2, 60), title.upper(), fill=_hex(TEXT_WHITE), font=title_font)

    sub_bbox = draw.textbbox((0, 0), subtitle.upper(), font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((WIDTH - sub_w) // 2, 60 + 80), subtitle.upper(), fill=_hex(ORANGE), font=sub_font)

    # --- Player rows ---
    rank_font = _font(96, bold=True)
    name_font = _font(52, bold=True)
    jersey_font = _font(44)
    stats_font = _font(36)

    PHOTO_SIZE = int(ROW_H * 0.72)
    ROW_PAD_V = (ROW_H - PHOTO_SIZE) // 2

    for i, player in enumerate(players):
        row_y = TITLE_H + i * ROW_H

        # Row background (subtle highlight for rank 1)
        row_bg = (255, 255, 255, 12) if i == 0 else (255, 255, 255, 5)
        overlay = Image.new("RGBA", (WIDTH - PAD * 2, ROW_H - ROW_GAP), row_bg)
        img.paste(overlay, (PAD, row_y + ROW_GAP // 2), overlay)

        # Orange left accent bar for rank 1
        if i == 0:
            draw.rectangle([PAD, row_y + ROW_GAP // 2, PAD + 6, row_y + ROW_H - ROW_GAP // 2], fill=_hex(ORANGE))

        # Rank number
        rank_str = f"0{i + 1}" if i < 9 else str(i + 1)
        rank_color = _hex(ORANGE) if i == 0 else _hex(ORANGE_DIM)
        rank_x = PAD + 20
        rank_bbox = draw.textbbox((0, 0), rank_str, font=rank_font)
        rank_h = rank_bbox[3] - rank_bbox[1]
        draw.text((rank_x, row_y + (ROW_H - rank_h) // 2), rank_str, fill=rank_color, font=rank_font)

        # Headshot
        RANK_W = 120
        photo_x = PAD + RANK_W + 20
        photo_y = row_y + ROW_PAD_V

        headshot = _load_headshot(player["id"], PHOTO_SIZE)
        if headshot is None:
            headshot = _initials_circle(player["name"], PHOTO_SIZE)

        if headshot.mode == "RGBA":
            img.paste(headshot, (photo_x, photo_y), headshot)
        else:
            img.paste(headshot, (photo_x, photo_y))

        # Name + jersey
        TEXT_X = photo_x + PHOTO_SIZE + 30
        name = player["name"].upper()
        jersey = f"#{player.get('jersey', '')}" if player.get("jersey") else ""
        name_color = _hex(TEXT_WHITE)

        name_y = row_y + ROW_PAD_V + 10
        draw.text((TEXT_X, name_y), name, fill=name_color, font=name_font)

        if jersey:
            name_bbox = draw.textbbox((TEXT_X, name_y), name, font=name_font)
            jersey_x = name_bbox[2] + 16
            draw.text((jersey_x, name_y + 6), jersey, fill=_hex(ORANGE), font=jersey_font)

        # Stats line
        ppg = player.get("ppg", 0)
        rpg = player.get("rpg", 0)
        apg = player.get("apg", 0)
        stats_str = f"{ppg}  ·  {rpg} RPG  ·  {apg} APG"
        stats_y = name_y + 64
        draw.text((TEXT_X, stats_y), stats_str, fill=_hex(TEXT_GRAY), font=stats_font)

    # --- Footer ---
    footer_font = _font(32)
    footer_text = "RUSHMORE.APP"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(
        ((WIDTH - footer_w) // 2, HEIGHT - FOOTER_H + 24),
        footer_text,
        fill=_hex(TEXT_MUTED),
        font=footer_font,
    )

    img.convert("RGB").save(output_path, "PNG", optimize=True)


if __name__ == "__main__":
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name
    generate_card(
        queries=sys.argv[1:] or ["203999", "1629029", "1629627", "201142", "203507"],
        title="MY TOP 5",
        subtitle="ALL-TIME GREATS",
        output_path=out,
    )
    print(f"Card saved to: {out}")
```

- [ ] **Step 4: Run smoke test against the new implementation**
```bash
cd /Users/razor/projects/rushmore/tools && /usr/bin/python3 _test_card.py
```
Expected: `✓ Card generated: (1080, 1920), RGB, ...KB`

- [ ] **Step 5: Visually inspect the generated card**
```bash
open $(cd /Users/razor/projects/rushmore/tools && /usr/bin/python3 -c "
import tempfile; t = tempfile.NamedTemporaryFile(suffix='.png', delete=False); print(t.name)
" && /usr/bin/python3 -c "
from generate_card import generate_card
import sys
out = sys.argv[1]
generate_card(['203999','1629029','1629627','201142','203507'], 'MY TOP 5', 'ALL-TIME GREATS', out)
" /tmp/rushmore_preview.png && echo /tmp/rushmore_preview.png)
```
Simpler version:
```bash
cd /Users/razor/projects/rushmore/tools
/usr/bin/python3 -c "
from generate_card import generate_card
generate_card(['203999','1629029','1629627','201142','203507'], 'MY TOP 5', 'ALL-TIME GREATS', '/tmp/card_preview.png')
"
open /tmp/card_preview.png
```
Check: dark background, orange rank numbers (01–05), circular headshots or orange initials fallback, stats line, footer.

- [ ] **Step 6: Commit**
```bash
cd /Users/razor/projects/rushmore
git add tools/generate_card.py tools/_test_card.py
git commit -m "feat: rewrite card generator with basketball orange layout (v3)"
```

---

## Task 3: Update CardPreview

**Files:**
- Modify: `web/src/components/builder/CardPreview.tsx`

- [ ] **Step 1: Replace the file**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Download, Copy, Check, X } from "lucide-react";

interface CardPreviewProps {
  url: string;
  onClose: () => void;
}

export function CardPreview({ url, onClose }: CardPreviewProps) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const handleSave = () => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "rushmore.png";
    a.click();
  };

  const handleCopy = async () => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not supported — fall back to save
      handleSave();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative max-h-[90vh] max-w-sm w-full flex flex-col gap-3">
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 rounded-lg p-1.5 text-text-secondary hover:text-text transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <img
          src={url}
          alt="Your Top 5 card"
          className="w-full rounded-xl"
        />

        <div className="flex gap-2">
          <button
            onClick={handleSave}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gold py-3 text-sm font-bold text-bg hover:bg-gold-bright transition-colors"
          >
            <Download className="h-4 w-4" />
            Save
          </button>
          <button
            onClick={handleCopy}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-3 text-sm font-semibold text-text-secondary hover:bg-card-hover hover:text-text transition-colors"
          >
            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify in browser**

Open http://localhost:3000/build, add 1+ players, click Export Image, check: modal shows card + Save + Copy buttons. Esc closes it.

- [ ] **Step 3: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/components/builder/CardPreview.tsx
git commit -m "feat: add Copy button and update text in CardPreview"
```

---

## Task 4: Update CardBuilderPanel

**Files:**
- Modify: `web/src/components/builder/CardBuilderPanel.tsx`

Remove all card generation state (`cardUrl`, `generating`, `error`, `copied`). The panel now only manages the slot list. Card generation is triggered via `onBuildCard` callback — the parent (`SplitCategoryPage`) owns the preview state.

- [ ] **Step 1: Replace the file**

```tsx
"use client";

import { ChevronUp, ChevronDown, X, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Player } from "@/lib/api";

interface CardBuilderPanelProps {
  slots: (Player | null)[];
  onRemove: (index: number) => void;
  onReorder: (from: number, to: number) => void;
  onBuildCard: () => void;
  onReset: () => void;
}

export function CardBuilderPanel({
  slots,
  onRemove,
  onReorder,
  onBuildCard,
  onReset,
}: CardBuilderPanelProps) {
  const filledCount = slots.filter(Boolean).length;

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-text-tertiary">
        Your Starting 5
      </p>

      <div className="flex flex-col gap-2">
        {slots.map((player, i) => (
          <div
            key={i}
            className={cn(
              "flex items-center gap-3 rounded-xl border px-3 py-2.5 transition-all",
              player ? "border-border-subtle bg-card" : "border-dashed border-border"
            )}
          >
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-surface text-xs font-bold text-gold">
              {i + 1}
            </div>
            {player ? (
              <>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-semibold">{player.name}</div>
                  {player.position && (
                    <div className="text-xs text-text-tertiary">{player.position}</div>
                  )}
                </div>
                <div className="flex shrink-0 gap-0.5">
                  {i > 0 && slots[i - 1] !== null && (
                    <button
                      onClick={() => onReorder(i, i - 1)}
                      className="rounded p-1 text-text-tertiary hover:bg-surface hover:text-text transition-colors"
                    >
                      <ChevronUp className="h-3.5 w-3.5" />
                    </button>
                  )}
                  {i < 4 && slots[i + 1] !== null && (
                    <button
                      onClick={() => onReorder(i, i + 1)}
                      className="rounded p-1 text-text-tertiary hover:bg-surface hover:text-text transition-colors"
                    >
                      <ChevronDown className="h-3.5 w-3.5" />
                    </button>
                  )}
                  <button
                    onClick={() => onRemove(i)}
                    className="rounded p-1 text-text-tertiary hover:bg-surface hover:text-text transition-colors"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              </>
            ) : (
              <span className="text-xs text-text-tertiary">Add a baller</span>
            )}
          </div>
        ))}
      </div>

      {filledCount > 0 && (
        <div className="flex flex-col gap-2">
          <button
            onClick={onBuildCard}
            className="flex items-center justify-center gap-2 rounded-xl bg-gold py-3 text-sm font-bold text-bg transition-colors hover:bg-gold-bright"
          >
            <Sparkles className="h-4 w-4" />
            Build Your Card
          </button>
          <button
            onClick={onReset}
            className="text-center text-xs text-text-tertiary hover:text-text-secondary transition-colors"
          >
            ↺ Reset
          </button>
        </div>
      )}

      {filledCount === 0 && (
        <p className="text-center text-xs text-text-tertiary">5 spots left</p>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/components/builder/CardBuilderPanel.tsx
git commit -m "feat: refactor CardBuilderPanel — extract card gen, add onBuildCard prop, update text"
```

---

## Task 5: Update SplitCategoryPage

**Files:**
- Modify: `web/src/components/categories/SplitCategoryPage.tsx`

Lift card generation + preview state here. Pass `onBuildCard` to both `CardBuilderPanel` and `SelectionBar`.

- [ ] **Step 1: Replace the file**

```tsx
"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { Loader2 } from "lucide-react";
import { fetchCategory, generateCard, type CategoryResult, type Player } from "@/lib/api";
import { PlayerList } from "./PlayerList";
import { SelectionBar } from "./SelectionBar";
import { CardBuilderPanel } from "@/components/builder/CardBuilderPanel";
import { CardPreview } from "@/components/builder/CardPreview";
import { cn } from "@/lib/utils";

export interface CategoryPill {
  label: string;
  path: string;
  params?: Record<string, string | number>;
  cardSubtitle: string;
}

interface SplitCategoryPageProps {
  title: string;
  categories: CategoryPill[];
}

export function SplitCategoryPage({ title, categories }: SplitCategoryPageProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [data, setData] = useState<CategoryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [slots, setSlots] = useState<(Player | null)[]>([null, null, null, null, null]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const active = categories[activeIndex];
  const selectedIds = useMemo(
    () => new Set(slots.filter((p): p is Player => p !== null).map((p) => p.id)),
    [slots]
  );

  useEffect(() => {
    setLoading(true);
    setSlots([null, null, null, null, null]);
    fetchCategory(active.path, active.params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeIndex]);

  const handlePlayerClick = useCallback((player: Player) => {
    setSlots((prev) => {
      if (prev.some((p) => p?.id === player.id)) return prev;
      const nextEmpty = prev.indexOf(null);
      if (nextEmpty === -1) return prev;
      const next = [...prev];
      next[nextEmpty] = player;
      return next;
    });
  }, []);

  const handleRemove = useCallback((index: number) => {
    setSlots((prev) => {
      const next = [...prev];
      next[index] = null;
      const filled = next.filter((s): s is Player => s !== null);
      return [...filled, ...Array(5 - filled.length).fill(null)];
    });
  }, []);

  const handleReorder = useCallback((from: number, to: number) => {
    setSlots((prev) => {
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next;
    });
  }, []);

  const handleReset = useCallback(() => {
    setSlots([null, null, null, null, null]);
  }, []);

  const handleBuildCard = useCallback(async () => {
    const playerIds = slots.filter(Boolean).map((p) => (p as Player).id);
    if (playerIds.length === 0) return;
    setGenerating(true);
    try {
      const blob = await generateCard(
        playerIds,
        "MY TOP 5",
        data?.subtitle || active.cardSubtitle
      );
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (err) {
      console.error("Card generation failed:", err);
    } finally {
      setGenerating(false);
    }
  }, [slots, data, active, previewUrl]);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border-subtle px-4 py-4 md:px-6">
        <h1 className="text-xl font-black tracking-tight">{title}</h1>
      </div>

      <div className="flex gap-2 overflow-x-auto border-b border-border-subtle px-4 py-3 md:px-6">
        {categories.map((cat, i) => (
          <button
            key={cat.path}
            onClick={() => setActiveIndex(i)}
            className={cn(
              "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
              i === activeIndex
                ? "bg-gold text-bg"
                : "bg-surface text-text-secondary hover:bg-card-hover hover:text-text"
            )}
          >
            {cat.label}
          </button>
        ))}
      </div>

      <div className="flex min-h-0 flex-1">
        <div className="flex-1 overflow-y-auto pb-32 md:pb-8">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
            </div>
          ) : data ? (
            <div className="px-4 py-4 md:px-6">
              <PlayerList
                players={data.players}
                selectedIds={selectedIds}
                onPlayerClick={handlePlayerClick}
              />
            </div>
          ) : null}
        </div>

        <aside className="hidden w-80 shrink-0 overflow-y-auto border-l border-border-subtle p-4 md:block">
          <div className="sticky top-4">
            <CardBuilderPanel
              slots={slots}
              onRemove={handleRemove}
              onReorder={handleReorder}
              onReset={handleReset}
              onBuildCard={handleBuildCard}
            />
          </div>
        </aside>
      </div>

      <div className="md:hidden">
        <SelectionBar
          slots={slots}
          onRemove={handleRemove}
          onReorder={handleReorder}
          onReset={handleReset}
          onBuildCard={handleBuildCard}
          generating={generating}
        />
      </div>

      {previewUrl && (
        <CardPreview url={previewUrl} onClose={() => setPreviewUrl(null)} />
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/components/categories/SplitCategoryPage.tsx
git commit -m "feat: lift card generation to SplitCategoryPage, wire onBuildCard to panel + bar"
```

---

## Task 6: Update SelectionBar

**Files:**
- Modify: `web/src/components/categories/SelectionBar.tsx`

Remove inline card generation. Accept `onBuildCard` + `generating` props from parent. Show button at ≥1 slot.

- [ ] **Step 1: Replace the file**

```tsx
"use client";

import { useState } from "react";
import { X, ChevronUp, ChevronDown, Loader2, Sparkles } from "lucide-react";
import type { Player } from "@/lib/api";

interface SelectionBarProps {
  slots: (Player | null)[];
  onRemove: (index: number) => void;
  onReorder: (from: number, to: number) => void;
  onReset?: () => void;
  onBuildCard: () => void;
  generating?: boolean;
}

export function SelectionBar({
  slots,
  onRemove,
  onReorder,
  onReset,
  onBuildCard,
  generating = false,
}: SelectionBarProps) {
  const [expanded, setExpanded] = useState(false);
  const filledCount = slots.filter(Boolean).length;

  if (filledCount === 0) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 md:left-56">
      <div className="mx-auto max-w-3xl px-4">
        <div className="rounded-t-2xl border border-b-0 border-border-subtle bg-surface/95 backdrop-blur-md shadow-2xl">
          {/* Collapsed bar */}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex w-full items-center justify-between px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold">Your Starting 5</span>
              <div className="flex gap-1.5">
                {slots.map((s, i) => (
                  <div
                    key={i}
                    className={`h-2.5 w-2.5 rounded-full transition-colors ${
                      s ? "bg-gold" : "bg-border"
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs text-text-tertiary">{filledCount}/5</span>
            </div>

            <div className="flex items-center gap-2">
              {onReset && (
                <button
                  onClick={(e) => { e.stopPropagation(); onReset(); }}
                  className="text-xs text-text-tertiary hover:text-text-secondary transition-colors"
                >
                  ↺ Reset
                </button>
              )}
              <button
                onClick={(e) => { e.stopPropagation(); onBuildCard(); }}
                disabled={generating}
                className="flex items-center gap-1.5 rounded-lg bg-gold px-3 py-1.5 text-xs font-bold text-bg hover:bg-gold-bright transition-colors disabled:opacity-50"
              >
                {generating ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Sparkles className="h-3.5 w-3.5" />
                )}
                {generating ? "Cooking…" : "Build Your Card"}
              </button>
              {expanded ? (
                <ChevronDown className="h-4 w-4 text-text-tertiary" />
              ) : (
                <ChevronUp className="h-4 w-4 text-text-tertiary" />
              )}
            </div>
          </button>

          {/* Expanded slot list */}
          {expanded && (
            <div className="border-t border-border-subtle px-4 pb-4 pt-2">
              <div className="flex flex-col gap-1.5">
                {slots.map((player, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2 ${
                      player
                        ? "bg-card border border-border-subtle"
                        : "border border-dashed border-border"
                    }`}
                  >
                    <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded text-xs font-bold text-gold bg-surface">
                      {i + 1}
                    </div>
                    {player ? (
                      <>
                        <div className="min-w-0 flex-1">
                          <span className="text-sm font-medium truncate block">{player.name}</span>
                        </div>
                        <div className="flex gap-0.5">
                          {i > 0 && slots[i - 1] !== null && (
                            <button onClick={() => onReorder(i, i - 1)} className="rounded p-1 text-text-tertiary hover:text-text hover:bg-surface transition-colors">
                              <ChevronUp className="h-3.5 w-3.5" />
                            </button>
                          )}
                          {i < 4 && slots[i + 1] !== null && (
                            <button onClick={() => onReorder(i, i + 1)} className="rounded p-1 text-text-tertiary hover:text-text hover:bg-surface transition-colors">
                              <ChevronDown className="h-3.5 w-3.5" />
                            </button>
                          )}
                          <button onClick={() => onRemove(i)} className="rounded p-1 text-text-tertiary hover:text-text hover:bg-surface transition-colors">
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </>
                    ) : (
                      <span className="text-xs text-text-tertiary">Add a baller</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify in browser (mobile viewport)**

Open http://localhost:3000/aktuell, select 1 player — bottom bar appears with "Build Your Card". Click it — card generates and CardPreview modal opens.

- [ ] **Step 3: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/components/categories/SelectionBar.tsx
git commit -m "feat: update SelectionBar — Build Your Card at ≥1 player, English slang, remove inline gen"
```

---

## Task 7: Update ExportButton + build/page

**Files:**
- Modify: `web/src/components/builder/ExportButton.tsx`

- [ ] **Step 1: Replace ExportButton.tsx**

```tsx
"use client";

import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { generateCard, type Player } from "@/lib/api";

interface ExportButtonProps {
  slots: (Player | null)[];
  disabled: boolean;
  onPreview: (url: string) => void;
}

export function ExportButton({ slots, disabled, onPreview }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    const playerIds = slots.filter(Boolean).map((p) => (p as Player).id);
    if (playerIds.length === 0) return;
    setLoading(true);
    try {
      const blob = await generateCard(playerIds, "MY TOP 5", "ALL-TIME GREATS");
      onPreview(URL.createObjectURL(blob));
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled || loading}
      className="flex w-full items-center justify-center gap-2 rounded-xl bg-gold py-3.5 text-sm font-bold text-bg transition-all hover:bg-gold-bright disabled:opacity-25 disabled:cursor-not-allowed"
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Sparkles className="h-4 w-4" />
      )}
      {loading ? "Cooking…" : "Build Your Card"}
    </button>
  );
}
```

- [ ] **Step 2: Update build/page.tsx — enable button at ≥1 slot**

In `web/src/app/build/page.tsx`, change:
```tsx
disabled={filledCount < 5}
```
To:
```tsx
disabled={filledCount === 0}
```

- [ ] **Step 3: Verify in browser**

Open http://localhost:3000/build — "Build Your Card" button is active after selecting 1 player, shows "Cooking…" while generating, opens CardPreview modal with Save + Copy buttons.

- [ ] **Step 4: Commit**
```bash
cd /Users/razor/projects/rushmore/web
git add src/components/builder/ExportButton.tsx src/app/build/page.tsx
git commit -m "feat: update ExportButton — Build Your Card, Cooking…, enable at ≥1 slot"
```
