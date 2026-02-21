import { DashboardNav } from "@/components/dashboard/DashboardNav";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="relative flex min-h-screen flex-col bg-background">
            <DashboardNav />
            {/* Push content below the fixed nav */}
            <main className="flex-1 pt-16">{children}</main>
        </div>
    );
}
