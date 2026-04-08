"use client";

import Link from "next/link";
import { Users } from "lucide-react";

const POSITIONS = [
  { code: "G", label: "Guards", description: "Point guards and shooting guards" },
  { code: "F", label: "Forwards", description: "Small forwards and power forwards" },
  { code: "C", label: "Centers", description: "The big men" },
];

export default function PositionsPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-black tracking-tight mb-6">By Position</h1>
      <div className="flex flex-col gap-3">
        {POSITIONS.map((pos) => (
          <Link
            key={pos.code}
            href={`/categories/positions/${pos.code}`}
            className="group flex items-center gap-4 rounded-xl border border-border-subtle bg-card p-5 transition-all hover:bg-card-hover"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-surface text-lg font-black text-gold">
              {pos.code}
            </div>
            <div>
              <div className="font-semibold group-hover:text-gold transition-colors">
                {pos.label}
              </div>
              <div className="text-xs text-text-tertiary">
                {pos.description}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
