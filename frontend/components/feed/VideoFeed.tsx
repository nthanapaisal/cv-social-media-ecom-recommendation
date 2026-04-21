"use client";

import { useCallback, useRef, useEffect, useState, useMemo } from "react";
import { useVideoFeed } from "@/hooks/use-video-feed";
import { useRecommendationTracker } from "@/hooks/use-recommendation-tracker";
import { SurveyModal } from "@/components/ui/survey-modal";
import { VideoCard } from "./VideoCard";
import { Loader2, VideoOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const SURVEY_THRESHOLD = 5; // Show survey every 5 loadMore calls

export function VideoFeed() {
  const { videos, isLoading, isError, loadMore, isFetchingMore, refetch } =
    useVideoFeed();
  const sentinelRef = useRef<HTMLDivElement>(null);
  const [showSurvey, setShowSurvey] = useState(false);
  const [userId] = useState(() => {
    // Generate or retrieve user ID (stored in localStorage)
    if (typeof window === "undefined") return "unknown";
    const stored = localStorage.getItem("user_id");
    if (stored) return stored;
    const newId = `user_${Date.now()}`;
    localStorage.setItem("user_id", newId);
    return newId;
  });

  const tracker = useRecommendationTracker(SURVEY_THRESHOLD);

  // Generate a unique ID for this recommendation batch  
  const currentRecommendationId = useMemo(() => {
    return `rec_${tracker.cycleCount}_${Date.now()}`;
  }, [tracker.cycleCount]);

  // Extract current video IDs being displayed
  const currentVideoIds = useMemo(() => {
    return videos.map((v) => v.video_id);
  }, [videos]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          loadMore();
          // Record this recommendation cycle
          tracker.recordCycle(currentVideoIds);
        }
      },
      { rootMargin: "200%" }
    );

    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [loadMore, tracker, currentVideoIds]);

  // Show survey when threshold is reached
  useEffect(() => {
    if (tracker.shouldShowSurvey) {
      setShowSurvey(true);
    }
  }, [tracker.shouldShowSurvey]);

  const handleCardVisible = useCallback(
    (index: number) => {
      if (index >= videos.length - 2) {
        loadMore();
      }
    },
    [videos.length, loadMore]
  );

  const handleSurveySubmit = () => {
    tracker.resetCycle();
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:py-3">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 text-white/50 animate-spin" />
          <p className="text-white/35 text-sm">Loading feed...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:py-3">
        <div className="flex flex-col items-center gap-4 text-center px-8">
          <p className="text-white/50 text-sm">
            Something went wrong loading the feed.
          </p>
          <Button variant="secondary" size="sm" onClick={() => refetch()}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="h-full flex items-center justify-center bg-black md:py-3">
        <div className="flex flex-col items-center gap-4 text-center px-8">
          <VideoOff className="w-12 h-12 text-white/20" />
          <p className="text-white/50 text-sm">No videos yet</p>
          <p className="text-white/35 text-xs">
            Be the first to upload a video!
          </p>
          <Button variant="secondary" size="sm" asChild>
            <Link href="/upload/video">Upload Video</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full min-h-0 bg-black md:flex md:items-center md:justify-center md:py-3">
      <SurveyModal
        open={showSurvey}
        onOpenChange={setShowSurvey}
        userId={userId}
        recommendationId={currentRecommendationId}
        itemsShown={tracker.recommendationIds}
        onSubmit={handleSurveySubmit}
      />
      {/* Desktop: md:py-3 inset; width uses usable height (viewport − top bar − vertical inset) × 9/16 */}
      <div className="h-full w-full md:h-auto md:w-[min(100%,calc((100dvh-3.5rem-1.5rem)*9/16))] md:aspect-[9/16] md:rounded-2xl md:border md:border-white/[0.06] md:overflow-hidden flex-shrink-0">
        <div className="h-full overflow-y-scroll snap-y snap-mandatory scrollbar-hide">
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
              <Loader2 className="w-6 h-6 text-white/30 animate-spin" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
