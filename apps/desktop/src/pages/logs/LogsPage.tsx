import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/lib/api-client";
import { PageHeader } from "@/components/layout/page-header";
import { StatusIndicator } from "@/components/status/StatusIndicator";

export function LogsPage() {
  const { data: mcps } = useQuery({
    queryKey: ["mcps"],
    queryFn: api.mcps,
  });

  return (
    <div>
      <PageHeader title="Logs" description="Select an MCP to view its logs" />
      <div className="space-y-2">
        {mcps?.map((mcp) => (
          <Link
            key={mcp.id}
            to={`/mcps/${mcp.id}`}
            className="console-floating-surface flex items-center justify-between rounded-2xl border border-border/55 p-4 transition-fast hover:ring-1 hover:ring-primary/20"
          >
            <span className="font-medium">{mcp.name}</span>
            <StatusIndicator status={mcp.status} />
          </Link>
        ))}
        {mcps?.length === 0 && (
          <p className="text-sm text-muted-foreground">No MCPs installed yet.</p>
        )}
      </div>
    </div>
  );
}
