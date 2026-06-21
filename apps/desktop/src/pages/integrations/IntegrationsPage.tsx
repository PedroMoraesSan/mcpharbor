import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { AppIconBadge, integrationIconId } from "@/components/icons/app-icon";
import { Clock } from "lucide-react";

const clients = [
  {
    id: "cursor",
    name: "Cursor",
    description: "Connect MCPs to Cursor IDE",
    available: true,
  },
  {
    id: "claude",
    name: "Claude Desktop",
    description: "Integration with Claude Desktop",
    available: false,
  },
  {
    id: "opencode",
    name: "OpenCode",
    description: "Integration with OpenCode",
    available: false,
  },
  {
    id: "cline",
    name: "Cline",
    description: "Integration with Cline",
    available: false,
  },
];

export function IntegrationsPage() {
  const { data: mcps } = useQuery({ queryKey: ["mcps"], queryFn: api.mcps });
  const queryClient = useQueryClient();
  const githubMcp = mcps?.find((m) => m.catalog_id === "github");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"info" | "error">("info");

  const connectMutation = useMutation({
    mutationFn: () => api.connectCursor(githubMcp!.id),
    onSuccess: (data) => {
      setMessage(data.message);
      setMessageType("info");
      queryClient.invalidateQueries({ queryKey: ["mcps"] });
    },
    onError: (e: Error) => {
      setMessage(e.message);
      setMessageType("error");
    },
  });

  const canConnect = Boolean(githubMcp?.has_credentials);

  return (
    <div>
      <PageHeader title="Integrations" description="Connect MCPs to your AI clients" />

      {message && (
        <div
          className={
            messageType === "error"
              ? "mb-6 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-2 text-sm text-destructive"
              : "mb-6 rounded-lg border border-primary/30 bg-primary/5 px-4 py-2 text-sm text-primary"
          }
        >
          {message}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {clients.map((client) => (
          <Card key={client.id}>
            <CardHeader>
              <div className="flex items-start gap-4">
                <AppIconBadge kind={integrationIconId(client.id)} size="lg" />
                <div className="min-w-0 flex-1">
                  <CardTitle>{client.name}</CardTitle>
                  <CardDescription>{client.description}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {client.available ? (
                <div className="space-y-3">
                  {githubMcp?.cursor_connected ? (
                    <p className="text-sm text-primary">
                      Connected — restart Cursor completely, then check Tools &amp; MCP.
                    </p>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {!githubMcp
                        ? "Install GitHub MCP from the Catalog first."
                        : !canConnect
                          ? "Save your GitHub PAT on the MCP detail page first."
                          : "Connect your installed GitHub MCP to Cursor."}
                    </p>
                  )}
                  <Button
                    onClick={() => {
                      if (!githubMcp) return;
                      if (!canConnect) {
                        setMessage("Save your GitHub PAT on the MCP detail page first.");
                        setMessageType("error");
                        return;
                      }
                      connectMutation.mutate();
                    }}
                    disabled={!githubMcp || connectMutation.isPending}
                  >
                    {connectMutation.isPending ? "Connecting..." : "Connect"}
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" /> Coming soon
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
