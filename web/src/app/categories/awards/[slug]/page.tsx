"use client";

import { use } from "react";
import { CategoryPage } from "@/components/categories/CategoryPage";

export default function AwardPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  return <CategoryPage path={`awards/${slug}`} params={{ limit: 10 }} />;
}
