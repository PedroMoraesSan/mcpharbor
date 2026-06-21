import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/lib/api-client";
import { PageHeader } from "@/components/layout/page-header";
import { StatusIndicator } from "@/components/status/StatusIndicator";
import { AppIconBadge, catalogIconId } from "@/components/icons/app-icon";
import { useAppStore } from "@/stores/app.store";

export function McpsPage() {
  const { data: mcps, isLoading } = useQuery({
    queryKey: ["mcps"],
    queryFn: api.mcps,
    refetchInterval: 5000,
    staleTime: 0,
  });
  const searchQuery = useAppStore((s) => s.searchQuery);

  const filtered = mcps?.filter(
    (m) =>
      !searchQuery ||
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.catalog_id.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div>
      <PageHeader title="MCPs" description="Installed MCP servers" />

      <div className="console-floating-surface rounded-2xl border border-border/55 p-5 ring-1 ring-white/[0.06]">
        <div className="mb-3 flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.15em] text-muted-foreground">
          installed/
        </div>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading...</p>
        ) : filtered?.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No MCPs installed.{" "}
            <Link to="/catalog" className="text-primary hover:underline">
              Browse Catalog
            </Link>
          </p>
        ) : (
          <div className="space-y-1">
            {filtered?.map((mcp) => (
              <Link
                key={mcp.id}
                to={`/mcps/${mcp.id}`}
                className="flex items-center justify-between rounded-xl px-3 py-2.5 transition-fast hover:bg-accent/40"
              >
                <div className="flex items-center gap-3">
                  <AppIconBadge kind={catalogIconId(mcp.catalog_id)} size="sm" />
                  <div>
                    <span className="font-mono text-sm">{mcp.name}</span>
                    <span className="ml-2 text-xs text-muted-foreground">v{mcp.version}</span>
                  </div>
                </div>
                <StatusIndicator status={mcp.status} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
