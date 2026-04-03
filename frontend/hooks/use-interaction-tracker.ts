"use client";

import { useCallback, useEffect, useRef, type RefObject } from "react";
import { logInteraction } from "@/lib/api-client";
import { useAppStore } from "@/store/app-store";

const MAX_LOOPS = 3;
const SKIP_THRESHOLD_MS = 3000;

export function useInteractionTracker(
  videoId: string | null,
  bucketName: string | null,
  isVisible: boolean,
  isPlaying?: boolean,
  durationMs?: number,
  watched50PctRef?: RefObject<boolean>,
) {
  const startTimeRef = useRef<number | null>(null);
  const sessionVideoIdRef = useRef<string | null>(null);
  const sessionDurationMsRef = useRef<number | undefined>(durationMs);
  const prevShouldTrackRef = useRef(false);
  const prevVideoIdRef = useRef<string | null>(videoId);
  const addWatchedBucket = useAppStore((s) => s.addWatchedBucket);

  const report = useCallback(async (markQuickSkip = false) => {
    const sessionVideoId = sessionVideoIdRef.current;
    const sessionDurationMs = sessionDurationMsRef.current;

    if (!sessionVideoId || !startTimeRef.current) return;
    let watchTimeMs = Date.now() - startTimeRef.current;
    const skippedQuickly = markQuickSkip && watchTimeMs < SKIP_THRESHOLD_MS;

    if (watchTimeMs < 500 && !skippedQuickly) {
      startTimeRef.current = null;
      sessionVideoIdRef.current = null;
      sessionDurationMsRef.current = undefined;
      return;
    }

    if (sessionDurationMs && sessionDurationMs > 0) {
      watchTimeMs = Math.min(watchTimeMs, MAX_LOOPS * sessionDurationMs);
    }

    startTimeRef.current = null;
    sessionVideoIdRef.current = null;
    sessionDurationMsRef.current = undefined;

    try {
      await logInteraction(sessionVideoId, watchTimeMs, {
        skipped_quickly: skippedQuickly,
        watched_50_pct: watched50PctRef?.current ?? false,
      });
    } catch {
      // silently fail interaction logging
    }
  }, [watched50PctRef]);

  useEffect(() => {
    const shouldTrack = Boolean(isVisible && videoId && isPlaying !== false);
    const wasTracking = prevShouldTrackRef.current;
    const previousVideoId = prevVideoIdRef.current;
    const changedVideo = wasTracking && previousVideoId !== videoId;

    if (wasTracking && (!shouldTrack || changedVideo)) {
      report(!isVisible || changedVideo || !videoId);
    }

    if (shouldTrack && (!wasTracking || changedVideo)) {
      if (!startTimeRef.current && videoId) {
        startTimeRef.current = Date.now();
        sessionVideoIdRef.current = videoId;
        sessionDurationMsRef.current = durationMs;
      }
      if (bucketName) {
        addWatchedBucket(bucketName);
      }
    }

    prevShouldTrackRef.current = shouldTrack;
    prevVideoIdRef.current = videoId;
  }, [isVisible, videoId, bucketName, isPlaying, durationMs, report, addWatchedBucket]);

  // Also flush on tab/app backgrounding
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) report();
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [report]);

  useEffect(() => {
    return () => {
      report(false);
    };
  }, [report]);
}
