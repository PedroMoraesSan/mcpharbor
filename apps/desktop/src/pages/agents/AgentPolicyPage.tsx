import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { requestRaw } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { Plus, Save, Trash2, Globe } from "lucide-react";

interface ToolRule {
  tool_name: string;
  allowed_arguments: string[] | null;
}

interface ServerPolicy {
  server_id: string;
  allowed_tools: ToolRule[] | null;
}

export function AgentPolicyPage() {
  const { agentId } = useParams<{ agentId: string }>();
  const [servers, setServers] = useState<ServerPolicy[]>([]);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");
  const queryClient = useQueryClient();

  const { data: policy } = useQuery({
    queryKey: ["policy", agentId],
    queryFn: () =>
      requestRaw<{ agent_id: string; allowed_servers: ServerPolicy[] | null }>(
        `/api/v1/agents/${agentId}/policy`,
      ),
    enabled: !!agentId,
  });

  useEffect(() => {
    if (policy?.allowed_servers) {
      setServers(policy.allowed_servers);
    } else if (policy && !policy.allowed_servers) {
      setServers([]);
    }
  }, [policy]);

  const saveMutation = useMutation({
    mutationFn: (body: { allowed_servers: ServerPolicy[] | null }) =>
      requestRaw(`/api/v1/agents/${agentId}/policy`, {
        method: "PUT",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      setMessage("Policy saved successfully");
      setMessageType("success");
      queryClient.invalidateQueries({ queryKey: ["policy", agentId] });
    },
    onError: (e: Error) => {
      setMessage(e.message);
      setMessageType("error");
    },
  });

  const addServer = () => {
    setServers([...servers, { server_id: "", allowed_tools: null }]);
  };

  const removeServer = (index: number) => {
    setServers(servers.filter((_, i) => i !== index));
  };

  const updateServerId = (index: number, server_id: string) => {
    const updated = [...servers];
    updated[index] = { ...updated[index], server_id };
    setServers(updated);
  };

  const toggleAllTools = (index: number, allowAll: boolean) => {
    const updated = [...servers];
    updated[index] = { ...updated[index], allowed_tools: allowAll ? null : [] };
    setServers(updated);
  };

  const addTool = (serverIndex: number) => {
    const updated = [...servers];
    const tools = updated[serverIndex].allowed_tools || [];
    updated[serverIndex] = {
      ...updated[serverIndex],
      allowed_tools: [...tools, { tool_name: "", allowed_arguments: null }],
    };
    setServers(updated);
  };

  const removeTool = (serverIndex: number, toolIndex: number) => {
    const updated = [...servers];
    const tools = updated[serverIndex].allowed_tools || [];
    tools.splice(toolIndex, 1);
    updated[serverIndex] = {
      ...updated[serverIndex],
      allowed_tools: tools.length > 0 ? tools : [],
    };
    setServers(updated);
  };

  const updateToolName = (serverIndex: number, toolIndex: number, name: string) => {
    const updated = [...servers];
    const tools = updated[serverIndex].allowed_tools || [];
    tools[toolIndex] = { ...tools[toolIndex], tool_name: name };
    setServers(updated);
  };

  const toggleAllArgs = (serverIndex: number, toolIndex: number, allowAll: boolean) => {
    const updated = [...servers];
    const tools = updated[serverIndex].allowed_tools || [];
    tools[toolIndex] = { ...tools[toolIndex], allowed_arguments: allowAll ? null : [] };
    setServers(updated);
  };

  const updateArgs = (serverIndex: number, toolIndex: number, args: string) => {
    const updated = [...servers];
    const tools = updated[serverIndex].allowed_tools || [];
    tools[toolIndex] = {
      ...tools[toolIndex],
      allowed_arguments: args ? args.split(",").map((a) => a.trim()) : [],
    };
    setServers(updated);
  };

  const handleSave = () => {
    const allowed_servers = servers.length > 0 ? servers : null;
    saveMutation.mutate({ allowed_servers });
  };

  return (
    <div>
      <PageHeader
        title="Edit Policy"
        description={`Agent: ${agentId}`}
      />

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

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Define which servers and tools this agent can access. No policy = no access.
          </p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={addServer}>
              <Plus className="mr-1 h-4 w-4" /> Add Server
            </Button>
            <Button size="sm" onClick={handleSave} disabled={saveMutation.isPending}>
              <Save className="mr-1 h-4 w-4" />
              {saveMutation.isPending ? "Saving..." : "Save Policy"}
            </Button>
          </div>
        </div>

        {servers.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <Globe className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                No servers configured. Add a server to grant access.
              </p>
              <p className="text-xs text-muted-foreground">
                Agents with no policy have access to nothing (default deny).
              </p>
            </CardContent>
          </Card>
        ) : (
          servers.map((server, sIdx) => (
            <Card key={sIdx}>
              <CardHeader className="flex flex-row items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder="Server ID (e.g., github)"
                      value={server.server_id}
                      onChange={(e) => updateServerId(sIdx, e.target.value)}
                      className="max-w-xs font-mono text-sm"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeServer(sIdx)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={server.allowed_tools === null}
                    onChange={() => toggleAllTools(sIdx, server.allowed_tools !== null)}
                    className="rounded"
                  />
                  Allow all tools
                </label>

                {server.allowed_tools !== null && (
                  <>
                    {server.allowed_tools.map((tool, tIdx) => (
                      <div
                        key={tIdx}
                        className="rounded-lg border border-border/50 p-3 space-y-2"
                      >
                        <div className="flex items-center gap-2">
                          <Input
                            placeholder="Tool name (e.g., create_issue)"
                            value={tool.tool_name}
                            onChange={(e) => updateToolName(sIdx, tIdx, e.target.value)}
                            className="max-w-xs font-mono text-xs"
                          />
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeTool(sIdx, tIdx)}
                          >
                            <Trash2 className="h-3 w-3 text-destructive" />
                          </Button>
                        </div>

                        <label className="flex items-center gap-2 text-xs">
                          <input
                            type="checkbox"
                            checked={tool.allowed_arguments === null}
                            onChange={() =>
                              toggleAllArgs(sIdx, tIdx, tool.allowed_arguments !== null)
                            }
                            className="rounded"
                          />
                          Allow all arguments
                        </label>

                        {tool.allowed_arguments !== null && (
                          <Input
                            placeholder="Allowed arguments (comma-separated, e.g., title, body)"
                            value={tool.allowed_arguments.join(", ")}
                            onChange={(e) => updateArgs(sIdx, tIdx, e.target.value)}
                            className="font-mono text-xs"
                          />
                        )}
                      </div>
                    ))}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => addTool(sIdx)}
                    >
                      <Plus className="mr-1 h-3 w-3" /> Add Tool
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
