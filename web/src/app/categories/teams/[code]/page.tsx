"use client";

import { use } from "react";
import { CategoryPage } from "@/components/categories/CategoryPage";

export default function TeamPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  const { code } = use(params);
  return (
    <CategoryPage
      path={`team/${code.toUpperCase()}`}
      params={{ limit: 10 }}
    />
  );
}
