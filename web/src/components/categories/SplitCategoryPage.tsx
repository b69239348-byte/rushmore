"use client";

import { useEffect, useState, useMemo } from "react";
import { Loader2, Search } from "lucide-react";
import { fetchCategory, type CategoryResult } from "@/lib/api";
import { PlayerList } from "./PlayerList";
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
  const [searchQuery, setSearchQuery] = useState("");

  const active = categories[activeIndex];

  const filteredPlayers = useMemo(() => {
    if (!data?.players) return [];
    if (!searchQuery.trim()) return data.players;
    const q = searchQuery.toLowerCase();
    return data.players.filter((p) => p.name.toLowerCase().includes(q));
  }, [data, searchQuery]);

  useEffect(() => {
    setLoading(true);
    setSearchQuery("");
    fetchCategory(active.path, active.params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeIndex]);

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

      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
          </div>
        ) : data ? (
          <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
            <PlayerList players={filteredPlayers} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
