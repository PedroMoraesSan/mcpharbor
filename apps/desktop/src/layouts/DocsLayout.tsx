import { Outlet } from "react-router-dom";
import { DocsHeader } from "@/components/docs/docs-header";
import { DocsFooter } from "@/components/docs/docs-footer";
import { DocsSidebar } from "@/components/docs/docs-sidebar";
import { DocsToc } from "@/components/docs/docs-toc";

export function DocsLayout() {
  return (
    <div className="docs-root">
      <div className="docs-bg" aria-hidden />
      <DocsHeader />
      <div className="docs-frame">
        <DocsSidebar />
        <div className="docs-main">
          <div className="docs-body">
            <div className="docs-content">
              <Outlet />
            </div>
            <DocsToc />
          </div>
          <DocsFooter />
        </div>
      </div>
    </div>
  );
}
