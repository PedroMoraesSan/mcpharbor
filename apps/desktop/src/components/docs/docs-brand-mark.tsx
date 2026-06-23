import { Link } from "react-router-dom";
import { HarborLogo } from "@/components/brand/harbor-logo";
import { cn } from "@/lib/utils";

export function DocsBrandMark({ className }: { className?: string }) {
  return (
    <Link
      to="/docs"
      aria-label="MCP Harbor — documentação"
      className={cn(
        "inline-flex items-center gap-2 text-foreground transition-opacity hover:opacity-85",
        className,
      )}
    >
      <HarborLogo size={18} className="shrink-0 text-primary" />
      <span className="font-display text-sm leading-none tracking-tight text-foreground">
        harbor
      </span>
      <span className="rounded border border-border/60 bg-surface/60 px-1.5 py-px font-mono text-[10px] leading-none text-muted-foreground">
        docs
      </span>
    </Link>
  );
}
