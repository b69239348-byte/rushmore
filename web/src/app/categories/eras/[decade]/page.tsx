"use client";

import { use } from "react";
import { CategoryPage } from "@/components/categories/CategoryPage";

export default function EraPage({
  params,
}: {
  params: Promise<{ decade: string }>;
}) {
  const { decade } = use(params);
  return (
    <CategoryPage path={`era/${decade}`} params={{ limit: 30 }} />
  );
}
