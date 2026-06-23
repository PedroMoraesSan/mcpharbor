import { Info, Lightbulb, TriangleAlert } from "lucide-react";
import { cn } from "@/lib/utils";

type DocsCalloutVariant = "default" | "info" | "tip" | "warning";

const variantConfig: Record<
  DocsCalloutVariant,
  { icon: typeof Info; className: string }
> = {
  default: {
    icon: Info,
    className: "border-border/60 bg-surface/50",
  },
  info: {
    icon: Info,
    className: "border-primary/25 bg-primary/6",
  },
  tip: {
    icon: Lightbulb,
    className: "border-border/60 bg-surface/60",
  },
  warning: {
    icon: TriangleAlert,
    className: "border-amber-500/30 bg-amber-500/6",
  },
};

export function DocsCallout({
  title,
  children,
  variant = "info",
}: {
  title?: string;
  children: React.ReactNode;
  variant?: DocsCalloutVariant;
}) {
  const { icon: Icon, className } = variantConfig[variant];

  return (
    <div className={cn("docs-callout", className)}>
      <Icon className="docs-callout-icon h-4 w-4 shrink-0 text-primary" />
      <div className="min-w-0 flex-1">
        {title ? <p className="docs-callout-title">{title}</p> : null}
        <div className="docs-callout-body">{children}</div>
      </div>
    </div>
  );
}
