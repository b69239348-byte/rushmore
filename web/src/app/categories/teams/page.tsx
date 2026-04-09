"use client";

import { useState, useEffect, useRef } from "react";
import { X, Download, Loader2, Pencil, Check, Plus, Trophy, Sparkles } from "lucide-react";
import { getTeamLogoUrl } from "@/lib/teams";
import { generateTeamCard } from "@/lib/api";
import { CardPreview } from "@/components/builder/CardPreview";
import { cn } from "@/lib/utils";

// ─────────────────────────────────────────────────────────────────────────────
// Data
// ─────────────────────────────────────────────────────────────────────────────

const TEAMS = [
  { code: "ATL", name: "Hawks" }, { code: "BOS", name: "Celtics" },
  { code: "BKN", name: "Nets" }, { code: "CHA", name: "Hornets" },
  { code: "CHI", name: "Bulls" }, { code: "CLE", name: "Cavaliers" },
  { code: "DAL", name: "Mavericks" }, { code: "DEN", name: "Nuggets" },
  { code: "DET", name: "Pistons" }, { code: "GSW", name: "Warriors" },
  { code: "HOU", name: "Rockets" }, { code: "IND", name: "Pacers" },
  { code: "LAC", name: "Clippers" }, { code: "LAL", name: "Lakers" },
  { code: "MEM", name: "Grizzlies" }, { code: "MIA", name: "Heat" },
  { code: "MIL", name: "Bucks" }, { code: "MIN", name: "Timberwolves" },
  { code: "NOP", name: "Pelicans" }, { code: "NYK", name: "Knicks" },
  { code: "OKC", name: "Thunder" }, { code: "ORL", name: "Magic" },
  { code: "PHI", name: "76ers" }, { code: "PHX", name: "Suns" },
  { code: "POR", name: "Trail Blazers" }, { code: "SAC", name: "Kings" },
  { code: "SAS", name: "Spurs" }, { code: "TOR", name: "Raptors" },
  { code: "UTA", name: "Jazz" }, { code: "WAS", name: "Wizards" },
];

const TIER_COLORS = ["#4cc9f0", "#7b61ff", "#f72585", "#ff9f1c", "#06d6a0", "#ff6b6b"];

// ─────────────────────────────────────────────────────────────────────────────
// Shared: Team Tile
// ─────────────────────────────────────────────────────────────────────────────

function TeamTile({ code, selected, onClick, dim }: {
  code: string; selected?: boolean; onClick?: () => void; dim?: boolean;
}) {
  const team = TEAMS.find(t => t.code === code);
  const logo = getTeamLogoUrl(code);
  return (
    <button onClick={onClick}
      className={cn(
        "relative flex flex-col items-center justify-end overflow-hidden rounded-xl border transition-all aspect-[4/3]",
        dim ? "opacity-40 pointer-events-none" : "cursor-pointer",
        selected ? "border-gold/50 bg-card-hover" : "border-border-subtle bg-card hover:border-gold/30 hover:bg-card-hover"
      )}>
      {logo && (
        <div className="absolute inset-0 flex items-center justify-center p-4">
          <div className="absolute inset-4 rounded-xl bg-white/18" />
          <img src={logo} alt={code} draggable={false} onDragStart={e => e.preventDefault()} className="relative w-full h-full object-contain pointer-events-none" />
        </div>
      )}
      {selected && <div className="absolute inset-0 bg-gold/8" />}
      <div className="relative z-10 w-full bg-gradient-to-t from-bg/90 to-transparent px-2 pb-2 pt-5 text-center">
        <div className={cn("text-sm font-black tracking-wide", selected ? "text-gold" : "text-text")}>{code}</div>
        <div className="text-[10px] text-text-tertiary leading-tight truncate">{team?.name}</div>
      </div>
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// BUILD YOUR TIERS
// ─────────────────────────────────────────────────────────────────────────────

type Tier = { id: number; name: string; teams: string[] };

function TiersPanel({ tiers, onUpdate }: {
  tiers: Tier[]; onUpdate: (tiers: Tier[]) => void;
}) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");

  const removeTier = (id: number) => onUpdate(tiers.filter(t => t.id !== id));
  const addTier = () => onUpdate([...tiers, { id: Date.now(), name: `Tier ${tiers.length + 1}`, teams: [] }]);
  const saveEdit = (id: number) => {
    onUpdate(tiers.map(t => t.id === id ? { ...t, name: editName } : t));
    setEditingId(null);
  };
  const removeTeam = (tierId: number, code: string) => {
    onUpdate(tiers.map(t => t.id === tierId ? { ...t, teams: t.teams.filter(c => c !== code) } : t));
  };

  return (
    <div className="flex flex-col gap-2 h-full overflow-y-auto">
      <p className="text-xs font-semibold uppercase tracking-widest text-text-tertiary mb-1">Your Tiers</p>
      {tiers.map((tier, ti) => (
        <div key={tier.id} className="rounded-xl border border-border-subtle bg-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: TIER_COLORS[ti % TIER_COLORS.length] }} />
            {editingId === tier.id ? (
              <div className="flex items-center gap-1.5 flex-1">
                <input autoFocus value={editName} onChange={e => setEditName(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && saveEdit(tier.id)}
                  className="flex-1 bg-surface border border-gold/40 rounded px-2 py-0.5 text-xs font-bold focus:outline-none min-w-0" />
                <button onClick={() => saveEdit(tier.id)} className="text-gold shrink-0"><Check className="h-3.5 w-3.5" /></button>
              </div>
            ) : (
              <>
                <span className="text-xs font-bold flex-1 min-w-0 truncate">{tier.name}</span>
                <button onClick={() => { setEditingId(tier.id); setEditName(tier.name); }} className="p-0.5 text-text-tertiary hover:text-text shrink-0"><Pencil className="h-3 w-3" /></button>
                {tiers.length > 1 && <button onClick={() => removeTier(tier.id)} className="p-0.5 text-text-tertiary hover:text-red-400 shrink-0"><X className="h-3 w-3" /></button>}
              </>
            )}
          </div>
          {tier.teams.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {tier.teams.map(code => {
                const logo = getTeamLogoUrl(code);
                return (
                  <div key={code} className="flex items-center gap-1 rounded bg-surface border border-border-subtle px-1.5 py-0.5 group">
                    {logo && <img src={logo} alt={code} draggable={false} onDragStart={e => e.preventDefault()} className="h-4 w-4 object-contain pointer-events-none" />}
                    <span className="text-[10px] font-bold">{code}</span>
                    <button onClick={() => removeTeam(tier.id, code)} className="opacity-0 group-hover:opacity-100 text-text-tertiary hover:text-red-400 ml-0.5"><X className="h-2.5 w-2.5" /></button>
                  </div>
                );
              })}
            </div>
          ) : <p className="text-[10px] text-text-tertiary italic">Empty</p>}
        </div>
      ))}
      {tiers.length < 6 && (
        <button onClick={addTier}
          className="flex items-center gap-1.5 rounded-xl border border-dashed border-border px-3 py-2 text-xs text-text-tertiary hover:text-text hover:border-border-subtle transition-colors">
          <Plus className="h-3.5 w-3.5" /> Add tier
        </button>
      )}
    </div>
  );
}

function TiersTab() {
  const [tiers, setTiers] = useState<Tier[]>([
    { id: 1, name: "Elite", teams: [] },
    { id: 2, name: "Contender", teams: [] },
    { id: 3, name: "Fringe", teams: [] },
  ]);
  const [activeTier, setActiveTier] = useState<number | null>(null);
  const [exporting, setExporting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const usedTeams = new Set(tiers.flatMap(t => t.teams));

  const handleTeamClick = (code: string) => {
    if (!activeTier) return;
    const inTier = tiers.find(t => t.id === activeTier)?.teams.includes(code);
    if (inTier) {
      setTiers(p => p.map(t => t.id === activeTier ? { ...t, teams: t.teams.filter(c => c !== code) } : t));
    } else if (!usedTeams.has(code)) {
      setTiers(p => p.map(t => t.id === activeTier ? { ...t, teams: [...t.teams, code] } : t));
    }
  };

  const doExport = async () => {
    const flatTeams = tiers.flatMap(t => t.teams.map(code => ({ code, tier: t.name })));
    const limited = flatTeams.slice(0, 5);
    if (!limited.length) return;
    const codes = limited.map(t => t.code);
    const tierLabels = limited.map(t => t.tier);
    const title = tiers.find(t => t.teams.length > 0)?.name.toUpperCase() ?? "MY TIERS";
    setExporting(true);
    try {
      const blob = await generateTeamCard(codes, title, tierLabels);
      setPreviewUrl(URL.createObjectURL(blob));
    } catch (e) { console.error(e); } finally { setExporting(false); }
  };

  const activeTierName = tiers.find(t => t.id === activeTier)?.name;

  return (
    <div className="flex min-h-0 flex-1">
      {/* Team tiles */}
      <div className="flex-1 overflow-y-auto pb-32 md:pb-8">
        <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
          {activeTier ? (
            <p className="text-xs text-text-tertiary mb-3 uppercase tracking-widest font-semibold">
              Adding to: <span className="text-gold">{activeTierName}</span> — tap to add / remove
            </p>
          ) : (
            <p className="text-xs text-text-tertiary mb-3">Select a tier below, then tap teams to add them.</p>
          )}
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
            {TEAMS.map(t => {
              const inActive = !!tiers.find(tr => tr.id === activeTier)?.teams.includes(t.code);
              const inOther = !inActive && usedTeams.has(t.code);
              return (
                <TeamTile key={t.code} code={t.code}
                  selected={inActive}
                  dim={!!activeTier && inOther}
                  onClick={() => handleTeamClick(t.code)} />
              );
            })}
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-72 shrink-0 flex-col border-l border-border-subtle p-4 sticky top-0 self-start max-h-[calc(100vh-120px)] overflow-y-auto gap-3">
        <div className="flex flex-col gap-2 flex-1 overflow-y-auto">
          <p className="text-xs font-semibold uppercase tracking-widest text-text-tertiary">Your Tiers</p>
          {tiers.map((tier, ti) => (
            <div key={tier.id}
              onClick={() => setActiveTier(activeTier === tier.id ? null : tier.id)}
              className={cn("rounded-xl border p-2.5 cursor-pointer transition-all",
                activeTier === tier.id ? "border-gold/50 bg-card-hover" : "border-border-subtle bg-card hover:border-border")}>
              <TierPanelRow tier={tier} tierIndex={ti} isActive={activeTier === tier.id}
                tiers={tiers} onUpdate={setTiers} />
            </div>
          ))}
          {tiers.length < 6 && (
            <button onClick={e => { e.stopPropagation(); setTiers(p => [...p, { id: Date.now(), name: `Tier ${p.length + 1}`, teams: [] }]); }}
              className="flex items-center gap-1.5 rounded-xl border border-dashed border-border px-3 py-2 text-xs text-text-tertiary hover:text-text transition-colors">
              <Plus className="h-3.5 w-3.5" /> Add tier
            </button>
          )}
        </div>
        {usedTeams.size > 0 && (
          <button onClick={doExport} disabled={exporting}
            className="flex items-center justify-center gap-2 rounded-xl bg-gold py-2.5 text-sm font-bold text-bg hover:bg-gold-bright disabled:opacity-50">
            {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            Drop the Card
          </button>
        )}
      </aside>

      {/* Mobile bottom bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-30 border-t border-border-subtle bg-bg/95 backdrop-blur-sm px-4 py-3 flex flex-col gap-2">
        {/* Tier pills */}
        <div className="flex gap-2 overflow-x-auto no-scrollbar pb-0.5">
          {tiers.map((tier) => (
            <button
              key={tier.id}
              onClick={() => setActiveTier(activeTier === tier.id ? null : tier.id)}
              className={cn(
                "shrink-0 flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-semibold transition-all",
                activeTier === tier.id
                  ? "border-gold bg-gold/10 text-gold"
                  : "border-border-subtle bg-card text-text-secondary"
              )}
            >
              {tier.name}
              {tier.teams.length > 0 && (
                <span className={cn(
                  "rounded-full px-1.5 py-0.5 text-[10px] font-bold",
                  activeTier === tier.id ? "bg-gold/20 text-gold" : "bg-surface text-text-tertiary"
                )}>
                  {tier.teams.length}
                </span>
              )}
            </button>
          ))}
          {tiers.length < 6 && (
            <button
              onClick={() => setTiers(p => [...p, { id: Date.now(), name: `Tier ${p.length + 1}`, teams: [] }])}
              className="shrink-0 flex items-center gap-1 rounded-full border border-dashed border-border px-3 py-1.5 text-xs text-text-tertiary"
            >
              <Plus className="h-3 w-3" /> Add
            </button>
          )}
        </div>
        {/* Export row */}
        {usedTeams.size > 0 && (
          <button onClick={doExport} disabled={exporting}
            className="flex items-center justify-center gap-2 rounded-xl bg-gold py-2.5 text-sm font-bold text-bg hover:bg-gold-bright disabled:opacity-50">
            {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            Drop the Card
          </button>
        )}
      </div>

      {previewUrl && <CardPreview url={previewUrl} onClose={() => setPreviewUrl(null)} />}
    </div>
  );
}

function TierPanelRow({ tier, tierIndex, isActive, tiers, onUpdate }: {
  tier: Tier; tierIndex: number; isActive: boolean;
  tiers: Tier[]; onUpdate: (t: Tier[]) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(tier.name);

  const save = (e: React.MouseEvent) => {
    e.stopPropagation();
    onUpdate(tiers.map(t => t.id === tier.id ? { ...t, name } : t));
    setEditing(false);
  };

  return (
    <>
      <div className="flex items-center gap-1.5 mb-1.5">
        <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: TIER_COLORS[tierIndex % TIER_COLORS.length] }} />
        {editing ? (
          <div className="flex items-center gap-1 flex-1" onClick={e => e.stopPropagation()}>
            <input autoFocus value={name} onChange={e => setName(e.target.value)}
              onKeyDown={e => e.key === "Enter" && save(e as any)}
              className="flex-1 bg-surface border border-gold/40 rounded px-1.5 py-0.5 text-xs font-bold focus:outline-none min-w-0" />
            <button onClick={save} className="text-gold shrink-0"><Check className="h-3 w-3" /></button>
          </div>
        ) : (
          <>
            <span className={cn("text-xs font-bold flex-1 truncate min-w-0", isActive && "text-gold")}>{tier.name}</span>
            <button onClick={e => { e.stopPropagation(); setEditing(true); setName(tier.name); }}
              className="p-0.5 text-text-tertiary hover:text-text shrink-0"><Pencil className="h-3 w-3" /></button>
            {tiers.length > 1 && (
              <button onClick={e => { e.stopPropagation(); onUpdate(tiers.filter(t => t.id !== tier.id)); }}
                className="p-0.5 text-text-tertiary hover:text-red-400 shrink-0"><X className="h-3 w-3" /></button>
            )}
          </>
        )}
      </div>
      {tier.teams.length > 0 ? (
        <div className="flex flex-wrap gap-1">
          {tier.teams.map(code => {
            const logo = getTeamLogoUrl(code);
            return (
              <div key={code} className="flex items-center gap-0.5 rounded bg-surface border border-border-subtle px-1 py-0.5">
                {logo && <img src={logo} alt={code} draggable={false} onDragStart={e => e.preventDefault()} className="h-3.5 w-3.5 object-contain pointer-events-none" />}
                <span className="text-[10px] font-bold">{code}</span>
              </div>
            );
          })}
        </div>
      ) : <p className="text-[10px] text-text-tertiary italic">{isActive ? "Tap teams to add" : "Empty"}</p>}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// PLAYOFF BRACKET — East/West split + drag & drop
// ─────────────────────────────────────────────────────────────────────────────

const WEST_CODES = ["LAL","LAC","GSW","PHX","DEN","MIN","OKC","DAL","HOU","NOP","MEM","SAS","UTA","SAC","POR"];
const EAST_CODES = ["BOS","MIL","PHI","MIA","NYK","ATL","CHI","CLE","IND","TOR","BKN","CHA","WAS","DET","ORL"];

// 31 slots:
//   West R1    0-7    matchups (0,1)(2,3)(4,5)(6,7)
//   West Semi  8-11   matchups (8,9)(10,11)
//   West CF    12-13  matchup  (12,13)
//   NBA Finals 14-15  matchup  (14,15)
//   East CF    16-17  matchup  (16,17)
//   East Semi  18-21  matchups (18,19)(20,21)
//   East R1    22-29  matchups (22,23)(24,25)(26,27)(28,29)
//   Champion   30

function DragChip({ code, dimmed, touchMode, selected, onTap }: {
  code: string; dimmed: boolean;
  touchMode?: boolean; selected?: boolean; onTap?: () => void;
}) {
  const logo = getTeamLogoUrl(code);
  return (
    <div
      draggable={!touchMode}
      onDragStart={!touchMode ? e => {
        e.dataTransfer.setData("text/plain", code);
        e.dataTransfer.effectAllowed = "move";
      } : undefined}
      onClick={touchMode ? onTap : undefined}
      className={cn(
        "flex flex-col items-center gap-1 rounded-xl border px-3 py-2 select-none transition-all shrink-0",
        touchMode ? "cursor-pointer active:scale-95" : "cursor-grab active:cursor-grabbing",
        selected
          ? "border-gold bg-gold/15 shadow-[0_0_12px_rgba(201,168,76,0.25)]"
          : dimmed
          ? "border-border-subtle bg-surface opacity-35 pointer-events-none"
          : "border-border-subtle bg-card hover:border-gold/30 hover:bg-card-hover"
      )}
    >
      {logo && (
        <img
          src={logo} alt={code}
          draggable={false}
          onDragStart={e => e.preventDefault()}
          className="h-10 w-10 object-contain pointer-events-none"
        />
      )}
      <span className="text-[11px] font-black tracking-wide text-text-secondary leading-none">{code}</span>
    </div>
  );
}

function SlotBox({ idx, slots, onAssign, onClear, touchMode, selectedTeam }: {
  idx: number;
  slots: (string|null)[];
  onAssign: (idx: number, code: string) => void;
  onClear: (idx: number) => void;
  touchMode?: boolean;
  selectedTeam?: string | null;
}) {
  const code = slots[idx];
  const logo = code ? getTeamLogoUrl(code) : null;
  const [over, setOver] = useState(false);

  const canReceive = touchMode && !!selectedTeam && !code;

  const handleTap = (e: React.PointerEvent) => {
    if (!touchMode) return;
    e.preventDefault();
    e.stopPropagation();
    if (selectedTeam && !code) onAssign(idx, selectedTeam);
    else if (code) onClear(idx);
  };

  return (
    <div
      onDragOver={!touchMode ? e => { e.preventDefault(); setOver(true); } : undefined}
      onDragLeave={!touchMode ? () => setOver(false) : undefined}
      onDrop={!touchMode ? e => {
        e.preventDefault();
        setOver(false);
        const c = e.dataTransfer.getData("text/plain");
        if (c) onAssign(idx, c);
      } : undefined}
      onPointerUp={touchMode ? handleTap : undefined}
      onClick={!touchMode && code ? () => onClear(idx) : undefined}
      style={touchMode ? { touchAction: "manipulation" } : undefined}
      className={cn(
        "flex items-center gap-1 rounded border w-full min-w-0 transition-all",
        touchMode ? "px-1.5 py-2.5" : "px-1.5 py-1",
        touchMode && (canReceive || code) && "cursor-pointer",
        over ? "border-gold bg-gold/15" :
        canReceive ? "border-gold/60 bg-gold/8 animate-pulse" :
        code ? "border-border-subtle bg-surface" :
               "border-dashed border-border bg-transparent"
      )}
    >
      {logo && <img src={logo} alt={code!} draggable={false} onDragStart={e => e.preventDefault()} className="h-4 w-4 object-contain shrink-0 pointer-events-none" />}
      <span className={cn("text-[10px] font-bold truncate flex-1 min-w-0", code ? "text-text" : "text-text-tertiary")}>
        {code ?? "—"}
      </span>
      {code && (
        <button
          onPointerUp={touchMode ? e => { e.stopPropagation(); onClear(idx); } : undefined}
          onClick={!touchMode ? e => { e.stopPropagation(); onClear(idx); } : undefined}
          className="shrink-0 text-text-tertiary hover:text-red-400"
        >
          <X className="h-2.5 w-2.5" />
        </button>
      )}
    </div>
  );
}

function Pair({ a, b, side, last = false, slots, onAssign, onClear, touchMode, selectedTeam }: {
  a: number; b: number; side: "west" | "east"; last?: boolean;
  slots: (string|null)[];
  onAssign: (i: number, code: string) => void;
  onClear: (i: number) => void;
  touchMode?: boolean;
  selectedTeam?: string | null;
}) {
  const w = side === "west";
  return (
    <div className="relative flex flex-col gap-0.5 w-full">
      <div className="relative">
        <SlotBox idx={a} slots={slots} onAssign={onAssign} onClear={onClear} touchMode={touchMode} selectedTeam={selectedTeam} />
        <div className={cn(
          "absolute top-1/2 w-2 h-[calc(100%+2px)] border-t border-border pointer-events-none",
          w ? "left-full border-r" : "right-full border-l"
        )} />
      </div>
      <div className="relative">
        <SlotBox idx={b} slots={slots} onAssign={onAssign} onClear={onClear} touchMode={touchMode} selectedTeam={selectedTeam} />
        <div className={cn(
          "absolute bottom-1/2 w-2 h-[calc(100%+2px)] border-b border-border pointer-events-none",
          w ? "left-full border-r" : "right-full border-l"
        )} />
      </div>
      {!last && (
        <div className={cn(
          "absolute top-1/2 w-2 border-t border-border pointer-events-none",
          w ? "left-[calc(100%+8px)]" : "right-[calc(100%+8px)]"
        )} />
      )}
    </div>
  );
}

function BracketTab() {
  const [slots, setSlots] = useState<(string|null)[]>(Array(31).fill(null));
  const [exporting, setExporting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [touchMode, setTouchMode] = useState(false);
  const bracketRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setTouchMode("ontouchstart" in window || navigator.maxTouchPoints > 0);
  }, []);

  const usedSet = new Set(slots.filter(Boolean) as string[]);

  const assign = (idx: number, code: string) => {
    setSlots(prev => {
      const next = [...prev];
      next[idx] = code;
      return next;
    });
    setSelectedTeam(null);
  };

  const clear = (idx: number) => {
    setSlots(prev => { const n = [...prev]; n[idx] = null; return n; });
  };

  const handleSelectTeam = (code: string) => {
    setSelectedTeam(prev => prev === code ? null : code);
  };

  const doExport = async () => {
    setExporting(true);
    try {
      const res = await fetch("/api/generate-bracket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slots, title: "MY PLAYOFF BRACKET" }),
      });
      if (!res.ok) throw new Error(`Server error ${res.status}`);
      const blob = await res.blob();
      setPreviewUrl(URL.createObjectURL(blob));
      setExporting(false);
      return;
    } catch {
      // fallback below
    }

    // Legacy html2canvas fallback (may fail with modern CSS)
    if (!bracketRef.current) { setExporting(false); return; }
    try {
      // @ts-ignore
      const { default: html2canvas } = await import("html2canvas");

      // Temporarily hide the CSS trophy background so html2canvas doesn't choke on it
      const el = bracketRef.current;
      const prevBg = el.style.backgroundImage;
      el.style.backgroundImage = "none";

      const canvas = await html2canvas(el, {
        backgroundColor: "#070b14",
        scale: 2,
        useCORS: true,
        logging: false,
        onclone: (_doc: Document, clonedEl: HTMLElement) => {
          const origEls = el.querySelectorAll("*");
          const cloneEls = clonedEl.querySelectorAll("*");
          origEls.forEach((orig, i) => {
            const s = window.getComputedStyle(orig);
            const cs = (cloneEls[i] as HTMLElement).style;
            cs.color = s.color;
            cs.backgroundColor = s.backgroundColor;
            cs.borderColor = s.borderColor;
            cs.borderTopColor = s.borderTopColor;
            cs.borderBottomColor = s.borderBottomColor;
            cs.borderLeftColor = s.borderLeftColor;
            cs.borderRightColor = s.borderRightColor;
            cs.outlineColor = s.outlineColor;
            cs.fill = s.fill;
          });
        },
      });

      el.style.backgroundImage = prevBg;

      // Output canvas 1920×1080
      const out = document.createElement("canvas");
      out.width = 1920; out.height = 1080;
      const ctx = out.getContext("2d")!;

      // 1. Dark base
      ctx.fillStyle = "#070b14";
      ctx.fillRect(0, 0, 1920, 1080);

      // 2. Trophy image manually drawn (faded center)
      await new Promise<void>(resolve => {
        const trophy = new Image();
        trophy.onload = () => {
          const th = 1080 * 0.85;
          const tw = trophy.width * (th / trophy.height);
          ctx.globalAlpha = 0.12;
          ctx.drawImage(trophy, (1920 - tw) / 2, (1080 - th) / 2, tw, th);
          ctx.globalAlpha = 1;
          resolve();
        };
        trophy.onerror = () => resolve();
        trophy.src = "/trophy_celebration.png";
      });

      // 3. Bracket on top
      const sc = Math.min(1920 / canvas.width, 1080 / canvas.height);
      ctx.drawImage(
        canvas,
        (1920 - canvas.width * sc) / 2,
        (1080 - canvas.height * sc) / 2,
        canvas.width * sc,
        canvas.height * sc,
      );

      setPreviewUrl(out.toDataURL("image/png"));
    } catch (e) {
      console.error("Bracket export failed:", e);
    } finally {
      setExporting(false);
    }
  };

  const p = (a: number, b: number, side: "west"|"east", last?: boolean) => (
    <Pair a={a} b={b} side={side} last={last} slots={slots} onAssign={assign} onClear={clear}
          touchMode={touchMode} selectedTeam={selectedTeam} />
  );

  const s = (idx: number) => (
    <SlotBox idx={idx} slots={slots} onAssign={assign} onClear={clear}
             touchMode={touchMode} selectedTeam={selectedTeam} />
  );

  return (
    <div className="flex flex-col min-h-0 flex-1">

      {/* ── Team Tiles: West | East ───────────────────────────────────── */}
      <div className="border-b border-border-subtle px-4 py-3 md:px-6 shrink-0">
        <div className="flex gap-4 max-w-[1200px] mx-auto">
          <div className="flex-1 min-w-0">
            <p className="text-[9px] uppercase tracking-widest font-semibold text-text-tertiary mb-2">Western Conference</p>

            <div className="flex flex-wrap gap-1.5">
              {WEST_CODES.map(c => (
                <DragChip key={c} code={c} dimmed={usedSet.has(c) && selectedTeam !== c}
                  touchMode={touchMode} selected={selectedTeam === c}
                  onTap={() => handleSelectTeam(c)} />
              ))}
            </div>
          </div>
          <div className="w-px bg-border-subtle shrink-0 self-stretch" />
          <div className="flex-1 min-w-0">
            <p className="text-[9px] uppercase tracking-widest font-semibold text-text-tertiary mb-2">Eastern Conference</p>
            <div className="flex flex-wrap gap-1.5">
              {EAST_CODES.map(c => (
                <DragChip key={c} code={c} dimmed={usedSet.has(c) && selectedTeam !== c}
                  touchMode={touchMode} selected={selectedTeam === c}
                  onTap={() => handleSelectTeam(c)} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── Hint ── */}
      <div className="px-4 pt-3 pb-1 md:px-6 shrink-0">
        <p className="text-xs text-center transition-colors duration-200" style={{ color: selectedTeam ? "var(--color-gold)" : "var(--color-text-tertiary)" }}>
          {touchMode
            ? selectedTeam
              ? `${selectedTeam} selected — tap a bracket slot to place`
              : "Tap a team above to select · tap a slot to place · tap slot again to remove"
            : "Drag teams from above into the bracket slots · click a slot to remove"}
        </p>
      </div>

      {/* ── Bracket ──────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-auto px-4 py-3 md:px-6">
        <div
          ref={bracketRef}
          className="relative min-w-[1000px] max-w-[1200px] mx-auto rounded-xl overflow-hidden bg-[#070b14]"
        >

          {/* Trophy image — center background, faded */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: "url('/trophy_celebration.png')",
              backgroundSize: "contain",
              backgroundRepeat: "no-repeat",
              backgroundPosition: "center center",
              opacity: 0.12,
            }}
          />
          <div className="relative z-10">

          {/* Title */}
          <div className="text-center pt-4 pb-2">
            <div className="text-xl font-black tracking-widest text-white uppercase" style={{fontFamily:"Impact, Arial Black, sans-serif", letterSpacing:"0.12em"}}>
              My Playoff Bracket
            </div>
            <div className="text-[10px] tracking-widest text-gold/70 uppercase mt-0.5">▲ Rushmore</div>
          </div>

          {/* Round labels */}
          <div className="flex text-[9px] uppercase tracking-widest text-text-tertiary mb-3">
            <div className="w-[130px] shrink-0 text-center">Round 1</div>
            <div className="w-2 shrink-0" />
            <div className="w-[130px] shrink-0 text-center">Conf. Semis</div>
            <div className="w-2 shrink-0" />
            <div className="w-[130px] shrink-0 text-center">Conf. Finals</div>
            <div className="w-2 shrink-0" />
            <div className="flex-1 text-center font-semibold text-gold">The Finals</div>
            <div className="w-2 shrink-0" />
            <div className="w-[130px] shrink-0 text-center">Conf. Finals</div>
            <div className="w-2 shrink-0" />
            <div className="w-[130px] shrink-0 text-center">Conf. Semis</div>
            <div className="w-2 shrink-0" />
            <div className="w-[130px] shrink-0 text-center">Round 1</div>
          </div>

          {/* Bracket body */}
          <div className="flex h-[560px]">

            {/* West R1 — 4 matchups */}
            <div className="w-[130px] shrink-0 flex flex-col justify-around pr-2">
              {p(0,1,"west")}
              {p(2,3,"west")}
              {p(4,5,"west")}
              {p(6,7,"west")}
            </div>

            <div className="w-2 shrink-0" />

            {/* West Semis — 2 matchups */}
            <div className="w-[130px] shrink-0 flex flex-col justify-around px-2">
              {p(8,9,"west")}
              {p(10,11,"west")}
            </div>

            <div className="w-2 shrink-0" />

            {/* West Conf Finals — 1 matchup */}
            <div className="w-[130px] shrink-0 flex flex-col justify-center px-2">
              {p(12,13,"west",true)}
            </div>

            <div className="w-2 shrink-0" />

            {/* Center: NBA Finals + Champion */}
            <div className="flex-1 flex flex-col justify-center items-center gap-4 px-4">
              <div className="w-full max-w-[170px] flex flex-col gap-1">
                {s(14)}
                <div className="flex items-center gap-1.5 my-0.5">
                  <div className="flex-1 h-px bg-border-subtle" />
                  <span className="text-[8px] font-bold uppercase tracking-widest text-gold">vs</span>
                  <div className="flex-1 h-px bg-border-subtle" />
                </div>
                {s(15)}
              </div>
              {/* Champion zone */}
              <div
                onDragOver={!touchMode ? e => e.preventDefault() : undefined}
                onDrop={!touchMode ? e => { e.preventDefault(); const c = e.dataTransfer.getData("text/plain"); if (c) assign(30, c); } : undefined}
                onPointerUp={touchMode ? e => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (selectedTeam && !slots[30]) assign(30, selectedTeam);
                  else if (slots[30]) clear(30);
                } : undefined}
                style={touchMode ? { touchAction: "manipulation" } : undefined}
                className={cn(
                  "flex flex-col items-center justify-center gap-1.5 rounded-xl border-2 py-3 px-4 w-full max-w-[170px] transition-all",
                  touchMode && (selectedTeam && !slots[30]) && "cursor-pointer",
                  touchMode && slots[30] && "cursor-pointer",
                  slots[30] ? "border-gold/70 bg-gold/10" :
                  (touchMode && selectedTeam) ? "border-gold/60 bg-gold/8 animate-pulse border-dashed" :
                  "border-dashed border-gold/30 hover:border-gold/50"
                )}
              >
                <Trophy className={cn("h-5 w-5", slots[30] ? "text-gold" : "text-text-tertiary")} />
                {slots[30] ? (
                  <>
                    {getTeamLogoUrl(slots[30]) && (
                      <img src={getTeamLogoUrl(slots[30])!} alt={slots[30]} draggable={false} onDragStart={e => e.preventDefault()} className="h-9 w-9 object-contain pointer-events-none" />
                    )}
                    <span className="text-xs font-black text-gold">{slots[30]}</span>
                    <button
                      onPointerUp={e => { e.stopPropagation(); clear(30); }}
                      className="text-[9px] text-text-tertiary hover:text-red-400"
                    >remove</button>
                  </>
                ) : (
                  <span className="text-[9px] text-text-tertiary text-center leading-tight">
                    Champion<br/>{touchMode ? "tap here" : "drop here"}
                  </span>
                )}
              </div>
            </div>

            <div className="w-2 shrink-0" />

            {/* East Conf Finals — 1 matchup */}
            <div className="w-[130px] shrink-0 flex flex-col justify-center px-2">
              {p(16,17,"east",true)}
            </div>

            <div className="w-2 shrink-0" />

            {/* East Semis — 2 matchups */}
            <div className="w-[130px] shrink-0 flex flex-col justify-around px-2">
              {p(18,19,"east")}
              {p(20,21,"east")}
            </div>

            <div className="w-2 shrink-0" />

            {/* East R1 — 4 matchups */}
            <div className="w-[130px] shrink-0 flex flex-col justify-around pl-2">
              {p(22,23,"east")}
              {p(24,25,"east")}
              {p(26,27,"east")}
              {p(28,29,"east")}
            </div>

          </div>
          </div>{/* end relative z-10 */}
        </div>

        {/* Export */}
        <div className="flex justify-center mt-5">
          <button onClick={doExport} disabled={exporting}
            className="flex items-center gap-2 rounded-xl bg-gold px-6 py-2.5 text-sm font-bold text-bg hover:bg-gold-bright disabled:opacity-50 transition-colors">
            {exporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            {exporting ? "Cooking…" : "Drop Your Bracket"}
          </button>
        </div>
      </div>

      {previewUrl && <CardPreview url={previewUrl} onClose={() => { setPreviewUrl(null); setExporting(false); }} />}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN PAGE
// ─────────────────────────────────────────────────────────────────────────────

const TABS = [
  { id: "tiers", label: "Build Your Tiers" },
  { id: "bracket", label: "Playoff Bracket" },
];

export default function TeamsPage() {
  const [tab, setTab] = useState("tiers");
  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border-subtle px-4 pt-4 pb-0 md:px-6">
        <h1 className="text-xl font-black tracking-tight mb-3">Teams</h1>
        <div className="flex gap-2 overflow-x-auto pb-3">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={cn("shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
                tab === t.id ? "bg-gold text-bg" : "bg-surface text-text-secondary hover:bg-card-hover hover:text-text")}>
              {t.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex min-h-0 flex-1">
        {tab === "tiers"   && <TiersTab />}
        {tab === "bracket" && <BracketTab />}
      </div>
    </div>
  );
}
