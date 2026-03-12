"use client";

import { useCallback, useState, useRef, type ReactNode } from "react";
import { Upload, X, FileVideo, Image as ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileDropzoneProps {
  accept: string;
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
  icon?: ReactNode;
  label: string;
  hint: string;
  preview?: ReactNode;
}

export function FileDropzone({
  accept,
  onFileSelect,
  selectedFile,
  onClear,
  icon,
  label,
  hint,
  preview,
}: FileDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect]
  );

  if (selectedFile) {
    return (
      <div className="relative rounded-xl border border-white/10 overflow-hidden bg-white/5">
        {preview || (
          <div className="flex items-center gap-3 p-4">
            {accept.includes("video") ? (
              <FileVideo className="w-8 h-8 text-white/40" />
            ) : (
              <ImageIcon className="w-8 h-8 text-white/40" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{selectedFile.name}</p>
              <p className="text-xs text-white/40">
                {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
              </p>
            </div>
          </div>
        )}
        <button
          onClick={onClear}
          className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 text-white/70 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-all",
        isDragOver
          ? "border-white/40 bg-white/10"
          : "border-white/15 bg-white/5 hover:border-white/25 hover:bg-white/[0.07]"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleInputChange}
        className="hidden"
      />
      <div className="flex flex-col items-center gap-3">
        {icon || <Upload className="w-10 h-10 text-white/30" />}
        <div>
          <p className="text-sm font-medium text-white/70">{label}</p>
          <p className="text-xs text-white/40 mt-1">{hint}</p>
        </div>
      </div>
    </div>
  );
}
