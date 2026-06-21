import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type PageHeaderProps = {
  title: string;
  description?: string;
  leading?: ReactNode;
  children?: ReactNode;
  className?: string;
};

export function PageHeader({ title, description, leading, children, className }: PageHeaderProps) {
  return (
    <div
      className={cn(
        "mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between animate-slide-up",
        className,
      )}
    >
      <div className="flex min-w-0 items-start gap-4">
        {leading}
        <div className="min-w-0 space-y-1">
          <h1 className="font-display text-xl uppercase tracking-wider text-foreground">
            {title}
          </h1>
          {description ? (
            <p className="max-w-2xl text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
      </div>
      {children ? (
        <div className="flex shrink-0 flex-wrap items-center gap-2">{children}</div>
      ) : null}
    </div>
  );
}
