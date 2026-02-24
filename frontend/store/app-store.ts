import { create } from "zustand";

interface AppState {
  watchedBuckets: Record<string, number>;
  addWatchedBucket: (bucketName: string) => void;
  activeCategory: string | null;
  setActiveCategory: (category: string | null) => void;
  mutedGlobal: boolean;
  toggleMute: () => void;
}

export const useAppStore = create<AppState>((set) => ({
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
}));
