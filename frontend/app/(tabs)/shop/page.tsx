"use client";

import { useSearchParams } from "next/navigation";
import { useState, Suspense, useMemo, useEffect } from "react";
import { CategoryFilter } from "@/components/shop/CategoryFilter";
import { ProductGrid } from "@/components/shop/ProductGrid";
import { useProducts } from "@/hooks/use-products";
import { useRecommendationTracker } from "@/hooks/use-recommendation-tracker";
import { SurveyModal } from "@/components/ui/survey-modal";
import { useAppStore } from "@/store/app-store";
import { PageTransition } from "@/components/layout/PageTransition";
import { Sparkles } from "lucide-react";

const PRODUCT_SURVEY_THRESHOLD = 5; // Show survey every 5 product page loads

function ShopContent() {
  const searchParams = useSearchParams();
  const categoryFromUrl = searchParams.get("category");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    categoryFromUrl
  );
  const [loadCount, setLoadCount] = useState(0); // Track number of times shop loads

  const { products, isLoading } = useProducts(selectedCategory);
  const watchedBuckets = useAppStore((s) => s.watchedBuckets);
  const hasRecommendations = Object.keys(watchedBuckets).length > 0;

  const [showSurvey, setShowSurvey] = useState(false);
  const [userId] = useState(() => {
    if (typeof window === "undefined") return "unknown";
    const stored = localStorage.getItem("user_id");
    if (stored) return stored;
    const newId = `user_${Date.now()}`;
    localStorage.setItem("user_id", newId);
    return newId;
  });

  const currentRecommendationId = useMemo(() => {
    return `prod_rec_${loadCount}_${Date.now()}`;
  }, [loadCount]);

  const currentProductIds = useMemo(() => {
    return products.map((p) => p.product_id);
  }, [products]);

  // Track when products finish loading (don't reset count on category change)
  useEffect(() => {
    if (!isLoading && products.length > 0) {
      setLoadCount((prev) => {
        const newCount = prev + 1;
        console.log(`[SHOP] Product load count: ${newCount}`);
        return newCount;
      });
    }
  }, [isLoading, products.length]);

  // Show survey when load count is multiple of threshold
  useEffect(() => {
    console.log(`[SHOP] Load count: ${loadCount}, threshold: ${PRODUCT_SURVEY_THRESHOLD}, should show: ${loadCount > 0 && loadCount % PRODUCT_SURVEY_THRESHOLD === 0}`);
    if (loadCount > 0 && loadCount % PRODUCT_SURVEY_THRESHOLD === 0) {
      console.log(`[SHOP] Showing survey modal!`);
      setShowSurvey(true);
    }
  }, [loadCount]);

  const handleSurveySubmit = () => {
    // Survey submitted, will show next survey in 5 more loads
  };

  return (
    <PageTransition>
      <SurveyModal
        open={showSurvey}
        onOpenChange={setShowSurvey}
        userId={userId}
        recommendationId={currentRecommendationId}
        itemsShown={currentProductIds}
        onSubmit={handleSurveySubmit}
      />
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
