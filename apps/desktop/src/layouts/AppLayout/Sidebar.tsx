import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Box,
  Library,
  ScrollText,
  Plug,
  Settings,
} from "lucide-react";
import { BrandMark } from "@/components/brand/brand-mark";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/mcps", label: "MCPs", icon: Box },
  { to: "/catalog", label: "Catalog", icon: Library },
  { to: "/logs", label: "Logs", icon: ScrollText },
  { to: "/integrations", label: "Integrations", icon: Plug },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden w-sidebar shrink-0 md:flex">
      <div className="console-floating-surface flex h-full w-full flex-col rounded-2xl border border-border/55 ring-1 ring-white/[0.06]">
        <div className="border-b border-border/50 p-4">
          <BrandMark />
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-3">
          <p className="px-3 pb-1 text-[10px] font-medium uppercase tracking-widest text-muted-foreground/80">
            Console
          </p>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-fast",
                  isActive
                    ? "bg-primary/12 font-medium text-foreground shadow-sm ring-1 ring-primary/20"
                    : "text-muted-foreground hover:bg-accent/40 hover:text-foreground",
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={cn("size-4", isActive && "text-primary")} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-border/50 p-4">
          <p className="text-xs text-muted-foreground">v0.1.0</p>
        </div>
      </div>
    </aside>
  );
}
