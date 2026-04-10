"use client";

import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { generateCard, type Player } from "@/lib/api";

interface ExportButtonProps {
  slots: (Player | null)[];
  disabled: boolean;
  onPreview: (url: string) => void;
}

export function ExportButton({ slots, disabled, onPreview }: ExportButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    const playerIds = slots.filter(Boolean).map((p) => (p as Player).id);
    if (playerIds.length === 0) return;
    setLoading(true);
    try {
      const blob = await generateCard(playerIds, "MY TOP 5", "ALL-TIME GREATS", undefined, "feed");
      onPreview(URL.createObjectURL(blob));
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled || loading}
      className="flex w-full items-center justify-center gap-2 rounded-xl bg-gold py-3.5 text-sm font-bold text-bg transition-all hover:bg-gold-bright disabled:opacity-25 disabled:cursor-not-allowed"
    >
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Sparkles className="h-4 w-4" />
      )}
      {loading ? "Cooking…" : "Build Your Card"}
    </button>
  );
}
