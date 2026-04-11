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
      <div className="relative rounded-2xl border border-white/[0.06] overflow-hidden bg-white/[0.03]">
        {preview || (
          <div className="flex items-center gap-3 p-4">
            {accept.includes("video") ? (
              <FileVideo className="w-8 h-8 text-white/30" />
            ) : (
              <ImageIcon className="w-8 h-8 text-white/30" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{selectedFile.name}</p>
              <p className="text-xs text-white/35">
                {(selectedFile.size / (1024 * 1024)).toFixed(1)} MB
              </p>
            </div>
          </div>
        )}
        <button
          onClick={onClear}
          className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 backdrop-blur-sm text-white/60 hover:text-white transition-colors border border-white/[0.06]"
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
        "cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200",
        isDragOver
          ? "border-violet-400/40 bg-violet-500/5"
          : "border-white/[0.08] bg-white/[0.02] hover:border-white/[0.15] hover:bg-white/[0.04]"
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
        {icon || <Upload className="w-10 h-10 text-white/20" />}
        <div>
          <p className="text-sm font-medium text-white/60">{label}</p>
          <p className="text-xs text-white/30 mt-1">{hint}</p>
        </div>
      </div>
    </div>
  );
}
