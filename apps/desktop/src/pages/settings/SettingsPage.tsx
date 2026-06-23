import { useQuery } from "@tanstack/react-query";
import { Copy, Key, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";
import { AppUpdateCard } from "@/features/settings/components/AppUpdateCard";
import { api } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { StatusIndicator } from "@/components/status/StatusIndicator";

const API_BASE = "http://127.0.0.1:8741";

export function SettingsPage() {
  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: api.settings,
  });

  const { data: agents } = useQuery({
    queryKey: ["agents"],
    queryFn: api.agents.list,
  });

  return (
    <div>
      <PageHeader title="Settings" description="Configure MCP Harbor" />

      <div className="grid gap-4 md:grid-cols-2">
        <AppUpdateCard />

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-primary" />
              MCP Endpoint
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-xs text-muted-foreground">
              Connect MCP clients to the unified gateway. Each agent needs its own token.
            </p>
            <div className="space-y-1.5">
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Endpoint URL
              </p>
              <CopyButton value={`${API_BASE}/api/v1/mcp`} />
            </div>
            <div className="rounded-xl border border-border/50 bg-secondary/20 p-3">
              <p className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                Client configuration (JSON)
              </p>
              <pre className="mt-2 overflow-x-auto font-mono text-[11px] text-foreground">
{`{
  "mcpServers": {
    "harbour": {
      "url": "${API_BASE}/api/v1/mcp",
      "headers": {
        "Authorization": "Bearer harbour_sk_..."
      }
    }
  }
}`}
              </pre>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-4 w-4 text-primary" />
              Agents ({agents?.length ?? 0})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-xs text-muted-foreground">
              Manage agents and their access policies.
            </p>
            {!agents || agents.length === 0 ? (
              <p className="text-xs text-muted-foreground">
                No agents yet.{" "}
                <Link to="/agents" className="text-primary hover:underline">
                  Create one
                </Link>
                .
              </p>
            ) : (
              <div className="space-y-2">
                {agents.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between rounded-lg border border-border/50 px-3 py-2"
                  >
                    <div>
                      <p className="text-sm font-medium">{agent.name}</p>
                      <p className="font-mono text-[10px] text-muted-foreground">
                        {agent.id.slice(0, 8)}…
                      </p>
                    </div>
                    <Link
                      to={`/agents/${agent.id}/policy`}
                      className="text-xs text-primary hover:underline"
                    >
                      Policy
                    </Link>
                  </div>
                ))}
                <Link
                  to="/agents"
                  className="block text-center text-xs text-primary hover:underline"
                >
                  Manage agents →
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Database</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            <StatusIndicator status="running" />
            <p className="text-muted-foreground">
              {settings?.database_kind === "sqlite"
                ? "Local SQLite database (created automatically on first run)."
                : "External PostgreSQL database."}
            </p>
            {settings?.database_path && (
              <p className="font-mono text-muted-foreground">
                File: {settings.database_path}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Docker</CardTitle>
          </CardHeader>
          <CardContent>
            <StatusIndicator
              status={settings?.docker_running ? "running" : "stopped"}
            />
            <p className="mt-2 text-xs text-muted-foreground">
              {settings?.docker_message ||
                "Docker must be running to manage MCP containers"}
            </p>
            {!settings?.docker_running && (
              <p className="mt-2 text-xs text-warning">
                Open Docker Desktop and wait until the engine is ready, then refresh.
              </p>
            )}
            {settings?.docker_socket && (
              <p className="mt-2 font-mono text-xs text-muted-foreground">
                Socket: {settings.docker_socket}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Directories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 font-mono text-xs">
            <div>
              <span className="text-muted-foreground">Data: </span>
              {settings?.data_dir}
            </div>
            <div>
              <span className="text-muted-foreground">Wrapper: </span>
              {settings?.wrapper_bin_dir}
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Registry</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 font-mono text-xs">
            <div>
              <span className="text-muted-foreground">Cursor config: </span>
              {settings?.cursor_config_path}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function CopyButton({ value }: { value: string }) {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-border/50 bg-background px-3 py-2 font-mono text-xs">
      <code className="flex-1 truncate text-foreground">{value}</code>
      <button
        type="button"
        onClick={() => navigator.clipboard.writeText(value)}
        className="shrink-0 text-muted-foreground hover:text-foreground"
      >
        <Copy className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
