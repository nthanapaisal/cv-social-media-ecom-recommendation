"use client";

import { useAppStore } from "@/store/app-store";
import { getProductImageUrl } from "@/lib/api-client";
import { CATEGORY_COLORS } from "@/lib/constants";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageTransition } from "@/components/layout/PageTransition";
import {
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  ShoppingBag,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function CartPage() {
  const cart = useAppStore((s) => s.cart);
  const removeFromCart = useAppStore((s) => s.removeFromCart);
  const updateQuantity = useAppStore((s) => s.updateQuantity);
  const clearCart = useAppStore((s) => s.clearCart);
  const totalItems = useAppStore((s) => s.cartCount());

  if (cart.length === 0) {
    return (
      <PageTransition>
        <div className="h-full flex items-center justify-center">
          <div className="flex flex-col items-center gap-4 text-center px-8">
            <ShoppingCart className="w-16 h-16 text-white/20" />
            <div>
              <p className="text-white/60 text-lg font-medium">
                Your cart is empty
              </p>
              <p className="text-white/40 text-sm mt-1">
                Browse the shop and add some products!
              </p>
            </div>
            <Button variant="secondary" asChild>
              <Link href="/shop">
                <ShoppingBag className="w-4 h-4 mr-2" />
                Browse Shop
              </Link>
            </Button>
          </div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="h-full overflow-y-auto scrollbar-hide pb-24 md:pb-8">
        <div className="max-w-3xl mx-auto p-4 md:p-6 lg:p-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl md:text-2xl font-bold">Cart</h1>
              <p className="text-sm text-white/50 mt-0.5">
                {totalItems} {totalItems === 1 ? "item" : "items"}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="text-white/50 hover:text-red-400"
              onClick={() => {
                clearCart();
                toast.success("Cart cleared");
              }}
            >
              <Trash2 className="w-4 h-4 mr-1.5" />
              Clear
            </Button>
          </div>

          <div className="space-y-3">
            {cart.map((item) => {
              const isMock = item.product.product_id.startsWith("mock-");
              const colorClass =
                CATEGORY_COLORS[item.product.bucket_name] ||
                CATEGORY_COLORS.other;

              return (
                <div
                  key={item.product.product_id}
                  className="flex gap-4 p-3 md:p-4 rounded-xl bg-white/5 border border-white/10"
                >
                  <Link
                    href={`/shop/${item.product.product_id}`}
                    className="shrink-0"
                  >
                    <div className="w-20 h-20 md:w-24 md:h-24 rounded-lg overflow-hidden bg-white/5">
                      {isMock ? (
                        <div className="w-full h-full flex items-center justify-center">
                          <ShoppingBag className="w-6 h-6 text-white/15" />
                        </div>
                      ) : (
                        <img
                          src={getProductImageUrl(item.product.product_id)}
                          alt={item.product.title}
                          className="w-full h-full object-cover"
                        />
                      )}
                    </div>
                  </Link>

                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                      <Link
                        href={`/shop/${item.product.product_id}`}
                        className="hover:underline"
                      >
                        <p className="text-sm font-medium text-white/90 line-clamp-2 leading-tight">
                          {item.product.title}
                        </p>
                      </Link>
                      <Badge
                        variant="secondary"
                        className={`${colorClass} text-white border-0 text-[10px] mt-1.5 capitalize`}
                      >
                        {item.product.bucket_name}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() =>
                            updateQuantity(
                              item.product.product_id,
                              item.quantity - 1
                            )
                          }
                          className="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="w-8 text-center text-sm font-medium tabular-nums">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() =>
                            updateQuantity(
                              item.product.product_id,
                              item.quantity + 1
                            )
                          }
                          className="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <button
                        onClick={() => {
                          removeFromCart(item.product.product_id);
                          toast.success("Removed from cart");
                        }}
                        className="p-1.5 rounded-md text-white/40 hover:text-red-400 hover:bg-white/10 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex flex-col gap-3 pt-2">
            <Button size="lg" className="w-full" disabled>
              Checkout
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <p className="text-xs text-white/30 text-center">
              Checkout is not yet available
            </p>
            <Button variant="secondary" size="sm" className="w-full" asChild>
              <Link href="/shop">Continue Shopping</Link>
            </Button>
          </div>
        </div>
      </div>
    </PageTransition>
  );
}
