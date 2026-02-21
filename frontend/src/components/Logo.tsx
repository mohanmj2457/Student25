"use client";

import Link from 'next/link';
import { cn } from '@/lib/utils';
import { GraduationCap } from 'lucide-react';

export function Logo({ className }: { className?: string }) {
  return (
    <Link href="/" className={cn("flex items-center gap-2 group", className)}>
      <div className="p-1.5 bg-background/50 rounded-md border border-white/10 group-hover:border-primary/50 transition-colors">
          <GraduationCap className="h-5 w-5 text-primary" />
      </div>
      <div className="font-bold text-lg font-headline tracking-tighter text-white">
        Padhloo
      </div>
    </Link>
  );
}
