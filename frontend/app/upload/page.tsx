import Link from "next/link";
import { FileVideo, ShoppingBag, ArrowRight } from "lucide-react";

export default function UploadPage() {
  return (
    <div className="p-4 pt-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Upload</h1>
        <p className="text-sm text-white/50 mt-1">
          Share a video or list a product
        </p>
      </div>

      <div className="space-y-3">
        <Link
          href="/upload/video"
          className="flex items-center gap-4 p-5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group"
        >
          <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center shrink-0">
            <FileVideo className="w-6 h-6 text-white/70" />
          </div>
          <div className="flex-1">
            <h2 className="font-semibold">Upload Video</h2>
            <p className="text-xs text-white/40 mt-0.5">
              Share short-form video content with your audience
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-white/30 group-hover:text-white/60 transition-colors" />
        </Link>

        <Link
          href="/upload/product"
          className="flex items-center gap-4 p-5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group"
        >
          <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center shrink-0">
            <ShoppingBag className="w-6 h-6 text-white/70" />
          </div>
          <div className="flex-1">
            <h2 className="font-semibold">List Product</h2>
            <p className="text-xs text-white/40 mt-0.5">
              Add a product to the marketplace for shoppers to discover
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-white/30 group-hover:text-white/60 transition-colors" />
        </Link>
      </div>
    </div>
  );
}
