"use client";

import { CategoryPage } from "@/components/categories/CategoryPage";

export default function AllTimePage() {
  return <CategoryPage path="all-time" params={{ limit: 30 }} />;
}
