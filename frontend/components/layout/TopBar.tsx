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
    )?.[1] ?? "VibeShop";

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
      className={`sticky top-0 z-40 flex items-center justify-between h-12 md:h-14 px-4 md:px-6 border-b border-white/10 bg-black/90 backdrop-blur-lg ${
        isFeed ? "hidden md:flex" : ""
      }`}
    >
      <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
      {isShop && (
        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="shrink-0 text-white/50 hover:text-white h-8 w-8"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
        </Button>
      )}
    </header>
  );
}
