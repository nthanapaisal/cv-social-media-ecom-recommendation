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

export function BottomNav() {
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
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/10 bg-black/90 backdrop-blur-lg pb-[env(safe-area-inset-bottom)] md:hidden">
      <div className="flex items-center justify-around h-14 max-w-lg mx-auto relative">
        {activeIndex >= 0 && (
          <motion.div
            className="absolute top-0 h-0.5 bg-white rounded-full"
            style={{ width: `${100 / tabs.length}%` }}
            animate={{ left: `${(activeIndex * 100) / tabs.length}%` }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
          />
        )}
        {tabs.map((tab) => {
          const isActive =
            pathname === tab.href ||
            pathname.startsWith(tab.href + "/");
          const Icon = tab.icon;
          const showBadge = mounted && tab.href === "/cart" && cartCount > 0;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`relative flex flex-col items-center justify-center gap-0.5 flex-1 h-full transition-colors ${
                isActive
                  ? "text-white"
                  : "text-white/50 hover:text-white/70"
              }`}
            >
              <div className="relative">
                <Icon className="w-5 h-5" strokeWidth={isActive ? 2.5 : 2} />
                {showBadge && (
                  <span className="absolute -top-1.5 -right-2.5 min-w-[16px] h-4 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center px-1">
                    {cartCount > 99 ? "99+" : cartCount}
                  </span>
                )}
              </div>
              <span className="text-[10px] font-medium">{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
