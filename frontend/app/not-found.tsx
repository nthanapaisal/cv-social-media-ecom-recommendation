import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-[100dvh] bg-background text-center px-8">
      <h1 className="text-6xl font-bold text-white/10 mb-2">404</h1>
      <p className="text-white/60 text-sm mb-6">
        This page doesn&apos;t exist or has been moved.
      </p>
      <Button asChild>
        <Link href="/feed">Back to Feed</Link>
      </Button>
    </div>
  );
}
