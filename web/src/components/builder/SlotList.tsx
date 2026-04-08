"use client";

import { useRef } from "react";
import { GripVertical, Plus, X } from "lucide-react";
import type { Player } from "@/lib/api";

interface SlotListProps {
  slots: (Player | null)[];
  onSlotClick: (index: number) => void;
  onRemove: (index: number) => void;
  onReorder: (from: number, to: number) => void;
}

export function SlotList({
  slots,
  onSlotClick,
  onRemove,
  onReorder,
}: SlotListProps) {
  const dragIdx = useRef<number | null>(null);

  return (
    <div className="flex flex-col gap-2">
      {slots.map((player, i) => (
        <div
          key={i}
          draggable={!!player}
          onDragStart={() => {
            dragIdx.current = i;
          }}
          onDragOver={(e) => {
            e.preventDefault();
          }}
          onDrop={() => {
            if (dragIdx.current !== null && dragIdx.current !== i) {
              onReorder(dragIdx.current, i);
            }
            dragIdx.current = null;
          }}
          className={`group flex items-center gap-3 rounded-xl border p-4 transition-all ${
            player
              ? "border-border-subtle bg-card cursor-grab active:cursor-grabbing"
              : "border-dashed border-border bg-transparent cursor-pointer hover:border-gold/40 hover:bg-card"
          }`}
          onClick={() => {
            if (!player) onSlotClick(i);
          }}
        >
          {/* Rank */}
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-surface text-sm font-bold text-gold">
            {i + 1}
          </div>

          {player ? (
            <>
              {/* Drag handle */}
              <GripVertical className="h-4 w-4 shrink-0 text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity" />
              {/* Player info */}
              <div className="min-w-0 flex-1">
                <div className="font-semibold truncate">{player.name}</div>
                <div className="text-xs text-text-secondary">
                  {player.position && `${player.position} · `}
                  {player.ppg} PPG · {player.rpg} RPG · {player.apg} APG
                </div>
              </div>
              {/* Remove */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(i);
                }}
                className="shrink-0 rounded-lg p-1.5 text-text-tertiary hover:text-text hover:bg-surface transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </>
          ) : (
            <div className="flex flex-1 items-center gap-2 text-sm text-text-tertiary">
              <Plus className="h-4 w-4" />
              <span>Tap to add player</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
