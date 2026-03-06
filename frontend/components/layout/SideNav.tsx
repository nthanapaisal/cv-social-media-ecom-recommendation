"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSyncExternalStore } from "react";
import { motion } from "framer-motion";
import { Play, ShoppingBag, PlusCircle, ShoppingCart } from "lucide-react";
import { useAppStore } from "@/store/app-store";

const tabs = [
  { href: "/feed", label: "Feed", icon: Play },
  { href: "/shop", label: "Shop", icon: ShoppingBag },
  { href: "/cart", label: "Cart", icon: ShoppingCart },
  { href: "/upload", label: "Upload", icon: PlusCircle },
] as const;

export function SideNav() {
  const pathname = usePathname();
  const cartCount = useAppStore((s) => s.cartCount());
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  const activeIndex = tabs.findIndex(
    (tab) => pathname === tab.href || pathname.startsWith(tab.href + "/")
  );

  return (
    <nav className="hidden md:flex fixed left-0 top-0 bottom-0 z-50 w-20 lg:w-64 flex-col border-r border-white/10 bg-black/90 backdrop-blur-lg">
      <div className="flex items-center h-16 px-4 lg:px-6">
        <span className="text-xl font-bold tracking-tight">
          <span className="hidden lg:inline">VibeShop</span>
          <span className="lg:hidden">V</span>
        </span>
      </div>

      <div className="flex flex-col gap-1 px-3 mt-4 relative">
        {activeIndex >= 0 && (
          <motion.div
            className="absolute left-0 w-0.5 h-10 bg-white rounded-full"
            animate={{ top: activeIndex * 44 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
          />
        )}
        {tabs.map((tab) => {
          const isActive =
            pathname === tab.href || pathname.startsWith(tab.href + "/");
          const Icon = tab.icon;
          const showBadge = mounted && tab.href === "/cart" && cartCount > 0;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`flex items-center justify-center lg:justify-start gap-3 h-10 rounded-lg px-3 transition-colors ${
                isActive
                  ? "text-white bg-white/10"
                  : "text-white/50 hover:text-white/70 hover:bg-white/5"
              }`}
            >
              <div className="relative shrink-0">
                <Icon
                  className="w-5 h-5"
                  strokeWidth={isActive ? 2.5 : 2}
                />
                {showBadge && (
                  <span className="absolute -top-1.5 -right-2.5 min-w-[16px] h-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1">
                    {cartCount > 99 ? "99+" : cartCount}
                  </span>
                )}
              </div>
              <span className="hidden lg:inline text-sm font-medium">
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
