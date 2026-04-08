"use client";

import Image from "next/image";
import Link from "next/link";
import {
  Trophy,
  Zap,
  Crown,
  Award,
  Users,
  Timer,
  ChevronRight,
  MessageSquare,
  BarChart2,
  Share2,
} from "lucide-react";

const FEATURED_CATEGORIES = [
  {
    href: "/categories/all-time",
    icon: Trophy,
    title: "All-Time Greatest",
    desc: "The greatest players of all time",
    accent: false,
    live: false,
  },
  {
    href: "/categories/champions",
    icon: Crown,
    title: "Champions",
    desc: "Ranked by championship rings",
    accent: false,
    live: false,
  },
  {
    href: "/categories/mvps",
    icon: Award,
    title: "MVP Race",
    desc: "Most MVP awards all-time",
    accent: false,
    live: false,
  },
  {
    href: "/aktuell",
    icon: Zap,
    title: "Season MVP",
    desc: "Current season favorites",
    accent: true,
    live: true,
  },
  {
    href: "/categories/positions/G",
    icon: Users,
    title: "By Position",
    desc: "Guards, Forwards, Centers",
    accent: false,
    live: false,
  },
  {
    href: "/categories/eras/2020",
    icon: Timer,
    title: "By Era",
    desc: "The best of every decade",
    accent: false,
    live: false,
  },
];

const WHY_POINTS = [
  {
    icon: MessageSquare,
    title: "Debate",
    desc: "Every NBA fan has a take. Now yours has data behind it.",
  },
  {
    icon: BarChart2,
    title: "Data",
    desc: "Stats, rings, MVPs — ranked across every era and position.",
  },
  {
    icon: Share2,
    title: "Share",
    desc: "Generate your Top 5 card and share it on your socials. Put your opinion on record.",
  },
];

export default function Home() {
  return (
    <div className="flex flex-col">

      {/* ── Hero ── */}
      <section className="relative flex min-h-screen items-start overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0">
          <Image
            src="/hero-bg.png"
            alt="Basketball court at night with mountains"
            fill
            priority
            className="object-cover object-center"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-bg/40 via-bg/10 to-bg/50" />
          <div className="absolute inset-0 bg-gradient-to-r from-bg/30 via-transparent to-bg/20" />
        </div>

        {/* Content */}
        <div className="relative z-10 w-full px-8 pb-16 pt-12">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-gold/30 bg-gold/5 px-4 py-1.5 text-xs font-medium text-gold mb-6">
              <Zap className="h-3 w-3" />
              2025–26 Season Live
            </div>

            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.05]">
              Build Your NBA
              <br />
              <span className="text-gold">Mount Rushmore</span>
            </h1>

            <p className="mt-5 text-base sm:text-lg text-text-secondary leading-relaxed max-w-xl">
              Every NBA fan has an opinion.
              <br />
              Now put it on record — and share it on your socials.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/categories/all-time"
                className="flex items-center gap-2 rounded-xl bg-gold px-7 py-3.5 text-sm font-bold text-bg hover:bg-gold-bright transition-all"
              >
                <Trophy className="h-4 w-4" />
                Explore Rankings
              </Link>
              <Link
                href="/build"
                className="flex items-center gap-2 rounded-xl border border-border bg-surface/50 backdrop-blur-sm px-7 py-3.5 text-sm font-semibold text-text-secondary hover:text-text hover:border-text-tertiary transition-all"
              >
                Build Your Top 5
              </Link>
            </div>
          </div>

        </div>
      </section>

      {/* ── Why Section ── */}
      <section className="mx-auto w-full max-w-4xl px-6 pt-12 pb-14">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {WHY_POINTS.map((point) => (
            <div
              key={point.title}
              className="flex flex-col gap-3 rounded-xl border border-border-subtle bg-card p-6"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gold/10 text-gold">
                <point.icon className="h-5 w-5" />
              </div>
              <div>
                <div className="font-bold text-base">{point.title}</div>
                <div className="mt-1 text-sm text-text-secondary leading-relaxed">
                  {point.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Categories ── */}
      <section className="mx-auto w-full max-w-4xl px-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold tracking-tight">Categories</h2>
          <Link
            href="/categories"
            className="flex items-center gap-1 text-xs font-medium text-text-tertiary hover:text-gold transition-colors"
          >
            View all
            <ChevronRight className="h-3 w-3" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {FEATURED_CATEGORIES.map((cat) => (
            <Link
              key={cat.href}
              href={cat.href}
              className={`group relative flex items-center gap-4 rounded-xl border p-4 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg overflow-hidden ${
                cat.accent
                  ? "border-gold/30 bg-gold/[0.04] hover:border-gold/50 hover:bg-gold/[0.07]"
                  : "border-border-subtle bg-card hover:border-border hover:bg-card-hover"
              }`}
            >
              {/* subtle glow for accented tile */}
              {cat.accent && (
                <div className="pointer-events-none absolute inset-0 rounded-xl bg-gradient-to-br from-gold/10 via-transparent to-transparent" />
              )}

              <div
                className={`relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-all duration-200 ${
                  cat.accent
                    ? "bg-gold/15 text-gold shadow-sm"
                    : "bg-surface text-text-secondary group-hover:bg-gold/10 group-hover:text-gold"
                }`}
              >
                <cat.icon className="h-5 w-5" />
              </div>

              <div className="relative min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-semibold transition-colors truncate ${
                    cat.accent ? "text-gold" : "group-hover:text-gold"
                  }`}>
                    {cat.title}
                  </span>
                  {cat.live && (
                    <span className="shrink-0 inline-flex items-center gap-1 rounded-full bg-gold/10 px-1.5 py-0.5 text-[10px] font-semibold text-gold">
                      <span className="h-1.5 w-1.5 rounded-full bg-gold animate-pulse" />
                      LIVE
                    </span>
                  )}
                </div>
                <div className="text-xs text-text-tertiary truncate mt-0.5">
                  {cat.desc}
                </div>
              </div>

              <ChevronRight className={`h-4 w-4 shrink-0 transition-all duration-200 ${
                cat.accent
                  ? "text-gold/50 group-hover:text-gold group-hover:translate-x-0.5"
                  : "text-text-tertiary/0 group-hover:text-text-tertiary group-hover:translate-x-0.5"
              }`} />
            </Link>
          ))}
        </div>
      </section>

      {/* ── Showcase ── */}
      <section className="mx-auto w-full max-w-4xl px-6 pb-20">
        <div className="mb-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
            Build Your <span className="text-gold">NBA</span>
          </h2>
          <p className="mt-2 text-sm text-text-tertiary">
            Pick your players. Set your order. Drop the card.
          </p>
        </div>

        <div className="flex gap-4 justify-center overflow-x-auto no-scrollbar pb-2">
          {[
            { src: "/showcase-1.png", label: "All-Time Greats" },
            { src: "/showcase-2.png", label: "Current Stars" },
            { src: "/showcase-3.png", label: "Best Guards" },
          ].map((card) => (
            <div key={card.src} className="shrink-0 hover:scale-105 transition-transform duration-300 drop-shadow-xl">
              <Image
                src={card.src}
                alt={card.label}
                width={180}
                height={320}
                className="rounded-xl ring-1 ring-white/10"
              />
            </div>
          ))}
        </div>

        <div className="mt-8 flex justify-center">
          <Link
            href="/build"
            className="flex items-center gap-2 rounded-xl bg-gold px-8 py-3.5 text-sm font-bold text-bg hover:bg-gold-bright transition-all"
          >
            <Trophy className="h-4 w-4" />
            Build Your Card
          </Link>
        </div>
      </section>

    </div>
  );
}
