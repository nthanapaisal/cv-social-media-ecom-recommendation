"use client";

import { useInfiniteQuery } from "@tanstack/react-query";
import { useCallback, useRef } from "react";
import { fetchFeed } from "@/lib/api-client";
import { FEED_PAGE_SIZE } from "@/lib/constants";
import type { VideoMetadata } from "@/lib/types";

export function useVideoFeed() {
  const seenIds = useRef(new Set<string>());

  const query = useInfiniteQuery({
    queryKey: ["video-feed"],
    queryFn: async () => {
      const videos = await fetchFeed(FEED_PAGE_SIZE);
      return videos.filter((v) => {
        if (seenIds.current.has(v.video_id)) return false;
        if (v.video_path.toLowerCase().endsWith(".avi")) return false;
        seenIds.current.add(v.video_id);
        return true;
      });
    },
    initialPageParam: 0,
    getNextPageParam: (_lastPage, allPages) => allPages.length,
    staleTime: 30_000,
    retry: 2,
  });

  const allVideos: VideoMetadata[] =
    query.data?.pages.flat() ?? [];

  const loadMore = useCallback(() => {
    if (!query.isFetchingNextPage && query.hasNextPage !== false) {
      query.fetchNextPage();
    }
  }, [query]);

  return {
    videos: allVideos,
    isLoading: query.isLoading,
    isError: query.isError,
    loadMore,
    isFetchingMore: query.isFetchingNextPage,
    refetch: query.refetch,
  };
}
