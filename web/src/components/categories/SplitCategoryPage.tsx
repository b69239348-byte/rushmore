"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { Loader2, Search } from "lucide-react";
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
  showBuilder?: boolean;
}

const BACKGROUNDS_POOL = [
  "night_court_outdoor","rooftop_city","underground_court","desert_dusk",
  "golden_arena","indoor_arena","morning_fog","sunset_court",
  "trophy_spotlight","trophy_celebration",
];
const randomBackground = () => BACKGROUNDS_POOL[Math.floor(Math.random() * BACKGROUNDS_POOL.length)];

export function SplitCategoryPage({ title, categories, showBuilder = false }: SplitCategoryPageProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [data, setData] = useState<CategoryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [slots, setSlots] = useState<(Player | null)[]>([null, null, null, null, null]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [lastPlayerIds, setLastPlayerIds] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  const active = categories[activeIndex];

  const selectedIds = useMemo(
    () => new Set(slots.filter((p): p is Player => p !== null).map((p) => p.id)),
    [slots]
  );

  const filteredPlayers = useMemo(() => {
    if (!data?.players) return [];
    if (!searchQuery.trim()) return data.players;
    const q = searchQuery.toLowerCase();
    return data.players.filter((p) => p.name.toLowerCase().includes(q));
  }, [data, searchQuery]);

  useEffect(() => {
    setLoading(true);
    setSlots([null, null, null, null, null]);
    setSearchQuery("");
    fetchCategory(active.path, active.params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeIndex]);

  const handlePlayerClick = useCallback((player: Player) => {
    if (!showBuilder) return;
    setSlots((prev) => {
      if (prev.some((p) => p?.id === player.id)) return prev;
      const nextEmpty = prev.indexOf(null);
      if (nextEmpty === -1) return prev;
      const next = [...prev];
      next[nextEmpty] = player;
      return next;
    });
  }, [showBuilder]);

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
    setLastPlayerIds(playerIds);
    setGenerating(true);
    try {
      const blob = await generateCard(
        playerIds,
        `MY ${active.label.toUpperCase()}`,
        data?.subtitle || active.cardSubtitle,
        randomBackground()
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
      <div className="relative border-b border-border-subtle px-4 pt-4 pb-3 md:px-6 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -top-8 bg-[radial-gradient(ellipse_at_50%_0%,rgba(201,168,76,0.07)_0%,transparent_70%)]" />
        <h1 className="relative text-xl font-black tracking-tight mb-3">{title}</h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-tertiary pointer-events-none" />
          <input
            type="text"
            placeholder="Search ballers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-border-subtle bg-surface pl-9 pr-4 py-2 text-sm text-text placeholder:text-text-tertiary focus:border-gold/40 focus:outline-none transition-colors"
          />
        </div>
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
        <div className={cn("flex-1 overflow-y-auto", showBuilder ? "pb-32 md:pb-8" : "pb-4")}>
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
            </div>
          ) : data ? (
            <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
              <PlayerList
                players={filteredPlayers}
                selectedIds={showBuilder ? selectedIds : undefined}
                onPlayerClick={showBuilder ? handlePlayerClick : undefined}
              />
            </div>
          ) : null}
        </div>

        {showBuilder && (
          <aside className="hidden w-80 shrink-0 border-l border-border-subtle p-4 md:block sticky top-0 self-start max-h-screen overflow-y-auto">
            <CardBuilderPanel
              slots={slots}
              onRemove={handleRemove}
              onReorder={handleReorder}
              onReset={handleReset}
              onBuildCard={handleBuildCard}
              generating={generating}
            />
          </aside>
        )}
      </div>

      {showBuilder && (
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
      )}

      {previewUrl && (
        <CardPreview
          url={previewUrl}
          onClose={() => setPreviewUrl(null)}
          regenerate={async (format) => {
            return generateCard(
              lastPlayerIds,
              `MY ${active.label.toUpperCase()}`,
              data?.subtitle || active.cardSubtitle,
              randomBackground(),
              format
            );
          }}
        />
      )}
    </div>
  );
}
