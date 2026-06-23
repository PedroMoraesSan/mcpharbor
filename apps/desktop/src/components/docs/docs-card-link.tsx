import { Link } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function DocsCardLink({
  href,
  title,
  description,
  icon: Icon,
  className,
}: {
  href: string;
  title: string;
  description: string;
  icon: LucideIcon;
  className?: string;
}) {
  return (
    <Link
      to={href}
      className={cn("docs-card-link group", className)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border/60 bg-surface text-primary transition-colors group-hover:border-primary/30 group-hover:bg-primary/8">
          <Icon className="h-4 w-4" />
        </div>
        <ArrowUpRight className="h-4 w-4 shrink-0 text-muted-foreground/50 transition-transform group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-primary" />
      </div>
      <h3 className="mt-4 text-sm font-semibold text-foreground">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{description}</p>
    </Link>
  );
}

export function DocsCardGrid({ children }: { children: React.ReactNode }) {
  return <div className="docs-card-grid">{children}</div>;
}
