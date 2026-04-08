"use client";

import { CategoryPage } from "@/components/categories/CategoryPage";

export default function ActivePage() {
  return <CategoryPage path="active" params={{ limit: 10 }} />;
}
