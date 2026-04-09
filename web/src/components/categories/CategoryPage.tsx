"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { fetchCategory, generateCard, type CategoryResult, type Player } from "@/lib/api";
import { CategoryHeader } from "./CategoryHeader";
import { PlayerList } from "./PlayerList";
import { SelectionBar } from "./SelectionBar";
import { CardBuilderPanel } from "@/components/builder/CardBuilderPanel";
import { CardPreview } from "@/components/builder/CardPreview";
import { Loader2 } from "lucide-react";

interface CategoryPageProps {
  path: string;
  params?: Record<string, string | number>;
  cardSubtitle?: string;
}

const BACKGROUNDS_POOL = [
  "night_court_outdoor","rooftop_city","underground_court","desert_dusk",
  "golden_arena","indoor_arena","morning_fog","sunset_court",
  "trophy_spotlight","trophy_celebration",
];
const randomBackground = () => BACKGROUNDS_POOL[Math.floor(Math.random() * BACKGROUNDS_POOL.length)];

export function CategoryPage({ path, params, cardSubtitle }: CategoryPageProps) {
  const [data, setData] = useState<CategoryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [slots, setSlots] = useState<(Player | null)[]>([null, null, null, null, null]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);

  const selectedIds = useMemo(
    () => new Set(slots.filter(Boolean).map((p) => (p as Player).id)),
    [slots]
  );

  useEffect(() => {
    setLoading(true);
    setSlots([null, null, null, null, null]);
    fetchCategory(path, params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [path, params]);

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
      const title = data?.title ? `MY ${data.title.toUpperCase()}` : "MY TOP 5";
      const blob = await generateCard(playerIds, title, undefined, randomBackground());
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (err) {
      console.error("Card generation failed:", err);
    } finally {
      setGenerating(false);
    }
  }, [slots, data, previewUrl]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="relative border-b border-border-subtle px-4 pt-4 pb-3 md:px-6 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -top-8 bg-[radial-gradient(ellipse_at_50%_0%,rgba(201,168,76,0.07)_0%,transparent_70%)]" />
        <CategoryHeader title={data.title} subtitle={data.subtitle} />
      </div>

      {/* Body */}
      <div className="flex min-h-0 flex-1">
        <div className="flex-1 overflow-y-auto pb-32 md:pb-8">
          <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
            <PlayerList
              players={data.players}
              selectedIds={selectedIds}
              onPlayerClick={handlePlayerClick}
            />
          </div>
        </div>

        {/* Desktop aside */}
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
      </div>

      {/* Mobile bottom bar */}
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
