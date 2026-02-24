"use client";

import { useRef, useEffect, useState } from "react";
import { VideoPlayer } from "./VideoPlayer";
import { useInteractionTracker } from "@/hooks/use-interaction-tracker";
import { Badge } from "@/components/ui/badge";
import { CATEGORY_COLORS } from "@/lib/constants";
import { ShoppingBag } from "lucide-react";
import Link from "next/link";
import type { VideoMetadata } from "@/lib/types";

interface VideoCardProps {
  video: VideoMetadata;
  onVisible?: () => void;
}

export function VideoCard({ video, onVisible }: VideoCardProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const visible = entry.isIntersecting && entry.intersectionRatio >= 0.75;
        setIsVisible(visible);
        if (visible) onVisible?.();
      },
      { threshold: [0.75] }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [onVisible]);

  useInteractionTracker(
    isVisible ? video.video_id : null,
    video.bucket_name,
    isVisible
  );

  const colorClass = CATEGORY_COLORS[video.bucket_name] || CATEGORY_COLORS.other;

  return (
    <div
      ref={containerRef}
      className="relative w-full h-[100dvh] snap-start snap-always flex-shrink-0"
    >
      <VideoPlayer videoId={video.video_id} isActive={isVisible} />

      <div className="absolute bottom-0 left-0 right-0 p-4 pb-20 bg-gradient-to-t from-black/80 via-black/40 to-transparent pointer-events-none">
        <div className="pointer-events-auto max-w-[80%]">
          <p className="text-white text-sm font-medium leading-snug mb-2 line-clamp-3">
            {video.caption}
          </p>
          <Badge
            variant="secondary"
            className={`${colorClass} text-white border-0 text-xs`}
          >
            {video.bucket_name}
          </Badge>
        </div>
      </div>

      <div className="absolute right-3 bottom-28 flex flex-col items-center gap-4 pointer-events-auto">
        <Link
          href={`/shop?category=${video.bucket_name}`}
          className="flex flex-col items-center gap-1 text-white/80 hover:text-white transition-colors"
        >
          <div className="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <span className="text-[10px]">Shop</span>
        </Link>
      </div>
    </div>
  );
}
