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
