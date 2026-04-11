import { Skeleton } from "@/components/ui/skeleton";

export default function ShopLoading() {
  return (
    <div className="h-full overflow-hidden">
      <div className="border-b border-white/[0.06] bg-black/80 px-4 py-3 md:px-6 lg:px-8 md:py-4">
        <div className="max-w-7xl mx-auto flex gap-2 overflow-hidden">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton
              key={i}
              className="h-9 w-[4.5rem] shrink-0 rounded-full ring-1 ring-white/[0.04]"
            />
          ))}
        </div>
      </div>
      <div className="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-5 p-4 md:p-6 lg:px-8 pt-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="aspect-square rounded-2xl ring-1 ring-white/[0.04]" />
            <Skeleton className="h-4 w-[85%] rounded-md" />
            <Skeleton className="h-3 w-1/2 rounded-md" />
          </div>
        ))}
      </div>
    </div>
  );
}
