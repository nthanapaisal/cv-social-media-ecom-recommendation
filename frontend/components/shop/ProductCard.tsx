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
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 28 }}
    >
      <Link
        href={`/shop/${product.product_id}`}
        className="group block rounded-2xl p-1 -m-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/40 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
      >
        <div className="relative aspect-square overflow-hidden rounded-2xl bg-white/[0.03] ring-1 ring-white/[0.06] transition-[box-shadow,ring-color] duration-300 group-hover:ring-violet-500/25 group-hover:shadow-lg group-hover:shadow-violet-500/5">
          <Image
            src={getProductImageUrl(product.product_id)}
            alt={product.title}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
            className="object-cover transition-transform duration-500 ease-out group-hover:scale-[1.04]"
          />
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        </div>
        <div className="mt-3 px-0.5">
          <p className="text-sm font-medium leading-snug text-white/90 line-clamp-2 tracking-tight">
            {product.title}
          </p>
          {product.price != null && (
            <p className="mt-1.5 text-sm font-semibold tabular-nums tracking-tight text-white/75">
              ${product.price.toFixed(2)}
            </p>
          )}
          <p className="mt-1 text-[11px] leading-relaxed text-white/30 line-clamp-2 md:line-clamp-1">
            {product.product_details}
          </p>
        </div>
      </Link>
    </motion.div>
  );
}
