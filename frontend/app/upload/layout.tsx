import { BottomNav } from "@/components/layout/BottomNav";

export default function UploadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-[100dvh]">
      <main className="flex-1 overflow-y-auto scrollbar-hide">
        {children}
      </main>
      <BottomNav />
    </div>
  );
}
