import { BottomNav } from "@/components/layout/BottomNav";
import { SideNav } from "@/components/layout/SideNav";

export default function UploadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col md:flex-row h-[100dvh]">
      <SideNav />
      <div className="flex flex-col flex-1 min-h-0 min-w-0 md:ml-20 lg:ml-64">
        <main className="flex-1 min-h-0 overflow-y-auto scrollbar-hide">
          {children}
        </main>
        <BottomNav />
      </div>
    </div>
  );
}
