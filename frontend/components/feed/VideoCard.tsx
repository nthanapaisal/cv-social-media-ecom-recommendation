"use client";

import { useRef, useEffect, useState } from "react";
import { VideoPlayer } from "./VideoPlayer";
import { useInteractionTracker } from "@/hooks/use-interaction-tracker";
import { ShoppingBag } from "lucide-react";
import Link from "next/link";
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
    video.bucket_name || null,
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

      {/* Right side action buttons — TikTok style */}
      <div className="absolute right-3 bottom-28 md:bottom-20 z-20 flex flex-col items-center gap-5 pointer-events-auto">
        {video.bucket_name && (
          <Link
            href={`/shop?category=${video.bucket_name}`}
            className="flex flex-col items-center gap-1 text-white/80 hover:text-white transition-colors"
          >
            <div className="w-11 h-11 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/10">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-medium">Shop</span>
          </Link>
        )}
      </div>

      {/* Bottom caption overlay — always visible like TikTok/Instagram */}
      <div className="absolute bottom-0 left-0 right-0 z-20 pointer-events-none">
        <div className="bg-gradient-to-t from-black/70 via-black/30 to-transparent pt-20 pb-20 md:pb-6 px-4">
          <div className="pointer-events-auto max-w-[75%]">
            {/* Category hashtag */}
            {video.bucket_name && (
              <p className="text-white/70 text-xs font-semibold mb-1 drop-shadow-lg capitalize">
                #{video.bucket_name}
              </p>
            )}

            {/* Caption text */}
            {caption ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setCaptionExpanded((v) => !v);
                }}
                className="text-left"
              >
                <p
                  className={`text-white text-sm leading-snug drop-shadow-lg ${
                    captionExpanded ? "" : "line-clamp-2"
                  }`}
                >
                  {caption}
                </p>
                {!captionExpanded && caption.length > 60 && (
                  <span className="text-white/60 text-xs font-medium mt-0.5 inline-block">
                    ... more
                  </span>
                )}
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
