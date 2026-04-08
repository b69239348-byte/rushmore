"use client";

import { CategoryPage } from "@/components/categories/CategoryPage";

export default function CurrentSeasonPage() {
  return <CategoryPage path="current-season" params={{ limit: 30 }} />;
}
