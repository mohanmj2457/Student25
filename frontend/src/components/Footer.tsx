import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="py-6 md:px-8 md:py-0 border-t border-border/40">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
        <Logo />
        <p className="text-balance text-center text-sm leading-loose text-muted-foreground">
          Your personal AI study partner.
        </p>
      </div>
    </footer>
  );
}
