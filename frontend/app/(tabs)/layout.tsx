import { BottomNav } from "@/components/layout/BottomNav";
import { TopBar } from "@/components/layout/TopBar";

export default function TabsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col h-[100dvh]">
      <TopBar />
      <main className="flex-1 overflow-hidden">{children}</main>
      <BottomNav />
    </div>
  );
}
