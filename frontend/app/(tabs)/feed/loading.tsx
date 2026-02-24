import { Loader2 } from "lucide-react";

export default function FeedLoading() {
  return (
    <div className="h-full flex items-center justify-center bg-black">
      <Loader2 className="w-8 h-8 text-white/40 animate-spin" />
    </div>
  );
}
