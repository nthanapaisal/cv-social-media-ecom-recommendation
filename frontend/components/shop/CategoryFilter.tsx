"use client";

import { PRODUCT_CATEGORIES } from "@/lib/types";
import { CATEGORY_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface CategoryFilterProps {
  selected: string | null;
  onSelect: (category: string | null) => void;
}

const chipBase =
  "flex-shrink-0 rounded-full text-xs md:text-sm font-medium capitalize transition-all duration-200 outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-black";

export function CategoryFilter({ selected, onSelect }: CategoryFilterProps) {
  return (
    <div className="sticky top-0 z-10 border-b border-white/[0.06] bg-black/80 backdrop-blur-xl supports-[backdrop-filter]:bg-black/60">
      <div className="max-w-7xl mx-auto flex gap-2 overflow-x-auto md:flex-wrap md:overflow-visible scrollbar-hide px-4 md:px-6 lg:px-8 py-3 md:py-4">
        <button
          type="button"
          onClick={() => onSelect(null)}
          className={cn(
            chipBase,
            "px-4 md:px-5 py-2 md:py-2.5",
            selected === null
              ? "bg-white text-black shadow-md shadow-black/20 ring-1 ring-white/20"
              : "bg-white/[0.05] text-white/50 hover:bg-white/[0.1] hover:text-white/75 ring-1 ring-transparent hover:ring-white/[0.08]"
          )}
        >
          All
        </button>
        {PRODUCT_CATEGORIES.map((cat) => {
          const isActive = selected === cat;
          return (
            <button
              type="button"
              key={cat}
              onClick={() => onSelect(isActive ? null : cat)}
              className={cn(
                chipBase,
                "px-4 md:px-5 py-2 md:py-2.5",
                isActive
                  ? `${CATEGORY_COLORS[cat] || "bg-white/20"} text-white shadow-md shadow-black/25 ring-1 ring-white/15`
                  : "bg-white/[0.05] text-white/50 hover:bg-white/[0.1] hover:text-white/75 ring-1 ring-transparent hover:ring-white/[0.08]"
              )}
            >
              {cat}
            </button>
          );
        })}
      </div>
    </div>
  );
}
