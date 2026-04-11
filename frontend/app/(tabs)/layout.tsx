import { BottomNav } from "@/components/layout/BottomNav";
import { SideNav } from "@/components/layout/SideNav";
import { TopBar } from "@/components/layout/TopBar";

export default function TabsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col md:flex-row h-[100dvh]">
      <SideNav />
      <div className="flex flex-col flex-1 min-h-0 min-w-0 md:ml-20 lg:ml-60">
        <TopBar />
        <main className="flex-1 min-h-0 overflow-hidden">{children}</main>
        <BottomNav />
      </div>
    </div>
  );
}
