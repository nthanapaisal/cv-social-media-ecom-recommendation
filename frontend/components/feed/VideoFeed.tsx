"use client";

import { useCallback, useRef, useEffect } from "react";
import { useVideoFeed } from "@/hooks/use-video-feed";
import { VideoCard } from "./VideoCard";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, VideoOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function VideoFeed() {
  const { videos, isLoading, isError, loadMore, isFetchingMore, refetch } =
    useVideoFeed();
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) loadMore();
      },
      { rootMargin: "200%" }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [loadMore]);

  const handleCardVisible = useCallback(
    (index: number) => {
      if (index >= videos.length - 2) {
        loadMore();
      }
    },
    [videos.length, loadMore]
  );

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:bg-zinc-950">
        <div className="w-full h-full md:max-w-[480px] md:mx-auto md:border-x md:border-white/10 flex items-center justify-center bg-black">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-8 h-8 text-white/60 animate-spin" />
            <p className="text-white/40 text-sm">Loading feed...</p>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:bg-zinc-950">
        <div className="w-full h-full md:max-w-[480px] md:mx-auto md:border-x md:border-white/10 flex items-center justify-center bg-black">
          <div className="flex flex-col items-center gap-4 text-center px-8">
            <p className="text-white/60 text-sm">
              Something went wrong loading the feed.
            </p>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:bg-zinc-950">
        <div className="w-full h-full md:max-w-[480px] md:mx-auto md:border-x md:border-white/10 flex items-center justify-center bg-black">
          <div className="flex flex-col items-center gap-4 text-center px-8">
            <VideoOff className="w-12 h-12 text-white/30" />
            <p className="text-white/60 text-sm">No videos yet</p>
            <p className="text-white/40 text-xs">
              Be the first to upload a video!
            </p>
            <Button variant="secondary" size="sm" asChild>
              <Link href="/upload/video">Upload Video</Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-black md:bg-zinc-950 md:flex md:justify-center">
      <div className="h-full w-full md:max-w-[480px] md:border-x md:border-white/10 overflow-y-scroll snap-y snap-mandatory scrollbar-hide">
        {videos.map((video, index) => (
          <VideoCard
            key={video.video_id}
            video={video}
            onVisible={() => handleCardVisible(index)}
          />
        ))}
        <div ref={sentinelRef} className="h-1" />
        {isFetchingMore && (
          <div className="flex justify-center py-4">
            <Loader2 className="w-6 h-6 text-white/40 animate-spin" />
          </div>
        )}
      </div>
    </div>
  );
}
