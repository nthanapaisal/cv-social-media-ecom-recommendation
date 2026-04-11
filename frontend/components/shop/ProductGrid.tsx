"use client";

import { ProductCard } from "./ProductCard";
import { Skeleton } from "@/components/ui/skeleton";
import { ShoppingBag } from "lucide-react";
import type { ProductMetadata } from "@/lib/types";

interface ProductGridProps {
  products: ProductMetadata[];
  isLoading: boolean;
}

const gridClass =
  "max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 md:gap-5 lg:gap-6 px-4 md:px-6 lg:px-8";

export function ProductGrid({ products, isLoading }: ProductGridProps) {
  if (isLoading) {
    return (
      <div className={`${gridClass} pb-6 pt-2`}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="aspect-square rounded-2xl ring-1 ring-white/[0.04]" />
            <Skeleton className="h-4 w-[85%] rounded-md" />
            <Skeleton className="h-3 w-1/2 rounded-md" />
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 py-16 md:py-20">
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/[0.08] bg-white/[0.02] px-8 py-16 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/[0.05] ring-1 ring-white/[0.06]">
            <ShoppingBag className="h-7 w-7 text-white/25" />
          </div>
          <p className="text-sm font-medium text-white/50">No products found</p>
          <p className="mt-1.5 max-w-xs text-xs text-white/30">
            Try another category or refresh — new items appear here as they&apos;re listed.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${gridClass} pb-24 pt-2 md:pb-10`}>
      {products.map((product) => (
        <ProductCard key={product.product_id} product={product} />
      ))}
    </div>
  );
}
