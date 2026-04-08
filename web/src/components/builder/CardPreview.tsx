"use client";

import { useEffect, useState } from "react";
import { Download, Copy, Check, X, Share2 } from "lucide-react";

interface CardPreviewProps {
  url: string;
  onClose: () => void;
}

// X (Twitter) logo as inline SVG
function XLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.261 5.632L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z" />
    </svg>
  );
}

export function CardPreview({ url, onClose }: CardPreviewProps) {
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);
  const canNativeShare = typeof navigator !== "undefined" && !!navigator.share;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const handleSave = () => {
    const a = document.createElement("a");
    a.href = url;
    a.download = "rushmore.png";
    a.click();
  };

  const handleCopy = async () => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not supported — fall back to save
      handleSave();
    }
  };

  const handleNativeShare = async () => {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      const file = new File([blob], "rushmore.png", { type: "image/png" });
      await navigator.share({ files: [file], title: "My NBA Rushmore" });
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    } catch {
      // User cancelled or not supported — no-op
    }
  };

  const handleXShare = async () => {
    // Download card first, then open X intent
    handleSave();
    const text = encodeURIComponent("My NBA Mount Rushmore 🏀 — built on rushmore.app");
    window.open(`https://twitter.com/intent/tweet?text=${text}`, "_blank");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="relative max-h-[90vh] max-w-sm w-full flex flex-col gap-3">
        <button
          onClick={onClose}
          className="absolute -top-10 right-0 rounded-lg p-1.5 text-text-secondary hover:text-text transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <img
          src={url}
          alt="Your Top 5 card"
          className="w-full rounded-xl"
        />

        {/* Primary actions */}
        <div className="flex gap-2">
          <button
            onClick={handleSave}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gold py-3 text-sm font-bold text-bg hover:bg-gold-bright transition-colors"
          >
            <Download className="h-4 w-4" />
            Save
          </button>
          {canNativeShare ? (
            <button
              onClick={handleNativeShare}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-3 text-sm font-semibold text-text-secondary hover:bg-card-hover hover:text-text transition-colors"
            >
              {shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}
              {shared ? "Shared!" : "Share"}
            </button>
          ) : (
            <button
              onClick={handleCopy}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-3 text-sm font-semibold text-text-secondary hover:bg-card-hover hover:text-text transition-colors"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          )}
        </div>

        {/* Secondary: X share + copy (desktop) */}
        <div className="flex gap-2">
          <button
            onClick={handleXShare}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-2.5 text-sm font-semibold text-text-secondary hover:bg-card-hover hover:text-text transition-colors"
          >
            <XLogo className="h-4 w-4" />
            Post on X
          </button>
          {canNativeShare && (
            <button
              onClick={handleCopy}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border-subtle py-2.5 text-sm font-semibold text-text-secondary hover:bg-card-hover hover:text-text transition-colors"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copied!" : "Copy"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
