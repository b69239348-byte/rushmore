"use client";

import { CategoryPage } from "@/components/categories/CategoryPage";

export default function ChampionsPage() {
  return <CategoryPage path="champions" params={{ limit: 20 }} />;
}
