"use client";

import { CategoryPage } from "@/components/categories/CategoryPage";

export default function MvpsPage() {
  return <CategoryPage path="mvps" params={{ limit: 20 }} />;
}
