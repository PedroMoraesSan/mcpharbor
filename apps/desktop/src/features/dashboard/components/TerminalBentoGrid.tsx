import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusIndicator } from "@/components/status/StatusIndicator";
import { AppIconBadge, catalogIconId } from "@/components/icons/app-icon";
import { api } from "@/lib/api-client";
import { Activity, AlertTriangle, Cpu, HardDrive } from "lucide-react";

export function TerminalBentoGrid() {
  const { data: stats } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.dashboard,
    refetchInterval: 5000,
  });

  const { data: mcps } = useQuery({
    queryKey: ["mcps"],
    queryFn: api.mcps,
    refetchInterval: 5000,
  });

  const running = mcps?.filter((m) => m.status === "running") || [];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[11px] font-medium normal-case tracking-[0.15em] text-muted-foreground">
            <Activity className="h-4 w-4 text-primary" /> Active MCPs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="font-display text-3xl tracking-wider text-foreground">
            {stats?.active_count ?? 0}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[11px] font-medium normal-case tracking-[0.15em] text-muted-foreground">
            <AlertTriangle className="h-4 w-4 text-destructive" /> Errors
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="font-display text-3xl tracking-wider text-destructive">
            {stats?.error_count ?? 0}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[11px] font-medium normal-case tracking-[0.15em] text-muted-foreground">
            <Cpu className="h-4 w-4 text-primary" /> CPU Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="font-display text-3xl tracking-wider text-foreground">
            {stats?.total_cpu ?? 0}%
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-[11px] font-medium normal-case tracking-[0.15em] text-muted-foreground">
            <HardDrive className="h-4 w-4 text-primary" /> Memory
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="font-display text-3xl tracking-wider text-foreground">
            {stats?.total_memory_mb ?? 0} MB
          </div>
        </CardContent>
      </Card>

      <Card className="md:col-span-2 xl:col-span-4">
        <CardHeader>
          <CardTitle>Running MCPs</CardTitle>
        </CardHeader>
        <CardContent>
          {running.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No MCPs running. Install one from the Catalog.
            </p>
          ) : (
            <div className="grid gap-2 md:grid-cols-2">
              {running.map((mcp) => (
                <Link
                  key={mcp.id}
                  to={`/mcps/${mcp.id}`}
                  className="flex items-center justify-between rounded-xl border border-border/50 bg-secondary/20 p-3 transition-fast hover:border-primary/30 hover:bg-secondary/40"
                >
                  <div className="flex items-center gap-3">
                    <AppIconBadge kind={catalogIconId(mcp.catalog_id)} size="sm" />
                    <div>
                      <div className="font-medium">{mcp.name}</div>
                      <div className="text-xs text-muted-foreground">{mcp.docker_image}</div>
                    </div>
                  </div>
                  <StatusIndicator status={mcp.status} />
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
