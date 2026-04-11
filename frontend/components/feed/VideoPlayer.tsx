"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { getVideoUrl } from "@/lib/api-client";
import { useAppStore } from "@/store/app-store";
import { Volume2, VolumeX, Play, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface VideoPlayerProps {
  videoId: string;
  isActive: boolean;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onWatched50Percent?: () => void;
  onCurrentTimeMs?: (ms: number) => void;
}

export function VideoPlayer({
  videoId,
  isActive,
  onPlayStateChange,
  onWatched50Percent,
  onCurrentTimeMs,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showPlayIcon, setShowPlayIcon] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const watched50Ref = useRef(false);
  const muted = useAppStore((s) => s.mutedGlobal);
  const toggleMute = useAppStore((s) => s.toggleMute);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isActive) {
      watched50Ref.current = false;
      video.play().catch((error) => {
        if (error.name === "NotAllowedError") {
          toast("Tap to play video", {
            description: "Autoplay is disabled for this video",
            duration: 2000,
          });
        }
      });
    } else {
      video.pause();
      video.currentTime = 0;
    }
  }, [isActive]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    video.muted = muted;
  }, [muted]);

  useEffect(() => {
    onPlayStateChange?.(isPlaying);
  }, [isPlaying, onPlayStateChange]);

  const handleTap = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    if (video.paused) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
    setShowPlayIcon(true);
    setTimeout(() => setShowPlayIcon(false), 600);
  }, []);

  return (
    <div className="relative w-full h-full bg-black" onClick={handleTap}>
      <video
        ref={videoRef}
        src={getVideoUrl(videoId)}
        className="w-full h-full object-contain"
        loop
        playsInline
        muted={muted}
        preload={isActive ? "auto" : "metadata"}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onWaiting={() => setIsBuffering(true)}
        onPlaying={() => setIsBuffering(false)}
        onTimeUpdate={(e) => {
          const video = e.currentTarget;
          if (!video.duration) return;
          onCurrentTimeMs?.(video.currentTime * 1000);
          if (!watched50Ref.current && video.currentTime / video.duration >= 0.5) {
            watched50Ref.current = true;
            onWatched50Percent?.();
          }
        }}
      />

      {isBuffering && isActive && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <Loader2 className="w-10 h-10 text-white/70 animate-spin" />
        </div>
      )}

      {showPlayIcon && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-black/40 rounded-full p-4 animate-ping-once">
            <Play
              className={`w-12 h-12 text-white ${isPlaying ? "hidden" : ""}`}
              fill="white"
            />
          </div>
        </div>
      )}

      <button
        onClick={(e) => {
          e.stopPropagation();
          toggleMute();
        }}
        className="absolute top-4 right-4 p-2.5 rounded-full bg-black/30 backdrop-blur-md text-white/70 hover:text-white hover:bg-black/50 transition-all duration-200 z-10 border border-white/[0.06]"
        aria-label={muted ? "Unmute" : "Mute"}
      >
        {muted ? (
          <VolumeX className="w-4 h-4" />
        ) : (
          <Volume2 className="w-4 h-4" />
        )}
      </button>

      {!isPlaying && !isBuffering && isActive && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-16 h-16 rounded-full bg-black/20 backdrop-blur-sm flex items-center justify-center">
            <Play
              className="w-8 h-8 text-white/70 ml-1"
              fill="white"
              fillOpacity={0.7}
            />
          </div>
        </div>
      )}
    </div>
  );
}
