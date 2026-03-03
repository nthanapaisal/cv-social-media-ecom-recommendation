"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import { getProductImageUrl } from "@/lib/api-client";
import type { ProductMetadata } from "@/lib/types";

interface ProductCardProps {
  product: ProductMetadata;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
    <Link href={`/shop/${product.product_id}`} className="group block">
      <div className="relative aspect-square rounded-xl md:rounded-2xl overflow-hidden bg-white/5 border border-white/10">
        <Image
          src={getProductImageUrl(product.product_id)}
          alt={product.title}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div className="mt-2 md:mt-3 px-0.5">
        <p className="text-sm font-medium text-white/90 line-clamp-2 leading-tight">
          {product.title}
        </p>
        {product.price != null && (
          <p className="text-sm font-semibold text-white/80 mt-1">
            ${product.price.toFixed(2)}
          </p>
        )}
        <p className="text-xs text-white/40 mt-0.5 line-clamp-1">
          {product.product_details}
        </p>
      </div>
    </Link>
    </motion.div>
  );
}
