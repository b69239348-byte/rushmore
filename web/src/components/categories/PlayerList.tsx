"use client";

import { useState } from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Player } from "@/lib/api";
import { getTeamLogoUrl, getPlayerTeam } from "@/lib/teams";

function StatBadge({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center gap-0.5 rounded-lg bg-surface px-2.5 py-1.5 min-w-[44px]">
      <div className="text-sm font-bold text-text" style={{ fontFamily: "var(--font-numeric)", fontFeatureSettings: '"tnum" on, "lnum" on', letterSpacing: "0.03em" }}>{value}</div>
      <div className="text-[9px] uppercase text-text-tertiary tracking-wider font-semibold">
        {label}
      </div>
    </div>
  );
}

function AwardBadges({ awards }: { awards?: Player["awards"] }) {
  if (!awards) return null;
  const badges: string[] = [];
  if (awards.championships)
    badges.push(`${awards.championships}x Champ`);
  if (awards.mvps) badges.push(`${awards.mvps}x MVP`);
  if (awards.finals_mvps)
    badges.push(`${awards.finals_mvps}x FMVP`);
  if (badges.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1.5 mt-1">
      {badges.map((b) => (
        <span
          key={b}
          className="rounded-md bg-gold/10 px-1.5 py-0.5 text-[10px] font-semibold text-gold"
        >
          {b}
        </span>
      ))}
    </div>
  );
}

function TeamLogo({ player }: { player: Player }) {
  const team = player.main_team || getPlayerTeam(player);
  const logoUrl = getTeamLogoUrl(team);
  if (!logoUrl) return <div className="h-10 w-10 shrink-0" />;
  return (
    <img
      src={logoUrl}
      alt=""
      aria-hidden
      className="h-10 w-10 shrink-0 object-contain opacity-40"
    />
  );
}

function getBestThirdStat(player: Player): { label: string; value: number } {
  // Use current season stats if available, else career
  const apg = player.current_apg ?? player.apg;
  const spg = player.current_spg ?? player.spg ?? 0;
  const bpg = player.current_bpg ?? player.bpg ?? 0;

  // Normalize to typical NBA elite range so the most impressive stat wins
  // APG: elite ~10  | SPG: elite ~2.0  | BPG: elite ~3.5
  const candidates = [
    { label: "APG", value: apg,  score: apg / 10 },
    { label: "SPG", value: spg,  score: spg / 2.0 },
    { label: "BPG", value: bpg,  score: bpg / 3.5 },
  ].filter(c => c.value > 0);

  if (candidates.length === 0) return { label: "APG", value: player.apg };
  return candidates.reduce((best, c) => c.score > best.score ? c : best);
}

function isActiveSeason(player: Player): boolean {
  return player.current_ppg != null;
}

function PlayerHeadshot({ player }: { player: Player }) {
  const [failed, setFailed] = useState(false);
  const initials = player.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div className="relative h-16 w-12 shrink-0 overflow-hidden rounded-lg bg-white/10 border border-border-subtle flex items-center justify-center">
      {failed ? (
        <span className="text-sm font-bold text-text-tertiary">{initials}</span>
      ) : (
        <img
          src={`/api/headshot/${player.id}`}
          alt={player.name}
          className="h-full w-full object-cover"
          style={{ objectPosition: "center 5%" }}
          onError={() => setFailed(true)}
        />
      )}
    </div>
  );
}

interface PlayerListProps {
  players: Player[];
  showRank?: boolean;
  selectedIds?: Set<number>;
  onPlayerClick?: (player: Player) => void;
}

export function PlayerList({
  players,
  showRank = true,
  selectedIds,
  onPlayerClick,
}: PlayerListProps) {
  const isSelectable = !!onPlayerClick;

  return (
    <div className="flex flex-col gap-3">
      {players.map((player, i) => {
        const isSelected = selectedIds?.has(player.id) ?? false;

        return (
          <div
            key={player.id}
            onClick={() => {
              if (isSelectable && !isSelected) onPlayerClick(player);
            }}
            className={cn(
              "flex items-center gap-4 rounded-xl border px-4 py-3.5 transition-all duration-200",
              isSelectable && !isSelected && "cursor-pointer hover:border-gold/40 hover:bg-card-hover hover:shadow-[0_0_20px_rgba(76,201,240,0.06)]",
              isSelected
                ? "border-gold/40 bg-gold/5 shadow-[0_0_24px_rgba(76,201,240,0.08)]"
                : "border-border-subtle bg-card",
              isSelectable && isSelected && "cursor-default"
            )}
          >
            {/* 1. Jersey / Rank */}
            {showRank && (
              <div className={cn(
                "flex h-8 w-9 shrink-0 items-center justify-center rounded-md text-sm font-bold",
                isSelected ? "bg-gold/15 text-gold" : "bg-surface text-gold/50"
              )} style={{ fontFamily: "var(--font-numeric)" }}>
                {isSelected ? (
                  <Check className="h-3.5 w-3.5" />
                ) : player.jersey ? (
                  <span className="text-xs">#{player.jersey}</span>
                ) : (
                  i + 1
                )}
              </div>
            )}

            {/* 2. Headshot */}
            <PlayerHeadshot player={player} />

            {/* 3. Name + team + awards */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className={cn("font-semibold text-base truncate", isSelected && "text-gold")}>
                  {player.name}
                </span>
                {player.position && (
                  <span className="text-xs text-text-tertiary shrink-0">{player.position}</span>
                )}
              </div>
              <div className="flex items-center gap-1.5 text-xs text-text-secondary mt-0.5">
                {player.team && <span>{player.team}</span>}
                {player.teams && player.teams.length > 0 && !player.team && (
                  <span>{player.teams.slice(0, 3).join(" · ")}</span>
                )}
                {player.from_year && player.to_year && (
                  <span className="text-text-tertiary">{player.from_year}–{player.to_year}</span>
                )}
              </div>
              <AwardBadges awards={player.awards} />
            </div>

            {/* 4. Stats */}
            <div className="flex shrink-0 self-center flex-col items-end gap-1">
              <div className="flex items-center gap-1.5">
                <StatBadge label="PPG" value={player.current_ppg ?? player.ppg} />
                <StatBadge label="RPG" value={player.current_rpg ?? player.rpg} />
                <StatBadge {...getBestThirdStat(player)} />
              </div>
              {isActiveSeason(player) && (
                <span className="text-[9px] uppercase tracking-wider text-gold/60 font-semibold">
                  this season
                </span>
              )}
            </div>

          </div>
        );
      })}
    </div>
  );
}
