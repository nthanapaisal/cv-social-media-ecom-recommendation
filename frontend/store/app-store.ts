import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { CartItem, ProductMetadata } from "@/lib/types";

interface AppState {
  watchedBuckets: Record<string, number>;
  addWatchedBucket: (bucketName: string) => void;
  activeCategory: string | null;
  setActiveCategory: (category: string | null) => void;
  mutedGlobal: boolean;
  toggleMute: () => void;
  cart: CartItem[];
  addToCart: (product: ProductMetadata) => void;
  removeFromCart: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  cartCount: () => number;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      watchedBuckets: {},
      addWatchedBucket: (bucketName) =>
        set((state) => ({
          watchedBuckets: {
            ...state.watchedBuckets,
            [bucketName]: (state.watchedBuckets[bucketName] || 0) + 1,
          },
        })),

      activeCategory: null,
      setActiveCategory: (category) => set({ activeCategory: category }),

      mutedGlobal: true,
      toggleMute: () => set((state) => ({ mutedGlobal: !state.mutedGlobal })),

      cart: [],
      addToCart: (product) =>
        set((state) => {
          const existing = state.cart.find(
            (item) => item.product.product_id === product.product_id
          );
          if (existing) {
            return {
              cart: state.cart.map((item) =>
                item.product.product_id === product.product_id
                  ? { ...item, quantity: item.quantity + 1 }
                  : item
              ),
            };
          }
          return { cart: [...state.cart, { product, quantity: 1 }] };
        }),
      removeFromCart: (productId) =>
        set((state) => ({
          cart: state.cart.filter(
            (item) => item.product.product_id !== productId
          ),
        })),
      updateQuantity: (productId, quantity) =>
        set((state) => {
          if (quantity <= 0) {
            return {
              cart: state.cart.filter(
                (item) => item.product.product_id !== productId
              ),
            };
          }
          return {
            cart: state.cart.map((item) =>
              item.product.product_id === productId
                ? { ...item, quantity }
                : item
            ),
          };
        }),
      clearCart: () => set({ cart: [] }),
      cartCount: () =>
        get().cart.reduce((sum, item) => sum + item.quantity, 0),
    }),
    {
      name: "vibeshop-storage",
      partialize: (state) => ({ cart: state.cart, watchedBuckets: state.watchedBuckets }),
    }
  )
);
