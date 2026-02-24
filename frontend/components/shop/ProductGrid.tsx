"use client";

import { ProductCard } from "./ProductCard";
import { Skeleton } from "@/components/ui/skeleton";
import { ShoppingBag } from "lucide-react";
import type { ProductMetadata } from "@/lib/types";

interface ProductGridProps {
  products: ProductMetadata[];
  isLoading: boolean;
}

export function ProductGrid({ products, isLoading }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 px-4 pb-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="aspect-square rounded-xl" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center px-8">
        <ShoppingBag className="w-12 h-12 text-white/20 mb-4" />
        <p className="text-white/50 text-sm">No products found</p>
        <p className="text-white/30 text-xs mt-1">
          Try a different category or check back later
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 px-4 pb-24">
      {products.map((product) => (
        <ProductCard key={product.product_id} product={product} />
      ))}
    </div>
  );
}
