import { SplitCategoryPage, type CategoryPill } from "@/components/categories/SplitCategoryPage";

const CATEGORIES: CategoryPill[] = [
  { label: "MVP", path: "current-mvp", params: { limit: 200 }, cardSubtitle: "MVP RACE" },
  { label: "DPOY", path: "current-dpoy", params: { limit: 200 }, cardSubtitle: "DPOY RACE" },
  { label: "ROY", path: "current-roy", params: { limit: 200 }, cardSubtitle: "ROOKIE OF THE YEAR" },
  { label: "MIP", path: "current-mip", params: { limit: 200 }, cardSubtitle: "MOST IMPROVED" },
  { label: "All-NBA 1", path: "all-nba/1", params: { limit: 200 }, cardSubtitle: "ALL-NBA FIRST TEAM" },
  { label: "All-NBA 2", path: "all-nba/2", params: { limit: 200 }, cardSubtitle: "ALL-NBA SECOND TEAM" },
  { label: "All-NBA 3", path: "all-nba/3", params: { limit: 200 }, cardSubtitle: "ALL-NBA THIRD TEAM" },
];

export default function AktuellPage() {
  return <SplitCategoryPage title="This Season" categories={CATEGORIES} />;
}
