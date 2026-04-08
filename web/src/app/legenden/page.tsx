import { SplitCategoryPage, type CategoryPill } from "@/components/categories/SplitCategoryPage";

const CATEGORIES: CategoryPill[] = [
  // All-Time GOATs
  { label: "All-Time 5", path: "all-time", params: { limit: 30 }, cardSubtitle: "ALL-TIME GREATEST" },
  // By Position (filtered from legend players)
  { label: "Guards", path: "position/G", params: { limit: 30 }, cardSubtitle: "TOP GUARDS" },
  { label: "Forwards", path: "position/F", params: { limit: 30 }, cardSubtitle: "TOP FORWARDS" },
  { label: "Centers", path: "position/C", params: { limit: 30 }, cardSubtitle: "TOP CENTERS" },
  // All-Time 5 by Era
  { label: "1960s", path: "era/1960", params: { limit: 30 }, cardSubtitle: "BEST OF THE 1960s" },
  { label: "1970s", path: "era/1970", params: { limit: 30 }, cardSubtitle: "BEST OF THE 1970s" },
  { label: "1980s", path: "era/1980", params: { limit: 30 }, cardSubtitle: "BEST OF THE 1980s" },
  { label: "1990s", path: "era/1990", params: { limit: 30 }, cardSubtitle: "BEST OF THE 1990s" },
  { label: "2000s", path: "era/2000", params: { limit: 30 }, cardSubtitle: "BEST OF THE 2000s" },
  { label: "2010s", path: "era/2010", params: { limit: 30 }, cardSubtitle: "BEST OF THE 2010s" },
  { label: "2020s", path: "era/2020", params: { limit: 30 }, cardSubtitle: "BEST OF THE 2020s" },
];

export default function LegendenPage() {
  return <SplitCategoryPage title="Legends" categories={CATEGORIES} />;
}
