"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Search, X } from "lucide-react";
import { searchPlayers, type Player } from "@/lib/api";

interface SearchDrawerProps {
  open: boolean;
  onClose: () => void;
  onSelect: (player: Player) => void;
  selectedIds: Set<number>;
}

export function SearchDrawer({
  open,
  onClose,
  onSelect,
  selectedIds,
}: SearchDrawerProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const doSearch = useCallback((q: string) => {
    setLoading(true);
    searchPlayers(q, 40)
      .then(setResults)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Initial load + debounced search
  useEffect(() => {
    if (!open) return;
    setQuery("");
    doSearch("");
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [open, doSearch]);

  useEffect(() => {
    if (!open) return;
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(query), 200);
    return () => clearTimeout(debounceRef.current);
  }, [query, open, doSearch]);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed inset-x-0 bottom-0 z-50 flex max-h-[85vh] flex-col rounded-t-2xl border-t border-border bg-surface animate-in slide-in-from-bottom">
        {/* Handle */}
        <div className="flex justify-center py-3">
          <div className="h-1 w-10 rounded-full bg-border" />
        </div>

        {/* Search input */}
        <div className="px-4 pb-3">
          <div className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3">
            <Search className="h-4 w-4 shrink-0 text-text-tertiary" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search players..."
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-text-tertiary"
            />
            {query && (
              <button onClick={() => setQuery("")}>
                <X className="h-4 w-4 text-text-tertiary hover:text-text" />
              </button>
            )}
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-4 pb-8">
          {results.map((player) => {
            const isSelected = selectedIds.has(player.id);
            return (
              <button
                key={player.id}
                disabled={isSelected}
                onClick={() => onSelect(player)}
                className={`flex w-full items-center gap-3 rounded-xl p-3 text-left transition-colors ${
                  isSelected
                    ? "opacity-30 cursor-not-allowed"
                    : "hover:bg-card-hover"
                }`}
              >
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold truncate">
                    {player.name}
                  </div>
                  <div className="text-xs text-text-secondary">
                    {player.position && `${player.position} · `}
                    {player.teams?.slice(0, 3).join(", ")}
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-3 text-xs text-text-secondary">
                  <span>{player.ppg} PPG</span>
                  <span>{player.rpg} RPG</span>
                  <span>{player.apg} APG</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </>
  );
}
