# Split-View Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Neue Legenden- und Aktuell-Seiten mit Split-View Layout — links Spielerliste mit Kategorie-Pills, rechts live Card Builder Panel.

**Architecture:** Zwei neue Routen (`/legenden`, `/aktuell`) nutzen eine shared `SplitCategoryPage` Komponente. Auf Desktop rendert diese ein zweispaltiges Layout mit `CardBuilderPanel` rechts (sticky). Auf Mobile bleibt die bestehende `SelectionBar` (Sticky Bottom Bar). Die Sidebar wird auf 4 flache Links reduziert.

**Tech Stack:** Next.js 16 App Router, TypeScript, Tailwind CSS, shadcn/ui, Lucide React

---

## File Map

| Aktion | Datei | Verantwortung |
|---|---|---|
| Create | `web/src/components/builder/CardBuilderPanel.tsx` | Rechtes Panel: Slots, Generate, PNG inline |
| Create | `web/src/components/categories/SplitCategoryPage.tsx` | Shared split-view layout + State |
| Create | `web/src/app/legenden/page.tsx` | Legenden-Route mit Pills-Konfiguration |
| Create | `web/src/app/aktuell/page.tsx` | Aktuell-Route mit Pills-Konfiguration |
| Modify | `web/src/components/layout/Sidebar.tsx` | 4 flache Links, kein Baum |

---

## Task 1: CardBuilderPanel

**Files:**
- Create: `web/src/components/builder/CardBuilderPanel.tsx`

- [ ] **Schritt 1: Datei anlegen mit Typen und leerem Export**

```tsx
// web/src/components/builder/CardBuilderPanel.tsx
"use client";

import { useState } from "react";
import { X, Download, Loader2, ChevronUp, ChevronDown, Sparkles } from "lucide-react";
import { generateCard, type Player } from "@/lib/api";
import { cn } from "@/lib/utils";

interface CardBuilderPanelProps {
  slots: (Player | null)[];
  onRemove: (index: number) => void;
  onReorder: (from: number, to: number) => void;
  categorySubtitle: string;
}

export function CardBuilderPanel({
  slots,
  onRemove,
  onReorder,
  categorySubtitle,
}: CardBuilderPanelProps) {
  const [generating, setGenerating] = useState(false);
  const [cardUrl, setCardUrl] = useState<string | null>(null);

  const filledCount = slots.filter(Boolean).length;
  const allFilled = filledCount === 5;

  const handleGenerate = async () => {
    const playerIds = slots.filter(Boolean).map((p) => (p as Player).id);
    setGenerating(true);
    try {
      const blob = await generateCard(playerIds, "MY MT. RUSHMORE", categorySubtitle);
      if (cardUrl) URL.revokeObjectURL(cardUrl);
      setCardUrl(URL.createObjectURL(blob));
    } catch (err) {
      console.error("Card generation failed:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!cardUrl) return;
    const a = document.createElement("a");
    a.href = cardUrl;
    a.download = "rushmore.png";
    a.click();
  };

  const handleCopy = async () => {
    if (!cardUrl) return;
    try {
      const res = await fetch(cardUrl);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  const handleReset = () => {
    if (cardUrl) URL.revokeObjectURL(cardUrl);
    setCardUrl(null);
  };

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-text-tertiary">
        Dein Top 5
      </p>

      {/* Slots */}
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
              <span className="text-xs text-text-tertiary">Spieler auswählen</span>
            )}
          </div>
        ))}
      </div>

      {/* State: all filled, no card yet */}
      {allFilled && !cardUrl && (
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center justify-center gap-2 rounded-xl bg-gold py-3 text-sm font-bold text-bg transition-colors hover:bg-gold-bright disabled:opacity-50"
        >
          {generating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          {generating ? "Wird erstellt…" : "Karte erstellen"}
        </button>
      )}

      {/* State: not all filled */}
      {!allFilled && !cardUrl && (
        <p className="text-center text-xs text-text-tertiary">
          Noch {5 - filledCount} {5 - filledCount === 1 ? "Spieler" : "Spieler"} auswählen
        </p>
      )}

      {/* State: card generated */}
      {cardUrl && (
        <div className="flex flex-col gap-3">
          <img
            src={cardUrl}
            alt="Deine Rushmore Karte"
            className="w-full rounded-xl"
          />
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gold py-2.5 text-sm font-bold text-bg transition-colors hover:bg-gold-bright"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              onClick={handleCopy}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-2.5 text-sm text-text-secondary transition-colors hover:bg-card-hover hover:text-text"
            >
              Kopieren
            </button>
          </div>
          <button
            onClick={handleReset}
            className="text-center text-xs text-text-tertiary hover:text-text-secondary transition-colors"
          >
            ↺ Neu starten
          </button>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Schritt 2: Build-Check**

```bash
cd web && npm run build 2>&1 | tail -20
```

Erwartet: ✓ Compiled successfully (CardBuilderPanel wird noch nicht importiert, daher keine Route — das ist ok)

---

## Task 2: SplitCategoryPage

**Files:**
- Create: `web/src/components/categories/SplitCategoryPage.tsx`

- [ ] **Schritt 1: Datei anlegen**

```tsx
// web/src/components/categories/SplitCategoryPage.tsx
"use client";

import { useEffect, useState, useCallback } from "react";
import { Loader2 } from "lucide-react";
import { fetchCategory, type CategoryResult, type Player } from "@/lib/api";
import { PlayerList } from "./PlayerList";
import { SelectionBar } from "./SelectionBar";
import { CardBuilderPanel } from "@/components/builder/CardBuilderPanel";
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

  const active = categories[activeIndex];
  const selectedIds = new Set(slots.filter(Boolean).map((p) => (p as Player).id));

  useEffect(() => {
    setLoading(true);
    setSlots([null, null, null, null, null]);
    fetchCategory(active.path, active.params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [active.path, JSON.stringify(active.params)]);

  const handlePlayerClick = useCallback(
    (player: Player) => {
      if (selectedIds.has(player.id)) return;
      setSlots((prev) => {
        const nextEmpty = prev.indexOf(null);
        if (nextEmpty === -1) return prev;
        const next = [...prev];
        next[nextEmpty] = player;
        return next;
      });
    },
    [selectedIds]
  );

  const handleRemove = useCallback((index: number) => {
    setSlots((prev) => {
      const next = [...prev];
      next[index] = null;
      return next;
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

  return (
    <div className="flex h-full flex-col">
      {/* Page title */}
      <div className="border-b border-border-subtle px-4 py-4 md:px-6">
        <h1 className="text-xl font-black tracking-tight">{title}</h1>
      </div>

      {/* Pills */}
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

      {/* Split view */}
      <div className="flex min-h-0 flex-1">
        {/* Left: player list */}
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

        {/* Right: card builder — desktop only */}
        <aside className="hidden w-80 shrink-0 overflow-y-auto border-l border-border-subtle p-4 md:block">
          <div className="sticky top-4">
            <CardBuilderPanel
              slots={slots}
              onRemove={handleRemove}
              onReorder={handleReorder}
              categorySubtitle={data?.subtitle || active.cardSubtitle}
            />
          </div>
        </aside>
      </div>

      {/* Mobile: sticky bottom bar */}
      <div className="md:hidden">
        <SelectionBar
          slots={slots}
          onRemove={handleRemove}
          onReorder={handleReorder}
          categoryTitle={data?.subtitle || active.cardSubtitle}
        />
      </div>
    </div>
  );
}
```

- [ ] **Schritt 2: Build-Check**

```bash
cd web && npm run build 2>&1 | tail -20
```

Erwartet: ✓ Compiled successfully

---

## Task 3: Legenden-Seite

**Files:**
- Create: `web/src/app/legenden/page.tsx`

- [ ] **Schritt 1: Datei anlegen**

```tsx
// web/src/app/legenden/page.tsx
import { SplitCategoryPage, type CategoryPill } from "@/components/categories/SplitCategoryPage";

const CATEGORIES: CategoryPill[] = [
  { label: "All-Time", path: "all-time", params: { limit: 5 }, cardSubtitle: "ALL-TIME GREATEST" },
  { label: "Guards", path: "position/G", params: { limit: 5 }, cardSubtitle: "TOP GUARDS" },
  { label: "Forwards", path: "position/F", params: { limit: 5 }, cardSubtitle: "TOP FORWARDS" },
  { label: "Centers", path: "position/C", params: { limit: 5 }, cardSubtitle: "TOP CENTERS" },
  { label: "MVP", path: "awards/mvp", params: { limit: 5 }, cardSubtitle: "MVP LEGENDS" },
  { label: "All-NBA", path: "awards/all-nba", params: { limit: 5 }, cardSubtitle: "ALL-NBA SELECTIONS" },
  { label: "DPOY", path: "awards/dpoy", params: { limit: 5 }, cardSubtitle: "DEFENSIVE GREATS" },
  { label: "ROY", path: "awards/roy", params: { limit: 5 }, cardSubtitle: "ROOKIE LEGENDS" },
  { label: "Finals MVP", path: "awards/finals-mvp", params: { limit: 5 }, cardSubtitle: "FINALS HEROES" },
];

export default function LegendenPage() {
  return <SplitCategoryPage title="Legenden" categories={CATEGORIES} />;
}
```

- [ ] **Schritt 2: Build-Check**

```bash
cd web && npm run build 2>&1 | tail -20
```

Erwartet: Route `/legenden` erscheint in der Build-Ausgabe als `○ /legenden`

---

## Task 4: Aktuell-Seite

**Files:**
- Create: `web/src/app/aktuell/page.tsx`

- [ ] **Schritt 1: Datei anlegen**

```tsx
// web/src/app/aktuell/page.tsx
import { SplitCategoryPage, type CategoryPill } from "@/components/categories/SplitCategoryPage";

const CATEGORIES: CategoryPill[] = [
  { label: "Diese Saison", path: "current-season", params: { limit: 30 }, cardSubtitle: "THIS SEASON" },
  { label: "Aktive Stars", path: "active", params: { limit: 30 }, cardSubtitle: "ACTIVE STARS" },
];

export default function AktuellPage() {
  return <SplitCategoryPage title="Aktuell" categories={CATEGORIES} />;
}
```

- [ ] **Schritt 2: Build-Check**

```bash
cd web && npm run build 2>&1 | tail -20
```

Erwartet: Route `/aktuell` erscheint als `○ /aktuell`

---

## Task 5: Sidebar vereinfachen

**Files:**
- Modify: `web/src/components/layout/Sidebar.tsx`

- [ ] **Schritt 1: `SidebarContent` ersetzen**

Ersetze die gesamte `SidebarContent` Funktion (Zeile 24–79) durch:

```tsx
export function SidebarContent() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col py-4 px-3 gap-1">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 px-3 py-2 mb-3">
        <Mountain className="h-5 w-5 text-gold" />
        <span className="text-lg font-black tracking-tight">RUSHMORE</span>
      </Link>

      <NavItem href="/" icon={Home} label="Home" active={pathname === "/"} />
      <NavItem href="/legenden" icon={Trophy} label="Legenden" active={pathname.startsWith("/legenden")} />
      <NavItem href="/aktuell" icon={Flame} label="Aktuell" active={pathname.startsWith("/aktuell")} />
      <NavItem href="/categories/teams" icon={Users} label="Teams" active={pathname.startsWith("/categories/teams")} />
    </nav>
  );
}
```

- [ ] **Schritt 2: Nicht mehr benötigte Imports entfernen**

Entferne aus dem Import-Block: `ChevronDown`, `Zap` (werden nicht mehr gebraucht).
Entferne die Funktionen `NavGroup` und `NavSubGroup` am Ende der Datei (nicht mehr gebraucht).
Behalte: `Mountain`, `Home`, `Trophy`, `Flame`, `Users`, `Link`, `usePathname`, `cn`, `useState` (useState kann auch weg da NavGroup weg ist).

Der finale Import-Block:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mountain, Home, Trophy, Users, Flame } from "lucide-react";
import { cn } from "@/lib/utils";
```

- [ ] **Schritt 3: Build-Check**

```bash
cd web && npm run build 2>&1 | tail -20
```

Erwartet: ✓ Compiled successfully, keine TypeScript-Fehler

---

## Task 6: Layout-Anpassung für Split-View

Die neuen Seiten brauchen `h-full` damit der Split-View korrekt die volle Höhe nutzt.

**Files:**
- Modify: `web/src/app/layout.tsx`

- [ ] **Schritt 1: Layout lesen**

```bash
cat web/src/app/layout.tsx
```

- [ ] **Schritt 2: Main-Container auf `flex-1 overflow-hidden` setzen**

Der `<main>` Tag (oder der Content-Wrapper neben der Sidebar) muss `min-h-0 flex-1` haben damit `SplitCategoryPage` mit `h-full` und `overflow-y-auto` korrekt funktioniert. Typisch sieht der Wrapper so aus — passe ihn entsprechend an:

```tsx
// Vorher (typisch):
<main className="flex-1">

// Nachher:
<main className="flex min-h-0 flex-1 flex-col">
```

- [ ] **Schritt 3: Build-Check + Visuelle Verifikation**

```bash
cd web && npm run build 2>&1 | tail -20
```

Dann Server starten:
```bash
cd tools && python3 server.py &
cd web && npm run dev
```

Öffne http://localhost:3000/legenden — prüfe:
- [ ] Sidebar zeigt 4 Einträge: Home, Legenden, Aktuell, Teams
- [ ] "Legenden" ist aktiv markiert (gold)
- [ ] Pills erscheinen oben: All-Time, Guards, Forwards, Centers, MVP, All-NBA, DPOY, ROY, Finals MVP
- [ ] Klick auf Pill → Spielerliste aktualisiert sich (5 Spieler)
- [ ] Klick auf Spieler → Slot 1 im rechten Panel füllt sich
- [ ] Weiterer Klick → Slot 2 füllt sich
- [ ] Nach 5 Spielern → "Karte erstellen" Button erscheint
- [ ] Klick → Karte wird generiert, PNG erscheint inline
- [ ] Download-Button lädt PNG herunter
- [ ] "Neu starten" setzt alles zurück

Öffne http://localhost:3000/aktuell — prüfe:
- [ ] Pills: "Diese Saison", "Aktive Stars"
- [ ] Diese Saison zeigt 30 aktuelle Spieler
- [ ] Aktive Stars zeigt bis zu 30 aktive Spieler

Mobile-Check (Browser DevTools → Mobile Ansicht):
- [ ] Split-View verschwindet (kein rechtes Panel)
- [ ] Sticky Bottom Bar erscheint nach erstem Spieler-Klick

---

## Spec-Coverage-Check

| Spec-Anforderung | Task |
|---|---|
| Sidebar: 4 flache Links | Task 5 |
| `/legenden` Route | Task 3 |
| `/aktuell` Route | Task 4 |
| SplitCategoryPage Komponente | Task 2 |
| CardBuilderPanel Komponente | Task 1 |
| Pills: Legenden 9 Kategorien, je limit=5 | Task 3 |
| Pills: Aktuell 2 Kategorien, limit=30 | Task 4 |
| Rechtes Panel: Live Slots → Generate → PNG inline | Task 1 |
| Download + Copy to Clipboard | Task 1 |
| Neu starten | Task 1 |
| Mobile: SelectionBar bleibt | Task 2 |
| Pill-Wechsel setzt Slots zurück | Task 2 |
