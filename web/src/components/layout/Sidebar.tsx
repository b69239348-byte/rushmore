"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Mountain, Home, Trophy, Flame, Users, Shuffle } from "lucide-react";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();
  const isHome = pathname === "/";

  return (
    <aside className={cn(
      "hidden md:flex w-56 shrink-0 flex-col overflow-y-auto h-screen fixed top-0 left-0 z-50 transition-colors duration-300",
      isHome
        ? "bg-transparent border-r border-transparent"
        : "bg-surface border-r border-border-subtle"
    )}>
      <SidebarContent />
    </aside>
  );
}

export function SidebarContent() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col py-4 px-3 gap-1">
      <Link href="/" className="flex items-center gap-2 px-3 py-2 mb-3">
        <Mountain className="h-5 w-5 text-gold" />
        <span className="text-lg font-black tracking-tight">RUSHMORE</span>
      </Link>

      <NavItem href="/" icon={Home} label="Home" active={pathname === "/"} />
      <NavItem href="/legenden" icon={Trophy} label="Legends" active={pathname.startsWith("/legenden")} />
      <NavItem href="/aktuell" icon={Flame} label="Season" active={pathname.startsWith("/aktuell")} />
      <NavItem href="/freestyle" icon={Shuffle} label="Freestyle" active={pathname.startsWith("/freestyle")} />
      <NavItem href="/categories/teams" icon={Users} label="Teams" active={pathname.startsWith("/categories/teams")} />
    </nav>
  );
}

function NavItem({
  href,
  icon: Icon,
  label,
  active,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "flex items-center gap-2.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
        active
          ? "bg-card text-gold font-medium"
          : "text-text-secondary hover:text-text hover:bg-card-hover"
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      {label}
    </Link>
  );
}
