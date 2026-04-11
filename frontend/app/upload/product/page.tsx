"use client";

import { ProductUploadForm } from "@/components/upload/ProductUploadForm";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ProductUploadPage() {
  return (
    <div>
      <div className="sticky top-0 z-10 bg-black/90 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-2xl mx-auto flex items-center gap-3 p-3">
          <Button variant="ghost" size="icon" asChild className="shrink-0 text-white/60 hover:text-white">
            <Link href="/upload">
              <ArrowLeft className="w-5 h-5" />
            </Link>
          </Button>
          <h1 className="text-base font-semibold">List Product</h1>
        </div>
      </div>
      <div className="max-w-2xl mx-auto">
        <ProductUploadForm />
      </div>
    </div>
  );
}
