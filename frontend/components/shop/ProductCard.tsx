"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { getProductImageUrl } from "@/lib/api-client";
import { ShoppingBag } from "lucide-react";
import type { ProductMetadata } from "@/lib/types";

interface ProductCardProps {
  product: ProductMetadata;
}

export function ProductCard({ product }: ProductCardProps) {
  const isMock = product.product_id.startsWith("mock-");

  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
    <Link href={`/shop/${product.product_id}`} className="group block">
      <div className="relative aspect-square rounded-xl md:rounded-2xl overflow-hidden bg-white/5 border border-white/10">
        {isMock ? (
          <div className="w-full h-full flex flex-col items-center justify-center gap-2 bg-gradient-to-br from-white/5 to-white/10">
            <ShoppingBag className="w-8 h-8 text-white/20" />
            <span className="text-[10px] text-white/30 capitalize">
              {product.bucket_name}
            </span>
          </div>
        ) : (
          <img
            src={getProductImageUrl(product.product_id)}
            alt={product.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        )}
      </div>
      <div className="mt-2 md:mt-3 px-0.5">
        <p className="text-sm font-medium text-white/90 line-clamp-2 leading-tight">
          {product.title}
        </p>
        <p className="text-xs text-white/40 mt-0.5 line-clamp-1">
          {product.product_details}
        </p>
      </div>
    </Link>
    </motion.div>
  );
}
