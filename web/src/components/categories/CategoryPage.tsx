"use client";

import { useEffect, useState, useCallback } from "react";
import { fetchCategory, type CategoryResult, type Player } from "@/lib/api";
import { CategoryHeader } from "./CategoryHeader";
import { PlayerList } from "./PlayerList";
import { SelectionBar } from "./SelectionBar";
import { Loader2 } from "lucide-react";

interface CategoryPageProps {
  path: string;
  params?: Record<string, string | number>;
}

export function CategoryPage({ path, params }: CategoryPageProps) {
  const [data, setData] = useState<CategoryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [slots, setSlots] = useState<(Player | null)[]>([null, null, null, null, null]);

  const selectedIds = new Set(
    slots.filter(Boolean).map((p) => (p as Player).id)
  );
  const filledCount = slots.filter(Boolean).length;

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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 pb-28">
      <CategoryHeader title={data.title} subtitle={data.subtitle} />
      <PlayerList
        players={data.players}
        selectedIds={selectedIds}
        onPlayerClick={handlePlayerClick}
      />
      <SelectionBar
        slots={slots}
        onRemove={handleRemove}
        onReorder={handleReorder}
        onBuildCard={() => {}}
      />
    </div>
  );
}
