"use client";

import { useState, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { uploadProduct } from "@/lib/api-client";
import { FileDropzone } from "./FileDropzone";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { CATEGORY_COLORS } from "@/lib/constants";
import { PRODUCT_CATEGORIES } from "@/lib/types";
import type { ProductCategory, ProductUploadResponse } from "@/lib/types";
import { CheckCircle2, AlertCircle, ImageIcon, Loader2, Upload } from "lucide-react";
import { toast } from "sonner";

const PROGRESS_THRESHOLDS = {
  UPLOAD_COMPLETE: 50,
  ANALYZING: 70,
  FINALIZING: 90,
  COMPLETE: 100,
} as const;

type UploadPhase = "idle" | "uploading" | "analyzing" | "finalizing" | "done" | "error";

export function ProductUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<ProductCategory | "">("");
  const [price, setPrice] = useState("");
  const [phase, setPhase] = useState<UploadPhase>("idle");
  const [result, setResult] = useState<ProductUploadResponse | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const imagePreview = useMemo(() => {
    if (!file) return null;
    return URL.createObjectURL(file);
  }, [file]);

  const mutation = useMutation({
    mutationFn: async (formData: FormData) => {
      setPhase("uploading");
      setUploadProgress(0);

      const response = await uploadProduct(formData, (loaded, total) => {
        const progress = Math.round((loaded / total) * PROGRESS_THRESHOLDS.UPLOAD_COMPLETE);
        setUploadProgress(progress);
      });

      setPhase("analyzing");
      setUploadProgress(PROGRESS_THRESHOLDS.ANALYZING);

      return response;
    },
    onSuccess: (data) => {
      setPhase("finalizing");
      setUploadProgress(PROGRESS_THRESHOLDS.FINALIZING);
      setResult(data);

      setTimeout(() => {
        setUploadProgress(PROGRESS_THRESHOLDS.COMPLETE);
        setPhase("done");
        toast.success("Product uploaded successfully!");
      }, 500);
    },
    onError: (err) => {
      setPhase("error");
      toast.error(err instanceof Error ? err.message : "Upload failed");
    },
  });

  const handleSubmit = () => {
    if (!file || !title.trim() || !description.trim() || !category || !price) return;
    const formData = new FormData();
    formData.append("image", file);
    formData.append("title", title.trim());
    formData.append("description", description.trim());
    formData.append("category", category);
    formData.append("price", price);
    setPhase("uploading");
    mutation.mutate(formData);
  };

  const handleReset = () => {
    setFile(null);
    setTitle("");
    setDescription("");
    setCategory("");
    setPrice("");
    setPhase("idle");
    setResult(null);
  };

  if (phase === "done" && result) {
    const colorClass =
      CATEGORY_COLORS[result.bucket_name] || CATEGORY_COLORS.other;
    const hasAnalysisWarnings = result.status === "uploaded_successful_but_failed_detect_classify";

    return (
      <div className="flex flex-col items-center gap-6 p-6 md:p-8 text-center">
        <CheckCircle2 className={`w-16 h-16 ${hasAnalysisWarnings ? "text-yellow-400" : "text-green-400"}`} />
        <div>
          <h3 className="text-lg font-semibold">
            {hasAnalysisWarnings ? "Product Listed with Warnings" : "Product Listed!"}
          </h3>
          <p className="text-sm text-white/50 mt-1">{result.title}</p>
        </div>
        {hasAnalysisWarnings && (
          <div className="w-full bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-left">
            <p className="text-sm text-yellow-200">
              ⚠️ AI analysis encountered an error. Your product was saved but category may need manual review.
            </p>
          </div>
        )}
        <div className="w-full bg-white/5 rounded-xl p-4 text-left space-y-2">
          {result.bucket_name && (
            <p className="text-sm">
              <span className="text-white/50">Category: </span>
              <Badge
                variant="secondary"
                className={`${colorClass} text-white border-0 text-xs capitalize`}
              >
                {result.bucket_name}
              </Badge>
            </p>
          )}
          <p className="text-sm text-white/50 break-all">
            ID: {result.product_id}
          </p>
        </div>
        <div className="flex gap-3 w-full">
          <Button variant="secondary" className="flex-1" onClick={handleReset}>
            Upload Another
          </Button>
          <Button className="flex-1" asChild>
            <Link href="/shop">View Shop</Link>
          </Button>
        </div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="flex flex-col items-center gap-6 p-6 md:p-8 text-center">
        <AlertCircle className="w-16 h-16 text-red-400" />
        <div>
          <h3 className="text-lg font-semibold">Upload Failed</h3>
          <p className="text-sm text-white/50 mt-1">
            Something went wrong listing your product
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

  const isUploading = ["uploading", "analyzing", "finalizing"].includes(phase) || mutation.isPending;
  const isValid = file && title.trim() && description.trim() && category && price && Number(price) >= 0;

  return (
    <div className="space-y-5 p-4 md:p-6">
      <FileDropzone
        accept="image/*,.jpg,.jpeg,.png,.webp"
        onFileSelect={setFile}
        selectedFile={file}
        onClear={() => setFile(null)}
        icon={<ImageIcon className="w-10 h-10 text-white/30" />}
        label="Drop your product image here"
        hint="JPG, PNG, WebP"
        preview={
          imagePreview ? (
            <div className="flex justify-center bg-black/20 p-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-64 md:max-h-72 w-auto rounded-lg object-contain"
              />
            </div>
          ) : undefined
        }
      />

      <div className="space-y-2">
        <label className="text-sm font-medium text-white/70">Title</label>
        <Input
          placeholder="Product title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isUploading}
          className="bg-white/5 border-white/10"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-white/70">
          Description
        </label>
        <Textarea
          placeholder="Describe your product..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={isUploading}
          className="resize-none bg-white/5 border-white/10"
          rows={3}
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-white/70">Category</label>
        <Select
          value={category}
          onValueChange={(v) => setCategory(v as ProductCategory)}
          disabled={isUploading}
        >
          <SelectTrigger className="bg-white/5 border-white/10">
            <SelectValue placeholder="Select a category" />
          </SelectTrigger>
          <SelectContent>
            {PRODUCT_CATEGORIES.map((cat) => (
              <SelectItem key={cat} value={cat} className="capitalize">
                {cat}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-white/70">Price ($)</label>
        <Input
          type="number"
          placeholder="0.00"
          min="0"
          step="0.01"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          disabled={isUploading}
          className="bg-white/5 border-white/10"
        />
      </div>

      {isUploading && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-white/60" />
              <span className="text-sm text-white/60">
                {phase === "uploading" && "Uploading image..."}
                {phase === "analyzing" && "Processing with AI models..."}
                {phase === "finalizing" && "Finalizing listing..."}
              </span>
            </div>
            <span className="text-xs text-white/40 font-mono">
              {uploadProgress}%
            </span>
          </div>
          <Progress value={uploadProgress} className="h-2" />
          <div className="flex justify-between text-xs text-white/30">
            <span>Upload</span>
            <span>Analyze</span>
            <span>Complete</span>
          </div>
        </div>
      )}

      <Button
        onClick={handleSubmit}
        disabled={!isValid || isUploading}
        className="w-full"
        size="lg"
      >
        {isUploading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Uploading...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4 mr-2" />
            List Product
          </>
        )}
      </Button>
    </div>
  );
}
