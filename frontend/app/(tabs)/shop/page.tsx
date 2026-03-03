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
          <div className="max-w-7xl mx-auto flex items-center gap-2 px-4 md:px-6 lg:px-8 py-2">
            <Sparkles className="w-4 h-4 text-yellow-400" />
            <span className="text-xs text-white/50">
              Sorted by your viewing history
            </span>
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
