"use client";

import { VideoUploadForm } from "@/components/upload/VideoUploadForm";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function VideoUploadPage() {
  return (
    <div>
      <div className="sticky top-0 z-10 flex items-center gap-3 p-3 bg-black/80 backdrop-blur-lg border-b border-white/10">
        <Button variant="ghost" size="icon" asChild className="shrink-0">
          <Link href="/upload">
            <ArrowLeft className="w-5 h-5" />
          </Link>
        </Button>
        <h1 className="text-lg font-semibold">Upload Video</h1>
      </div>
      <VideoUploadForm />
    </div>
  );
}
