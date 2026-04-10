export const TEAM_NBA_IDS: Record<string, number> = {
  ATL: 1610612737, BOS: 1610612738, BKN: 1610612751,
  CHA: 1610612766, CHI: 1610612741, CLE: 1610612739,
  DAL: 1610612742, DEN: 1610612743, DET: 1610612765,
  GSW: 1610612744, HOU: 1610612745, IND: 1610612754,
  LAC: 1610612746, LAL: 1610612747, MEM: 1610612763,
  MIA: 1610612748, MIL: 1610612749, MIN: 1610612750,
  NOP: 1610612740, NYK: 1610612752, OKC: 1610612760,
  ORL: 1610612753, PHI: 1610612755, PHX: 1610612756,
  POR: 1610612757, SAC: 1610612758, SAS: 1610612759,
  TOR: 1610612761, UTA: 1610612762, WAS: 1610612764,
};

// Local logos for defunct teams (served from /public/team-logos/)
const LOCAL_LOGOS: Record<string, string> = {
  SEA: "/team-logos/SEA.svg",
};

// Historical abbreviations → current franchise abbreviation
const ABBR_ALIASES: Record<string, string> = {
  UTH: "UTA", SAN: "SAS", NJN: "BKN", NJD: "BKN",
  NOH: "NOP", NOK: "NOP", NOJ: "NOP",
  PHW: "GSW", SFW: "GSW", GOS: "GSW",
  VAN: "MEM", SDC: "LAC", SDR: "LAC",
  SEA: "OKC", KCK: "SAC",
  CHH: "CHA", CHO: "CHA",
  CAP: "WAS", BLT: "WAS",
  STL: "ATL", MIH: "LAL", MNL: "LAL",
  SYR: "PHI", PHL: "PHI",
  NYN: "BKN", ROC: "SAC", CIN: "SAC",
  BUF: "LAC",
};

/** NBA CDN SVG logo URL for a team abbreviation. Returns null if unknown. */
export function getTeamLogoUrl(abbr: string | null | undefined): string | null {
  if (!abbr) return null;
  const upper = abbr.toUpperCase();
  if (LOCAL_LOGOS[upper]) return LOCAL_LOGOS[upper];
  const resolved = ABBR_ALIASES[upper] ?? upper;
  const id = TEAM_NBA_IDS[resolved];
  if (!id) return null;
  return `https://cdn.nba.com/logos/nba/${id}/global/L/logo.svg`;
}

/** Primary team abbreviation for a player (single team or first in array). */
export function getPlayerTeam(player: {
  team?: string | null;
  teams?: string[];
}): string | null {
  return player.team || player.teams?.[0] || null;
}
