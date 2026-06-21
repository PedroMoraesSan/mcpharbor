import { useQuery } from "@tanstack/react-query";
import { AppUpdateCard } from "@/features/settings/components/AppUpdateCard";
import { api } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { StatusIndicator } from "@/components/status/StatusIndicator";

export function SettingsPage() {
  const { data: settings } = useQuery({
    queryKey: ["settings"],
    queryFn: api.settings,
  });

  return (
    <div>
      <PageHeader title="Settings" description="Configure MCP Harbor" />

      <div className="grid gap-4 md:grid-cols-2">
        <AppUpdateCard />

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
