"use client";

import { useState, useCallback, useEffect } from "react";

interface RecommendationTracker {
  cycleCount: number;
  shouldShowSurvey: boolean;
  recommendationIds: string[];
  recordCycle: (videoIds: string[]) => void;
  recordPageVisit: () => void;
  resetCycle: () => void;
  setSurveyThreshold: (threshold: number) => void;
}

export function useRecommendationTracker(
  initialThreshold: number = 5
): RecommendationTracker {
  const [cycleCount, setCycleCount] = useState(0);
  const [threshold, setThreshold] = useState(initialThreshold);
  const [recommendationIds, setRecommendationIds] = useState<string[]>([]);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("rec_cycle_count");
    if (stored) {
      setCycleCount(parseInt(stored, 10));
    }

    const storedThreshold = localStorage.getItem("rec_survey_threshold");
    if (storedThreshold) {
      setThreshold(parseInt(storedThreshold, 10));
    }
  }, []);

  const recordPageVisit = useCallback(() => {
    setCycleCount((prev) => {
      const newCount = prev + 1;
      localStorage.setItem("rec_cycle_count", newCount.toString());
      return newCount;
    });
  }, []);

  // Track page visibility to count tab switches as recommendation cycles
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        recordPageVisit();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [recordPageVisit]);

  const recordCycle = useCallback(
    (videoIds: string[]) => {
      const newCount = cycleCount + 1;
      setCycleCount(newCount);
      setRecommendationIds(videoIds);
      localStorage.setItem("rec_cycle_count", newCount.toString());
      localStorage.setItem("rec_recommendation_ids", JSON.stringify(videoIds));
    },
    [cycleCount]
  );

  const resetCycle = useCallback(() => {
    setCycleCount(0);
    setRecommendationIds([]);
    localStorage.setItem("rec_cycle_count", "0");
    localStorage.removeItem("rec_recommendation_ids");
  }, []);

  const setSurveyThreshold = useCallback((newThreshold: number) => {
    setThreshold(newThreshold);
    localStorage.setItem("rec_survey_threshold", newThreshold.toString());
  }, []);

  return {
    cycleCount,
    shouldShowSurvey: cycleCount > 0 && cycleCount % threshold === 0,
    recommendationIds,
    recordCycle,
    recordPageVisit,
    resetCycle,
    setSurveyThreshold,
  };
}
