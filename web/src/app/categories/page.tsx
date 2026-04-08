"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Trophy,
  Star,
  Users,
  Timer,
  Crown,
  Award,
  Zap,
  TrendingUp,
} from "lucide-react";
import { fetchCategories, type CategoriesIndex } from "@/lib/api";

export default function CategoriesPage() {
  const [cats, setCats] = useState<CategoriesIndex | null>(null);

  useEffect(() => {
    fetchCategories().then(setCats).catch(console.error);
  }, []);

  if (!cats) return null;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-black tracking-tight mb-8">Categories</h1>

      {/* Live */}
      <Section title="Live">
        <CategoryLink
          href="/categories/current-season"
          icon={Zap}
          label="This Season"
          sub={cats.current_season.label}
          accent
        />
        <CategoryLink
          href="/categories/active"
          icon={TrendingUp}
          label="Active Players"
          sub={cats.active.label}
          accent
        />
      </Section>

      {/* Classic */}
      <Section title="All-Time">
        <CategoryLink
          href="/categories/all-time"
          icon={Trophy}
          label="All-Time Greatest"
          sub="Ranked by total career points"
        />
        <CategoryLink
          href="/categories/champions"
          icon={Crown}
          label="Champions"
          sub="Most rings all-time"
        />
        <CategoryLink
          href="/categories/mvps"
          icon={Award}
          label="MVP Race"
          sub="Most MVP awards"
        />
      </Section>

      {/* Positions */}
      <Section title="By Position">
        {Object.entries(cats.positions).map(([code, label]) => (
          <CategoryLink
            key={code}
            href={`/categories/positions/${code}`}
            icon={Users}
            label={label}
            sub={`Top ${label.toLowerCase()}`}
          />
        ))}
      </Section>

      {/* Eras */}
      <Section title="By Era">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {Object.entries(cats.eras).map(([decade, label]) => (
            <Link
              key={decade}
              href={`/categories/eras/${decade}`}
              className="rounded-lg border border-border-subtle bg-card px-4 py-3 text-center text-sm font-semibold hover:bg-card-hover hover:text-gold transition-all"
            >
              {label}
            </Link>
          ))}
        </div>
      </Section>

      {/* Teams */}
      <Section title="By Team">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {Object.entries(cats.teams).map(([code, name]) => (
            <Link
              key={code}
              href={`/categories/teams/${code}`}
              className="rounded-lg border border-border-subtle bg-card px-4 py-3 text-sm hover:bg-card-hover hover:text-gold transition-all"
            >
              <span className="font-bold">{code}</span>
              <span className="ml-2 text-text-secondary text-xs">{name}</span>
            </Link>
          ))}
        </div>
      </Section>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-8">
      <h2 className="text-xs font-bold uppercase tracking-widest text-text-tertiary mb-3">
        {title}
      </h2>
      <div className="flex flex-col gap-2">{children}</div>
    </div>
  );
}

function CategoryLink({
  href,
  icon: Icon,
  label,
  sub,
  accent,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  sub: string;
  accent?: boolean;
}) {
  return (
    <Link
      href={href}
      className={`group flex items-center gap-4 rounded-xl border p-4 transition-all hover:bg-card-hover ${
        accent ? "border-gold/20 bg-card" : "border-border-subtle bg-card"
      }`}
    >
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
          accent
            ? "bg-gold/10 text-gold"
            : "bg-surface text-text-secondary"
        }`}
      >
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <div className="text-sm font-semibold group-hover:text-gold transition-colors">
          {label}
        </div>
        <div className="text-xs text-text-tertiary">{sub}</div>
      </div>
    </Link>
  );
}
