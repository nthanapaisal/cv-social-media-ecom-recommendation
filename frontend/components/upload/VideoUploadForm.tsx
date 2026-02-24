"use client";

import { useState, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import { uploadVideo } from "@/lib/api-client";
import { FileDropzone } from "./FileDropzone";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { CATEGORY_COLORS } from "@/lib/constants";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  FileVideo,
  Upload,
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import type { VideoUploadResponse } from "@/lib/types";

type UploadPhase = "idle" | "uploading" | "processing" | "done" | "error";

export function VideoUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [caption, setCaption] = useState("");
  const [phase, setPhase] = useState<UploadPhase>("idle");
  const [result, setResult] = useState<VideoUploadResponse | null>(null);

  const videoPreview = useMemo(() => {
    if (!file) return null;
    return URL.createObjectURL(file);
  }, [file]);

  const mutation = useMutation({
    mutationFn: async (formData: FormData) => {
      setPhase("uploading");
      const response = await uploadVideo(formData);
      return response;
    },
    onSuccess: (data) => {
      setResult(data);
      setPhase("done");
      toast.success("Video uploaded successfully!");
    },
    onError: (err) => {
      setPhase("error");
      toast.error(err instanceof Error ? err.message : "Upload failed");
    },
  });

  const handleSubmit = () => {
    if (!file || !caption.trim()) return;
    const formData = new FormData();
    formData.append("video", file);
    formData.append("caption", caption.trim());
    setPhase("uploading");
    mutation.mutate(formData);
  };

  const handleReset = () => {
    setFile(null);
    setCaption("");
    setPhase("idle");
    setResult(null);
  };

  if (phase === "done" && result) {
    const colorClass =
      CATEGORY_COLORS[result.bucket_name] || CATEGORY_COLORS.other;
    return (
      <div className="flex flex-col items-center gap-6 p-6 text-center">
        <CheckCircle2 className="w-16 h-16 text-green-400" />
        <div>
          <h3 className="text-lg font-semibold">Upload Complete!</h3>
          <p className="text-sm text-white/50 mt-1">
            Your video has been processed
          </p>
        </div>
        <div className="w-full bg-white/5 rounded-xl p-4 text-left space-y-2">
          <p className="text-sm">
            <span className="text-white/50">Category: </span>
            <Badge
              variant="secondary"
              className={`${colorClass} text-white border-0 text-xs`}
            >
              {result.bucket_name}
            </Badge>
          </p>
          <p className="text-sm">
            <span className="text-white/50">Duration: </span>
            {(result.duration_ms / 1000).toFixed(1)}s
          </p>
          <p className="text-sm text-white/50 break-all">
            ID: {result.video_id}
          </p>
        </div>
        <div className="flex gap-3 w-full">
          <Button variant="secondary" className="flex-1" onClick={handleReset}>
            Upload Another
          </Button>
          <Button className="flex-1" asChild>
            <Link href="/feed">View Feed</Link>
          </Button>
        </div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="flex flex-col items-center gap-6 p-6 text-center">
        <AlertCircle className="w-16 h-16 text-red-400" />
        <div>
          <h3 className="text-lg font-semibold">Upload Failed</h3>
          <p className="text-sm text-white/50 mt-1">
            Something went wrong processing your video
          </p>
        </div>
        <div className="flex gap-3 w-full">
          <Button variant="secondary" className="flex-1" onClick={handleReset}>
            Start Over
          </Button>
          <Button className="flex-1" onClick={handleSubmit}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const isUploading = phase === "uploading" || mutation.isPending;

  return (
    <div className="space-y-5 p-4">
      <FileDropzone
        accept="video/mp4,video/quicktime,video/x-matroska,video/webm,video/x-msvideo,.mp4,.mov,.mkv,.webm,.avi"
        onFileSelect={setFile}
        selectedFile={file}
        onClear={() => setFile(null)}
        icon={<FileVideo className="w-10 h-10 text-white/30" />}
        label="Drop your video here"
        hint="MP4, MOV, MKV, WebM, AVI"
        preview={
          videoPreview ? (
            <video
              src={videoPreview}
              className="w-full aspect-video object-cover"
              muted
              playsInline
            />
          ) : undefined
        }
      />

      <div className="space-y-2">
        <label className="text-sm font-medium text-white/70">Caption</label>
        <Textarea
          placeholder="Add a caption to your video..."
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          disabled={isUploading}
          className="resize-none bg-white/5 border-white/10"
          rows={3}
        />
      </div>

      {isUploading && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-white/60" />
            <span className="text-sm text-white/60">
              {phase === "uploading"
                ? "Uploading video..."
                : "Analyzing with CV model..."}
            </span>
          </div>
          <Progress value={phase === "uploading" ? 50 : 80} className="h-1" />
        </div>
      )}

      <Button
        onClick={handleSubmit}
        disabled={!file || !caption.trim() || isUploading}
        className="w-full"
        size="lg"
      >
        {isUploading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Processing...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4 mr-2" />
            Upload Video
          </>
        )}
      </Button>
    </div>
  );
}
