"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Database, BarChart2, GraduationCap, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

export function DashboardNav() {
    const pathname = usePathname();

    const navLinks = [
        {
            href: "/dashboard/engine",
            label: "Data Engine",
            icon: Database,
            description: "Enter & manage marks",
        },
        {
            href: "/dashboard/analyzer",
            label: "Performance Analyzer",
            icon: BarChart2,
            description: "View analytics",
        },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/70 backdrop-blur-xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">

                {/* Logo */}
                <Link href="/dashboard" className="flex items-center gap-2.5 shrink-0">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/30">
                        <GraduationCap className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-white font-bold text-lg tracking-tight">Padhloo</span>
                </Link>

                {/* Nav Links */}
                <nav className="flex items-center gap-2">
                    {navLinks.map(({ href, label, icon: Icon, description }) => {
                        const isActive = pathname.startsWith(href);
                        return (
                            <Link
                                key={href}
                                href={href}
                                title={description}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
                                    isActive
                                        ? "bg-violet-600 text-white shadow-lg shadow-violet-500/30"
                                        : "text-white/70 hover:text-white hover:bg-white/10"
                                )}
                            >
                                <Icon className="w-4 h-4" />
                                <span className="hidden sm:inline">{label}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Logout */}
                <Link
                    href="/"
                    className="flex items-center gap-2 px-3 py-2 rounded-full text-sm text-white/50 hover:text-white hover:bg-white/10 transition-all duration-200"
                    title="Log out"
                >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden sm:inline text-xs">Logout</span>
                </Link>
            </div>
        </header>
    );
}
