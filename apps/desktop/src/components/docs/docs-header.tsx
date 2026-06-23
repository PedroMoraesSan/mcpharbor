import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { DocsBrandMark } from "@/components/docs/docs-brand-mark";
import { Button } from "@/components/ui/button";
import { DOCS_VERSION } from "@/lib/docs-nav";

export function DocsHeader() {
  return (
    <header className="docs-header sticky top-0 z-50 border-b border-border/40">
      <div className="docs-header-inner">
        <div className="flex min-w-0 items-center gap-3">
          <DocsBrandMark />
          <span className="hidden text-muted-foreground/40 sm:inline" aria-hidden>
            /
          </span>
          <span className="hidden font-mono text-[10px] text-muted-foreground sm:inline">
            v{DOCS_VERSION}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Button asChild size="sm" className="h-8 gap-1.5 px-3">
            <Link to="/">
              Console
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
