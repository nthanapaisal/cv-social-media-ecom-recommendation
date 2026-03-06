"use client";

import { ProductUploadForm } from "@/components/upload/ProductUploadForm";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ProductUploadPage() {
  return (
    <div>
      <div className="sticky top-0 z-10 bg-black/80 backdrop-blur-lg border-b border-white/10">
        <div className="max-w-2xl mx-auto flex items-center gap-3 p-3">
          <Button variant="ghost" size="icon" asChild className="shrink-0">
            <Link href="/upload">
              <ArrowLeft className="w-5 h-5" />
            </Link>
          </Button>
          <h1 className="text-lg font-semibold">List Product</h1>
        </div>
      </div>
      <div className="max-w-2xl mx-auto">
        <ProductUploadForm />
      </div>
    </div>
  );
}
