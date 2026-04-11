"use client";

import { useSearchParams } from "next/navigation";
import { useState, Suspense } from "react";
import { CategoryFilter } from "@/components/shop/CategoryFilter";
import { ProductGrid } from "@/components/shop/ProductGrid";
import { useProducts } from "@/hooks/use-products";
import { useAppStore } from "@/store/app-store";
import { PageTransition } from "@/components/layout/PageTransition";
import { Sparkles } from "lucide-react";

function ShopContent() {
  const searchParams = useSearchParams();
  const categoryFromUrl = searchParams.get("category");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    categoryFromUrl
  );

  const { products, isLoading } = useProducts(selectedCategory);
  const watchedBuckets = useAppStore((s) => s.watchedBuckets);
  const hasRecommendations = Object.keys(watchedBuckets).length > 0;

  return (
    <PageTransition>
      <div className="h-full overflow-y-auto scrollbar-hide">
        <CategoryFilter
          selected={selectedCategory}
          onSelect={setSelectedCategory}
        />

        {hasRecommendations && !selectedCategory && (
          <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 pt-3 pb-1">
            <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/5 px-3.5 py-1.5">
              <Sparkles className="w-3.5 h-3.5 shrink-0 text-violet-400" />
              <span className="text-[11px] md:text-xs font-medium text-white/55">
                Personalized from your feed
              </span>
            </div>
          </div>
        )}

        <ProductGrid products={products} isLoading={isLoading} />
      </div>
    </PageTransition>
  );
}

export default function ShopPage() {
  return (
    <Suspense>
      <ShopContent />
    </Suspense>
  );
}
