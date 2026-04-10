"use client";

import { useEffect, useRef, useState } from "react";
import { Download, Copy, Check, X, Share2 } from "lucide-react";

type CardFormat = "story" | "feed";

interface CardPreviewProps {
  url: string;
  onClose: () => void;
  regenerate?: (format: CardFormat) => Promise<Blob>;
}

/** Converts any image to a 1080×1080 square (letterboxed) for Instagram Post. */
async function toSquareBlob(srcUrl: string): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const img = new window.Image();
    img.onload = () => {
      const SIZE = 1080;
      const canvas = document.createElement("canvas");
      canvas.width = SIZE;
      canvas.height = SIZE;
      const ctx = canvas.getContext("2d")!;
      // Dark background matching card style
      ctx.fillStyle = "#05080e";
      ctx.fillRect(0, 0, SIZE, SIZE);
      // Scale image to fit fully inside the square (letterbox)
      const scale = Math.min(SIZE / img.naturalWidth, SIZE / img.naturalHeight);
      const w = Math.round(img.naturalWidth * scale);
      const h = Math.round(img.naturalHeight * scale);
      ctx.drawImage(img, Math.round((SIZE - w) / 2), Math.round((SIZE - h) / 2), w, h);
      canvas.toBlob(
        (b) => (b ? resolve(b) : reject(new Error("toBlob failed"))),
        "image/png"
      );
    };
    img.onerror = reject;
    img.src = srcUrl;
  });
}

function XLogo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.261 5.632L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z" />
    </svg>
  );
}

export function CardPreview({ url, onClose, regenerate }: CardPreviewProps) {
  const [currentUrl, setCurrentUrl] = useState(url);
  const [format, setFormat] = useState<CardFormat>("feed");
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);
  const internalUrlRef = useRef<string | null>(null);
  const onCloseRef = useRef(onClose);
  useEffect(() => { onCloseRef.current = onClose; });
  const canNativeShare = typeof navigator !== "undefined" && !!navigator.share;
  const canCopyImage =
    typeof navigator !== "undefined" &&
    !!navigator.clipboard?.write &&
    typeof ClipboardItem !== "undefined";

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCloseRef.current();
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, []);

  useEffect(() => {
    return () => {
      if (internalUrlRef.current) URL.revokeObjectURL(internalUrlRef.current);
    };
  }, []);

  const handleFormatChange = async (newFormat: CardFormat) => {
    if (newFormat === format || !regenerate || regenerating) return;
    setRegenerating(true);
    try {
      const blob = await regenerate(newFormat);
      const newUrl = URL.createObjectURL(blob);
      if (internalUrlRef.current) URL.revokeObjectURL(internalUrlRef.current);
      internalUrlRef.current = newUrl;
      setCurrentUrl(newUrl);
      setFormat(newFormat);
    } finally {
      setRegenerating(false);
    }
  };

  const getShareBlob = async (): Promise<Blob> => {
    if (format === "feed") return toSquareBlob(currentUrl);
    const res = await fetch(currentUrl);
    return res.blob();
  };

  const handleSave = async () => {
    const blob = await getShareBlob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = `rushmore-${format}.png`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
  };

  const handleCopy = async () => {
    try {
      const blob = await getShareBlob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      handleSave();
    }
  };

  const handleNativeShare = async () => {
    try {
      const blob = await getShareBlob();
      const file = new File([blob], `rushmore-${format}.png`, { type: "image/png" });
      await navigator.share({ files: [file], title: "My NBA Rushmore" });
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    } catch {
      // cancelled or not supported
    }
  };

  const handleXShare = () => {
    handleSave();
    const text = encodeURIComponent("My NBA Mount Rushmore 🏀 — built on rushmore.cards");
    window.open(`https://x.com/intent/tweet?text=${text}`, "_blank");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-black/90 backdrop-blur-sm"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 shrink-0">
        <span className="text-sm font-semibold text-white/80">Your Card</span>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-white/60 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Image */}
      <div className="flex-1 min-h-0 flex items-center justify-center px-4 py-2 overflow-hidden">
        {regenerating ? (
          <div className="flex flex-col items-center gap-3 text-white/60">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-white/80" />
            <span className="text-sm">Generating…</span>
          </div>
        ) : (
          <img
            src={currentUrl}
            alt="Your Top 5 card"
            className="max-h-full max-w-full rounded-xl object-contain shadow-2xl"
          />
        )}
      </div>

      {/* Controls */}
      <div className="shrink-0 px-4 pt-3 pb-5 flex flex-col gap-3">

        {/* Format toggle — only shown if regenerate is available */}
        {regenerate && (
          <div className="flex items-center justify-center">
            <div className="flex rounded-lg border border-white/15 overflow-hidden text-xs font-semibold">
              <button
                onClick={() => handleFormatChange("story")}
                className={`px-4 py-1.5 transition-colors ${
                  format === "story"
                    ? "bg-white/15 text-white"
                    : "text-white/40 hover:text-white/70"
                }`}
              >
                Story
              </button>
              <button
                onClick={() => handleFormatChange("feed")}
                className={`px-4 py-1.5 transition-colors ${
                  format === "feed"
                    ? "bg-white/15 text-white"
                    : "text-white/40 hover:text-white/70"
                }`}
              >
                Feed Post
              </button>
            </div>
          </div>
        )}

        {/* Mobile: native share as hero action */}
        {canNativeShare ? (
          <div className="flex flex-col gap-2">
            <button
              onClick={handleNativeShare}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-3.5 text-sm font-bold text-black hover:bg-white/90 transition-colors"
            >
              {shared ? <Check className="h-4 w-4" /> : <Share2 className="h-4 w-4" />}
              {shared ? "Shared!" : "Share"}
            </button>
            <button
              onClick={handleSave}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/20 py-3 text-sm font-semibold text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            >
              <Download className="h-4 w-4" />
              Save to Device
            </button>
            <p className="text-center text-xs text-white/30 pt-1">
              Tag <span className="text-white/50">@rushmore.cards</span> on Instagram &amp; TikTok
            </p>
          </div>
        ) : (
          /* Desktop: download + X */
          <div className="flex flex-col gap-2">
            <button
              onClick={handleSave}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-3.5 text-sm font-bold text-black hover:bg-white/90 transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              onClick={handleXShare}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/20 py-3 text-sm font-semibold text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            >
              <XLogo className="h-4 w-4" />
              Post on X
            </button>
            <p className="text-center text-xs text-white/30">
              Image saves automatically — attach it to your post in X
            </p>
            <p className="text-center text-xs text-white/30">
              Also on Instagram &amp; TikTok? Tag <span className="text-white/50">@rushmore.cards</span>
            </p>
            {canCopyImage && (
              <button
                onClick={handleCopy}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 py-2.5 text-xs text-white/40 hover:text-white/70 transition-colors"
              >
                {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? "Copied!" : "Copy to clipboard"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
