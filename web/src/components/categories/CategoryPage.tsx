"use client";

import { useEffect, useState } from "react";
import { fetchCategory, type CategoryResult } from "@/lib/api";
import { CategoryHeader } from "./CategoryHeader";
import { PlayerList } from "./PlayerList";
import { Loader2 } from "lucide-react";

interface CategoryPageProps {
  path: string;
  params?: Record<string, string | number>;
}

export function CategoryPage({ path, params }: CategoryPageProps) {
  const [data, setData] = useState<CategoryResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchCategory(path, params)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [path, params]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-text-tertiary" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="flex h-full flex-col">
      <div className="relative border-b border-border-subtle px-4 pt-4 pb-3 md:px-6 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -top-8 bg-[radial-gradient(ellipse_at_50%_0%,rgba(201,168,76,0.07)_0%,transparent_70%)]" />
        <CategoryHeader title={data.title} subtitle={data.subtitle} />
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-4 py-4 md:px-6">
          <PlayerList players={data.players} />
        </div>
      </div>
    </div>
  );
}
