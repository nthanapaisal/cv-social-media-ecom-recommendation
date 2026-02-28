"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchShopProducts } from "@/lib/api-client";
import type { ProductMetadata } from "@/lib/types";
import { useAppStore } from "@/store/app-store";

export function useProducts(category?: string | null) {
  const watchedBuckets = useAppStore((s) => s.watchedBuckets);

  const query = useQuery({
    queryKey: ["shop-products"],
    queryFn: fetchShopProducts,
    staleTime: 60_000,
    retry: 1,
  });

  let products: ProductMetadata[] = query.data ?? [];

  if (category) {
    products = products.filter((p) => p.bucket_name === category);
  }

  // Sort by relevance to watched video buckets
  products = [...products].sort((a, b) => {
    const aScore = watchedBuckets[a.bucket_name] || 0;
    const bScore = watchedBuckets[b.bucket_name] || 0;
    return bScore - aScore;
  });

  return {
    products,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: query.refetch,
  };
}
