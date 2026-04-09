"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mountain, Home, Trophy, Flame, Users, Shuffle } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", icon: Home, label: "Home" },
  { href: "/legenden", icon: Trophy, label: "Legends" },
  { href: "/aktuell", icon: Flame, label: "Season" },
  { href: "/freestyle", icon: Shuffle, label: "Freestyle" },
  { href: "/categories/teams", icon: Users, label: "Teams" },
];

export function Header() {
  const pathname = usePathname();
  const isHome = pathname === "/";

  return (
    <header className={cn(
      "sticky top-0 z-50 hidden md:flex h-14 items-center px-6 transition-colors duration-300",
      isHome
        ? "bg-transparent border-b border-transparent"
        : "bg-bg/90 border-b border-border-subtle backdrop-blur-md"
    )}>
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 mr-10">
        <Mountain className="h-5 w-5 text-gold" />
        <span className="text-base font-black tracking-tight">RUSHMORE</span>
      </Link>

      {/* Nav items */}
      <nav className="flex items-center gap-1">
        {NAV_ITEMS.map((item) => {
          const active = item.href === "/"
            ? pathname === "/"
            : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
                active
                  ? "text-gold font-medium"
                  : isHome
                    ? "text-white/70 hover:text-white"
                    : "text-text-secondary hover:text-text"
              )}
            >
              <item.icon className="h-3.5 w-3.5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
