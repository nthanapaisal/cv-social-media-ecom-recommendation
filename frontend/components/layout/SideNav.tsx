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
    <nav className="hidden md:flex fixed left-0 top-0 bottom-0 z-50 w-20 lg:w-60 flex-col border-r border-white/[0.06] bg-black/95 backdrop-blur-xl">
      <div className="flex h-16 w-full items-center justify-center lg:justify-start lg:px-5">
        <Link href="/feed" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-sm font-bold shadow-lg shadow-violet-500/20">
            V
          </div>
          <span className="hidden lg:inline text-lg font-bold tracking-tight bg-gradient-to-r from-white to-white/70 bg-clip-text text-transparent">
            VisCart
          </span>
        </Link>
      </div>

      <div className="flex flex-col gap-0.5 px-3 mt-6 relative">
        {activeIndex >= 0 && (
          <motion.div
            className="absolute left-0 w-[3px] h-10 bg-gradient-to-b from-violet-400 to-fuchsia-400 rounded-full"
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
              className={`flex items-center justify-center lg:justify-start gap-3 h-10 rounded-lg px-3 transition-all duration-200 ${
                isActive
                  ? "text-white bg-white/[0.08]"
                  : "text-white/40 hover:text-white/70 hover:bg-white/[0.04]"
              }`}
            >
              <div className="relative shrink-0">
                <Icon
                  className="w-5 h-5"
                  strokeWidth={isActive ? 2.5 : 1.75}
                />
                {showBadge && (
                  <span className="absolute -top-1.5 -right-2.5 min-w-[16px] h-4 rounded-full bg-violet-500 text-white text-[10px] font-bold flex items-center justify-center px-1 shadow-lg shadow-violet-500/30">
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
