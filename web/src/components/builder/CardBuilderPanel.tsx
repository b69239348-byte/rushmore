"use client";

import { ChevronUp, ChevronDown, X, Sparkles, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Player } from "@/lib/api";

interface CardBuilderPanelProps {
  slots: (Player | null)[];
  onRemove: (index: number) => void;
  onReorder: (from: number, to: number) => void;
  onBuildCard: (title: string) => void;
  onReset: () => void;
  generating?: boolean;
}

export function CardBuilderPanel({
  slots,
  onRemove,
  onReorder,
  onBuildCard,
  onReset,
  generating = false,
}: CardBuilderPanelProps) {
  const filledCount = slots.filter(Boolean).length;

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-text-tertiary">
        Starting Five
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
              <span className="text-xs text-text-tertiary">Empty slot</span>
            )}
          </div>
        ))}
      </div>

{filledCount > 0 && (
        <div className="flex flex-col gap-2">
          <button
            onClick={() => onBuildCard("")}
            disabled={generating}
            className="flex items-center justify-center gap-2 rounded-xl bg-gold py-3 text-sm font-bold text-bg transition-colors hover:bg-gold-bright disabled:opacity-50"
          >
            {generating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {generating ? "Cooking..." : "Drop the Card"}
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
        <p className="text-center text-xs text-text-tertiary">
          {5 - filledCount} {5 - filledCount === 1 ? "spot" : "spots"} left
        </p>
      )}
    </div>
  );
}
