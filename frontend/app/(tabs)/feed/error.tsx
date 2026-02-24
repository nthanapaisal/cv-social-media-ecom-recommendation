"use client";

import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function FeedError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="h-full flex items-center justify-center bg-black">
      <div className="flex flex-col items-center gap-4 text-center px-8">
        <AlertCircle className="w-12 h-12 text-red-400/60" />
        <p className="text-white/60 text-sm">Failed to load the video feed</p>
        <Button variant="secondary" size="sm" onClick={reset}>
          Try Again
        </Button>
      </div>
    </div>
  );
}
