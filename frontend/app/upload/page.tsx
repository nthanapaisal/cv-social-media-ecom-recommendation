import Link from "next/link";
import { FileVideo, ShoppingBag, ArrowRight } from "lucide-react";

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto p-4 md:p-8 pt-8 md:pt-12 space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold">Upload</h1>
        <p className="text-sm text-white/40 mt-1.5">
          Share a video or list a product
        </p>
      </div>

      <div className="space-y-3">
        <Link
          href="/upload/video"
          className="flex items-center gap-4 p-5 md:p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.1] transition-all duration-200 group"
        >
          <div className="w-12 h-12 md:w-14 md:h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 flex items-center justify-center shrink-0 border border-violet-500/10">
            <FileVideo className="w-6 h-6 text-violet-400" />
          </div>
          <div className="flex-1">
            <h2 className="font-semibold">Upload Video</h2>
            <p className="text-xs text-white/35 mt-0.5">
              Share short-form video content with your audience
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all duration-200" />
        </Link>

        <Link
          href="/upload/product"
          className="flex items-center gap-4 p-5 md:p-6 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.06] hover:border-white/[0.1] transition-all duration-200 group"
        >
          <div className="w-12 h-12 md:w-14 md:h-14 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center shrink-0 border border-blue-500/10">
            <ShoppingBag className="w-6 h-6 text-blue-400" />
          </div>
          <div className="flex-1">
            <h2 className="font-semibold">List Product</h2>
            <p className="text-xs text-white/35 mt-0.5">
              Add a product to the marketplace for shoppers to discover
            </p>
          </div>
          <ArrowRight className="w-5 h-5 text-white/20 group-hover:text-white/50 group-hover:translate-x-0.5 transition-all duration-200" />
        </Link>
      </div>
    </div>
  );
}
