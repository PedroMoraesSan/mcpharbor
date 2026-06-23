import { Link, useLocation } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export function DocsNavLink({
  href,
  label,
  icon: Icon,
  onClick,
  className,
}: {
  href: string;
  label: string;
  icon: LucideIcon;
  onClick?: () => void;
  className?: string;
}) {
  const { pathname } = useLocation();
  const active =
    href === "/docs"
      ? pathname === "/docs"
      : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <Link
      to={href}
      onClick={onClick}
      className={cn(
        "docs-nav-link group flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors",
        active ? "docs-nav-link-active" : "text-muted-foreground hover:text-foreground",
        className,
      )}
    >
      <Icon
        className={cn(
          "h-4 w-4 shrink-0 transition-colors",
          active ? "text-primary" : "text-muted-foreground/70 group-hover:text-foreground/80",
        )}
      />
      <span className={cn("truncate", active && "font-medium text-foreground")}>{label}</span>
    </Link>
  );
}
