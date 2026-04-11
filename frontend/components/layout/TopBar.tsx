"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { refreshShop } from "@/lib/api-client";
import { RefreshCw } from "lucide-react";

const TITLES: Record<string, string> = {
  "/feed": "Feed",
  "/shop": "Shop",
  "/cart": "Cart",
  "/upload": "Upload",
};

export function TopBar() {
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const isFeed = pathname === "/feed";
  const isShop = pathname === "/shop" || pathname.startsWith("/shop/");

  const title =
    Object.entries(TITLES).find(([path]) =>
      pathname.startsWith(path)
    )?.[1] ?? "VisCart";

  const handleRefresh = async () => {
    if (!isShop) return;
    setIsRefreshing(true);
    try {
      await refreshShop();
      await queryClient.invalidateQueries({ queryKey: ["shop-products"] });
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <header
      className={`sticky top-0 z-40 flex items-center justify-between h-12 md:h-14 px-4 md:px-6 border-b border-white/[0.06] bg-black/95 backdrop-blur-xl ${
        isFeed ? "hidden md:flex" : ""
      }`}
    >
      <h1 className="text-base font-semibold tracking-tight text-white/90">{title}</h1>
      {isShop && (
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="shrink-0 text-white/40 hover:text-white h-8 w-8"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
        </Button>
      )}
    </header>
  );
}
