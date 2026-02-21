"use client"

import { AnimeNavBar } from "@/components/gpa/AnimeNavBar"
import { Sparkles, Cog, LogIn } from "lucide-react"

const navItems = [
  { name: "Features", url: "/#features", icon: Sparkles },
  { name: "How It Works", url: "/#how-it-works", icon: Cog },
  { name: "Get Started", url: "/login", icon: LogIn, highlighted: true },
]

export function Header() {
  return <AnimeNavBar items={navItems} />
}
