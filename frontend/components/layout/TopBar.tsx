"use client";

import { usePathname } from "next/navigation";

const TITLES: Record<string, string> = {
  "/feed": "Feed",
  "/shop": "Shop",
  "/cart": "Cart",
  "/upload": "Upload",
};

export function TopBar() {
  const pathname = usePathname();

  const isFeed = pathname === "/feed";

  const title =
    Object.entries(TITLES).find(([path]) =>
      pathname.startsWith(path)
    )?.[1] ?? "VibeShop";

  return (
    <header
      className={`sticky top-0 z-40 flex items-center h-12 md:h-14 px-4 md:px-6 border-b border-white/10 bg-black/90 backdrop-blur-lg ${
        isFeed ? "hidden md:flex" : ""
      }`}
    >
      <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
    </header>
  );
}
