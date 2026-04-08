const API_BASE = "/api";

export interface Player {
  id: number;
  name: string;
  position?: string;
  team?: string;
  teams?: string[];
  main_team?: string;
  jersey?: string;
  current_ppg?: number;
  current_rpg?: number;
  current_apg?: number;
  current_spg?: number;
  current_bpg?: number;
  ppg: number;
  rpg: number;
  apg: number;
  spg?: number;
  bpg?: number;
  from_year?: number;
  to_year?: number;
  total_points?: number;
  total_points_season?: number;
  awards?: {
    championships?: number;
    mvps?: number;
    all_stars?: number;
    finals_mvps?: number;
  };
}

export interface CategoryResult {
  title: string;
  subtitle: string;
  players: Player[];
}

export interface CategoriesIndex {
  all_time: { label: string; sort_options: string[] };
  positions: Record<string, string>;
  teams: Record<string, string>;
  eras: Record<number, string>;
  champions: { label: string };
  mvps: { label: string };
  current_season: { label: string };
  active: { label: string };
}

export async function fetchCategories(): Promise<CategoriesIndex> {
  const res = await fetch(`${API_BASE}/categories`);
  return res.json();
}

export async function fetchCategory(
  path: string,
  params?: Record<string, string | number>
): Promise<CategoryResult> {
  const url = new URL(`${API_BASE}/categories/${path}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([k, v]) =>
      url.searchParams.set(k, String(v))
    );
  }
  const res = await fetch(url.toString());
  return res.json();
}

export async function searchPlayers(
  query: string,
  limit = 40
): Promise<Player[]> {
  const res = await fetch(
    `${API_BASE}/players?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  return res.json();
}

export async function generateTeamCard(
  teamCodes: string[],
  title?: string,
  tierLabels?: string[]
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/generate-teams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      team_codes: teamCodes,
      title: title || "MY TOP 5 TEAMS",
      tier_labels: tierLabels || [],
    }),
  });
  return res.blob();
}

export async function generateCard(
  playerIds: number[],
  title?: string,
  subtitle?: string,
  background?: string
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player_ids: playerIds,
      title: title || "MY MT. RUSHMORE",
      subtitle: subtitle || "ALL-TIME GREATEST",
      ...(background && { background }),
    }),
  });
  return res.blob();
}
