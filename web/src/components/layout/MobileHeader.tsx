"use client";

import { useState } from "react";
import { Menu, X, Mountain } from "lucide-react";
import { SidebarContent } from "./Sidebar";

export function MobileHeader() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Top bar — mobile only */}
      <header className="shrink-0 z-50 flex h-14 items-center justify-between border-b border-border-subtle bg-bg/90 backdrop-blur-md px-4 md:hidden">
        <button
          onClick={() => setOpen(true)}
          className="rounded-lg p-1.5 text-text-secondary hover:text-text transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="flex items-center gap-2">
          <Mountain className="h-4 w-4 text-gold" />
          <span className="text-sm font-bold tracking-tight">RUSHMORE</span>
        </div>
        <div className="w-8" /> {/* Spacer for centering */}
      </header>

      {/* Slide-out overlay */}
      {open && (
        <>
          <div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm md:hidden"
            onClick={() => setOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 z-50 w-64 bg-surface border-r border-border-subtle overflow-y-auto md:hidden" onClick={() => setOpen(false)}>
            <div className="flex items-center justify-end p-3">
              <button
                onClick={() => setOpen(false)}
                className="rounded-lg p-1.5 text-text-secondary hover:text-text"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <SidebarContent />
          </div>
        </>
      )}
    </>
  );
}
