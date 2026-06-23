import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { requestRaw } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { Key, Plus, Trash2, Shield, Copy, Check } from "lucide-react";

export function AgentsPage() {
  const { data: agents, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => requestRaw<AgentResponse[]>("/api/v1/agents"),
  });
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [newToken, setNewToken] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const createMutation = useMutation({
    mutationFn: (agentName: string) =>
      requestRaw<{ id: string; name: string; token: string; created_at: string }>(
        "/api/v1/agents",
        { method: "POST", body: JSON.stringify({ name: agentName }) },
      ),
    onSuccess: (data) => {
      setNewToken(data.token);
      setName("");
      setError("");
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
    onError: (e: Error) => {
      setError(e.message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      requestRaw(`/api/v1/agents/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });

  const copyToken = async () => {
    if (newToken) {
      await navigator.clipboard.writeText(newToken);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div>
      <PageHeader title="Access Control" description="Manage agent identities and permissions" />

      {newToken && (
        <Card className="mb-6 border-primary/30 bg-primary/5">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Key className="h-5 w-5 text-primary" />
              <CardTitle className="text-sm">Agent Created — Copy this token now</CardTitle>
            </div>
            <CardDescription>
              You won't be able to see this token again. Store it securely.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <code className="flex-1 rounded bg-background px-3 py-2 font-mono text-xs break-all">
                {newToken}
              </code>
              <Button size="sm" variant="outline" onClick={copyToken}>
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Agents</CardTitle>
            <CardDescription>AI clients that can connect to MCP Harbor</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : agents?.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No agents created yet. Create one to get started.
              </p>
            ) : (
              <div className="space-y-2">
                {agents?.map((agent) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between rounded-xl border border-border/50 px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <span className="font-mono text-sm">{agent.name}</span>
                        <span className="ml-2 text-xs text-muted-foreground">
                          created {new Date(agent.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteMutation.mutate(agent.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>New Agent</CardTitle>
            <CardDescription>Generate a token for a new AI client</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              placeholder="Agent name (e.g., my-cursor)"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            {error && <p className="text-xs text-destructive">{error}</p>}
            <Button
              className="w-full"
              onClick={() => createMutation.mutate(name)}
              disabled={!name.trim() || createMutation.isPending}
            >
              <Plus className="mr-2 h-4 w-4" />
              {createMutation.isPending ? "Creating..." : "Create Agent"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

interface AgentResponse {
  id: string;
  name: string;
  created_at: string;
}
