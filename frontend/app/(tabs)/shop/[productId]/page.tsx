"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchProductMetadata, getProductImageUrl } from "@/lib/api-client";
import { getMockProducts } from "@/lib/mock-products";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CATEGORY_COLORS } from "@/lib/constants";
import { ArrowLeft, ShoppingBag, Share2 } from "lucide-react";
import Link from "next/link";
import { useProducts } from "@/hooks/use-products";

export default function ProductDetailPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = use(params);
  const isMock = productId.startsWith("mock-");

  const { data: product, isLoading } = useQuery({
    queryKey: ["product", productId],
    queryFn: async () => {
      if (isMock) {
        const allMock = getMockProducts();
        const found = allMock.find((p) => p.product_id === productId);
        if (!found) throw new Error("Not found");
        return found;
      }
      return fetchProductMetadata(productId);
    },
    retry: 1,
  });

  const { products: relatedProducts } = useProducts(
    product?.bucket_name ?? null
  );
  const related = relatedProducts.filter(
    (p) => p.product_id !== productId
  ).slice(0, 4);

  if (isLoading) {
    return (
      <div className="h-full overflow-y-auto p-4 space-y-4">
        <Skeleton className="aspect-square rounded-xl" />
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-white/50 mb-4">Product not found</p>
          <Button variant="secondary" size="sm" asChild>
            <Link href="/shop">Back to Shop</Link>
          </Button>
        </div>
      </div>
    );
  }

  const colorClass =
    CATEGORY_COLORS[product.bucket_name] || CATEGORY_COLORS.other;

  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-24">
      <div className="sticky top-0 z-10 flex items-center gap-3 p-3 bg-black/80 backdrop-blur-lg">
        <Button variant="ghost" size="icon" asChild className="shrink-0">
          <Link href="/shop">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <h2 className="text-sm font-medium truncate">{product.title}</h2>
      </div>

      <div className="relative aspect-square bg-white/5">
        {isMock ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 bg-gradient-to-br from-white/5 to-white/10">
            <ShoppingBag className="w-16 h-16 text-white/15" />
            <span className="text-sm text-white/25 capitalize">
              {product.bucket_name}
            </span>
          </div>
        ) : (
          <img
            src={getProductImageUrl(product.product_id)}
            alt={product.title}
            className="w-full h-full object-cover"
          />
        )}
      </div>

      <div className="p-4 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <h1 className="text-xl font-semibold leading-tight">
              {product.title}
            </h1>
            <Badge
              variant="secondary"
              className={`${colorClass} text-white border-0 text-xs mt-2`}
            >
              {product.bucket_name}
            </Badge>
          </div>
          <Button variant="ghost" size="icon" className="shrink-0">
            <Share2 className="w-5 h-5" />
          </Button>
        </div>

        <p className="text-sm text-white/60 leading-relaxed">
          {product.product_details}
        </p>

        <Button className="w-full" size="lg">
          <ShoppingBag className="w-4 h-4 mr-2" />
          Add to Cart
        </Button>
      </div>

      {related.length > 0 && (
        <div className="p-4 pt-2">
          <h3 className="text-sm font-medium text-white/70 mb-3">
            Related Products
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {related.map((p) => (
              <Link
                key={p.product_id}
                href={`/shop/${p.product_id}`}
                className="block"
              >
                <div className="aspect-square rounded-xl overflow-hidden bg-white/5 border border-white/10">
                  {p.product_id.startsWith("mock-") ? (
                    <div className="w-full h-full flex items-center justify-center">
                      <ShoppingBag className="w-6 h-6 text-white/15" />
                    </div>
                  ) : (
                    <img
                      src={getProductImageUrl(p.product_id)}
                      alt={p.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  )}
                </div>
                <p className="text-xs text-white/70 mt-1.5 line-clamp-2">
                  {p.title}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
