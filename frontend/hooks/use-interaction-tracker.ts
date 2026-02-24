"use client";

import { useCallback, useEffect, useRef } from "react";
import { logInteraction } from "@/lib/api-client";
import { useAppStore } from "@/store/app-store";

const REPORT_INTERVAL_MS = 3000;

export function useInteractionTracker(
  videoId: string | null,
  bucketName: string | null,
  isVisible: boolean
) {
  const startTimeRef = useRef<number | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const addWatchedBucket = useAppStore((s) => s.addWatchedBucket);

  const report = useCallback(async () => {
    if (!videoId || !startTimeRef.current) return;
    const watchTimeMs = Date.now() - startTimeRef.current;
    if (watchTimeMs < 500) return;
    try {
      await logInteraction(videoId, watchTimeMs);
    } catch {
      // silently fail interaction logging
    }
  }, [videoId]);

  useEffect(() => {
    if (isVisible && videoId) {
      startTimeRef.current = Date.now();

      if (bucketName) {
        addWatchedBucket(bucketName);
      }

      intervalRef.current = setInterval(report, REPORT_INTERVAL_MS);

      return () => {
        report();
        if (intervalRef.current) clearInterval(intervalRef.current);
        startTimeRef.current = null;
      };
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (startTimeRef.current) {
        report();
        startTimeRef.current = null;
      }
    }
  }, [isVisible, videoId, bucketName, report, addWatchedBucket]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && startTimeRef.current) {
        report();
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [report]);
}
