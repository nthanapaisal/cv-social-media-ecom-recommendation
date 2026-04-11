"use client";

import { useRef, useEffect, useState } from "react";
import { VideoPlayer } from "./VideoPlayer";
import { useInteractionTracker } from "@/hooks/use-interaction-tracker";
import type { VideoMetadata } from "@/lib/types";

interface VideoCardProps {
  video: VideoMetadata;
  onVisible?: () => void;
}

export function VideoCard({ video, onVisible }: VideoCardProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const watched50PctRef = useRef(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [captionExpanded, setCaptionExpanded] = useState(false);
  const caption = (video.caption ?? "").trim();

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting && entry.intersectionRatio >= 0.75;
        setIsVisible(visible);
        if (visible) {
          watched50PctRef.current = false;
          onVisible?.();
        }
      },
      { threshold: [0.75] },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [onVisible]);

  useInteractionTracker(
    isVisible ? video.video_id : null,
    video.bucket_name?.[0] || null,
    isVisible,
    isPlaying,
    video.duration_ms,
    watched50PctRef,
  );

  return (
    <div
      ref={containerRef}
      className="relative isolate w-full h-[100dvh] md:h-full snap-start snap-always flex-shrink-0"
    >
      <VideoPlayer
        videoId={video.video_id}
        isActive={isVisible}
        onPlayStateChange={setIsPlaying}
        onWatched50Percent={() => {
          watched50PctRef.current = true;
        }}
      />

      {caption ? (
        <div className="absolute bottom-0 left-0 right-0 z-20 pointer-events-none">
          <div className="bg-gradient-to-t from-black/80 via-black/40 to-transparent pt-24 pb-20 md:pb-6 px-4">
            <div className="pointer-events-auto max-w-[80%]">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setCaptionExpanded((v) => !v);
                }}
                className="text-left"
              >
                <p
                  className={`text-white/95 text-sm leading-relaxed drop-shadow-lg ${
                    captionExpanded ? "" : "line-clamp-2"
                  }`}
                >
                  {caption}
                </p>
                {!captionExpanded && caption.length > 60 && (
                  <span className="text-white/50 text-xs font-medium mt-0.5 inline-block">
                    ... more
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
