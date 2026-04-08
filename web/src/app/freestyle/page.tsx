"use client";

import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Search, X, Pencil } from "lucide-react";
import { searchPlayers, generateCard, type Player } from "@/lib/api";
import { PlayerList } from "@/components/categories/PlayerList";
import { CardBuilderPanel } from "@/components/builder/CardBuilderPanel";
import { CardPreview } from "@/components/builder/CardPreview";
import { SelectionBar } from "@/components/categories/SelectionBar";

export default function FreestylePage() {
  const [slots, setSlots] = useState<(Player | null)[]>([null, null, null, null, null]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [query, setQuery] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [cardTitle, setCardTitle] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const BACKGROUNDS_POOL = [
    "night_court_outdoor","rooftop_city","underground_court","desert_dusk",
    "golden_arena","indoor_arena","morning_fog","sunset_court",
    "trophy_spotlight","trophy_celebration",
  ];
  const randomBackground = () => BACKGROUNDS_POOL[Math.floor(Math.random() * BACKGROUNDS_POOL.length)];

  const TITLE_SUGGESTIONS = [
    "Most Feared", "Ball Hogs", "Best Trash Talkers", "Top 5 Finishers",
    "Built Different", "Untouchable", "Most Disrespected", "The Enforcers",
    "Coldest of All Time", "Ones That Got Away", "Most Controversial",
    "Best Kept Secrets", "The Architects", "Legends of the Clutch",
    "No Ring, No Problem", "The GOAT Debate", "Criminally Underrated",
  ];

  const selectedIds = useMemo(
    () => new Set(slots.filter((p): p is Player => p !== null).map((p) => p.id)),
    [slots]
  );

  useEffect(() => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      searchPlayers(query, 300)
        .then(setPlayers)
        .catch(console.error)
        .finally(() => setLoading(false));
    }, query ? 200 : 0);
    return () => clearTimeout(debounceRef.current);
  }, [query]);

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
    setCardTitle("");
  }, []);

  const handleBuildCard = useCallback(async () => {
    const playerIds = slots.filter(Boolean).map((p) => (p as Player).id);
    if (playerIds.length === 0) return;
    setGenerating(true);
    try {
      const title = cardTitle.trim() || "MY TOP 5";
      const blob = await generateCard(playerIds, title.toUpperCase(), "FREESTYLE", randomBackground());
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  }, [slots, cardTitle, previewUrl]);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="relative border-b border-border-subtle px-4 pt-4 pb-3 md:px-6 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -top-8 bg-[radial-gradient(ellipse_at_50%_0%,rgba(201,168,76,0.07)_0%,transparent_70%)]" />
        <h1 className="relative text-xl font-black tracking-tight mb-3">Freestyle</h1>
        <p className="text-sm text-text-secondary mb-3">Your list, your rules. Name it and run it.</p>

        {/* Custom title input */}
        <div className="relative mb-2">
          <Pencil className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-tertiary pointer-events-none" />
          <input
            type="text"
            placeholder="Name your list — e.g. Top 5 Enforcers"
            value={cardTitle}
            onChange={(e) => setCardTitle(e.target.value)}
            maxLength={40}
            className="w-full rounded-lg border border-border-subtle bg-surface pl-9 pr-4 py-2 text-sm text-text placeholder:text-text-tertiary focus:border-gold/40 focus:outline-none transition-colors"
          />
        </div>

        {/* Title suggestions */}
        <div className="flex gap-1.5 overflow-x-auto pb-2 mb-1 scrollbar-hide">
          {TITLE_SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => setCardTitle(s)}
              className="shrink-0 rounded-full border border-border-subtle bg-surface px-3 py-1 text-xs text-text-secondary hover:border-gold/30 hover:text-text transition-colors"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Player search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-tertiary pointer-events-none" />
          <input
            type="text"
            placeholder="Search ballers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full rounded-lg border border-border-subtle bg-surface pl-9 pr-9 py-2 text-sm text-text placeholder:text-text-tertiary focus:border-gold/40 focus:outline-none transition-colors"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex min-h-0 flex-1">
        <div className="flex-1 overflow-y-auto pb-32 md:pb-8">
          <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
            {loading ? (
              <div className="flex justify-center py-20 text-text-tertiary text-sm">Loading...</div>
            ) : players.length === 0 ? (
              <div className="flex justify-center py-20 text-text-tertiary text-sm">No ballers found</div>
            ) : (
              <PlayerList
                players={players}
                showRank={false}
                selectedIds={selectedIds}
                onPlayerClick={handlePlayerClick}
              />
            )}
          </div>
        </div>

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
