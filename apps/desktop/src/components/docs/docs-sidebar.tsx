import { Menu } from "lucide-react";
import { useState } from "react";
import { DocsNavLink } from "@/components/docs/docs-nav-link";
import { Button } from "@/components/ui/button";
import { DOCS_NAV } from "@/lib/docs-nav";

function NavSections({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav aria-label="Documentação" className="space-y-7">
      {DOCS_NAV.map((section) => (
        <div key={section.title}>
          <p className="docs-nav-section">{section.title}</p>
          <ul className="space-y-0.5">
            {section.items.map((item) => (
              <li key={item.href}>
                <DocsNavLink
                  href={item.href}
                  label={item.label}
                  icon={item.icon}
                  onClick={onNavigate}
                />
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

export function DocsSidebar() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <div className="docs-mobile-bar lg:hidden">
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-2 border-border/60"
          onClick={() => setOpen(true)}
        >
          <Menu className="h-3.5 w-3.5" />
          Menu
        </Button>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          <div className="fixed left-0 top-0 bottom-0 w-[18rem] border-r border-border/60 bg-background p-0">
            <div className="border-b border-border/50 px-5 py-4">
              <p className="font-display text-base">Documentação</p>
            </div>
            <div className="overflow-y-auto px-4 py-5" style={{ height: "calc(100dvh - 60px)" }}>
              <NavSections onNavigate={() => setOpen(false)} />
            </div>
          </div>
        </div>
      )}

      <aside className="docs-sidebar hidden lg:block">
        <div className="docs-sidebar-panel">
          <NavSections />
        </div>
      </aside>
    </>
  );
}
