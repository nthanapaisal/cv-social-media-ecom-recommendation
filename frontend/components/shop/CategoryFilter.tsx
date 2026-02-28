"use client";

import { PRODUCT_CATEGORIES } from "@/lib/types";
import { CATEGORY_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface CategoryFilterProps {
  selected: string | null;
  onSelect: (category: string | null) => void;
}

export function CategoryFilter({ selected, onSelect }: CategoryFilterProps) {
  return (
    <div className="max-w-7xl mx-auto flex gap-2 overflow-x-auto md:flex-wrap md:overflow-visible scrollbar-hide px-4 md:px-6 lg:px-8 py-3">
      <button
        onClick={() => onSelect(null)}
        className={cn(
          "flex-shrink-0 px-4 md:px-5 py-1.5 md:py-2 rounded-full text-xs md:text-sm font-medium transition-all",
          selected === null
            ? "bg-white text-black"
            : "bg-white/10 text-white/70 hover:bg-white/20"
        )}
      >
        All
      </button>
      {PRODUCT_CATEGORIES.map((cat) => {
        const isActive = selected === cat;
        return (
          <button
            key={cat}
            onClick={() => onSelect(isActive ? null : cat)}
            className={cn(
              "flex-shrink-0 px-4 md:px-5 py-1.5 md:py-2 rounded-full text-xs md:text-sm font-medium capitalize transition-all",
              isActive
                ? `${CATEGORY_COLORS[cat] || "bg-white/20"} text-white`
                : "bg-white/10 text-white/70 hover:bg-white/20"
            )}
          >
            {cat}
          </button>
        );
      })}
    </div>
  );
}
