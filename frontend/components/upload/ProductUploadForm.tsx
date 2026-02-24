"use client";

import { useState, useMemo } from "react";
import { useMutation } from "@tanstack/react-query";
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
import { CATEGORY_COLORS } from "@/lib/constants";
import { PRODUCT_CATEGORIES } from "@/lib/types";
import type { ProductCategory, ProductUploadResponse } from "@/lib/types";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  Image as ImageIcon,
  Upload,
} from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";

type UploadPhase = "idle" | "uploading" | "done" | "error";

export function ProductUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<ProductCategory | "">("");
  const [phase, setPhase] = useState<UploadPhase>("idle");
  const [result, setResult] = useState<ProductUploadResponse | null>(null);

  const imagePreview = useMemo(() => {
    if (!file) return null;
    return URL.createObjectURL(file);
  }, [file]);

  const mutation = useMutation({
    mutationFn: async (formData: FormData) => {
      return await uploadProduct(formData);
    },
    onSuccess: (data) => {
      setResult(data);
      setPhase("done");
      toast.success("Product uploaded successfully!");
    },
    onError: (err) => {
      setPhase("error");
      toast.error(err instanceof Error ? err.message : "Upload failed");
    },
  });

  const handleSubmit = () => {
    if (!file || !title.trim() || !description.trim() || !category) return;
    const formData = new FormData();
    formData.append("image", file);
    formData.append("title", title.trim());
    formData.append("description", description.trim());
    formData.append("category", category);
    setPhase("uploading");
    mutation.mutate(formData);
  };

  const handleReset = () => {
    setFile(null);
    setTitle("");
    setDescription("");
    setCategory("");
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
          <h3 className="text-lg font-semibold">Product Listed!</h3>
          <p className="text-sm text-white/50 mt-1">{result.title}</p>
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
      <div className="flex flex-col items-center gap-6 p-6 text-center">
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

  const isUploading = mutation.isPending;
  const isValid = file && title.trim() && description.trim() && category;

  return (
    <div className="space-y-5 p-4">
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
            <img
              src={imagePreview}
              alt="Preview"
              className="w-full aspect-square object-cover"
            />
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
