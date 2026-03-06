"use client";

import { useCallback, useEffect, useRef } from "react";
import { logInteraction } from "@/lib/api-client";
import { useAppStore } from "@/store/app-store";

const MAX_LOOPS = 3;

export function useInteractionTracker(
  videoId: string | null,
  bucketName: string | null,
  isVisible: boolean,
  isPlaying?: boolean,
  durationMs?: number
) {
  const startTimeRef = useRef<number | null>(null);
  const addWatchedBucket = useAppStore((s) => s.addWatchedBucket);

  const report = useCallback(async () => {
    if (!videoId || !startTimeRef.current) return;
    let watchTimeMs = Date.now() - startTimeRef.current;
    if (watchTimeMs < 500) return;
    // Cap at 3 full loops worth of watch time
    if (durationMs && durationMs > 0) {
      watchTimeMs = Math.min(watchTimeMs, MAX_LOOPS * durationMs);
    }
    startTimeRef.current = null;
    try {
      await logInteraction(videoId, watchTimeMs);
    } catch {
      // silently fail interaction logging
    }
  }, [videoId, durationMs]);

  // Start the clock when video becomes visible; report total watch time when scrolled away
  useEffect(() => {
    if (isVisible && videoId && isPlaying !== false) {
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now();
      }
      if (bucketName) {
        addWatchedBucket(bucketName);
      }
      return () => {
        report();
      };
    } else {
      report();
    }
  }, [isVisible, videoId, bucketName, isPlaying, report, addWatchedBucket]);

  // Also flush on tab/app backgrounding
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) report();
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [report]);
}
