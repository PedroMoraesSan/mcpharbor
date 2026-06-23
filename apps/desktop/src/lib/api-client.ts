import { getApiBaseUrl, httpFetch } from "@/lib/http";

export class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await httpFetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = body.detail;
    const message =
      typeof detail === "string"
        ? detail
        : detail?.error || body.error || response.statusText;
    throw new ApiError(message, detail?.code || body.code || "error", response.status);
  }

  return response.json();
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  catalog: () => request<CatalogEntry[]>("/api/v1/catalog"),
  mcps: () => request<MCP[]>("/api/v1/mcps"),
  mcp: (id: string) => request<MCP>(`/api/v1/mcps/${id}`),
  install: (catalogId: string) =>
    request<MCP>("/api/v1/mcps/install", {
      method: "POST",
      body: JSON.stringify({ catalog_id: catalogId }),
    }),
  uninstall: (id: string) =>
    request<{ message: string }>(`/api/v1/mcps/${id}`, { method: "DELETE" }),
  start: (id: string) =>
    request<MCP>(`/api/v1/mcps/${id}/start`, { method: "POST" }),
  stop: (id: string) =>
    request<MCP>(`/api/v1/mcps/${id}/stop`, { method: "POST" }),
  expose: (id: string) =>
    request<MCP>(`/api/v1/mcps/${id}/expose`, { method: "POST" }),
  restart: (id: string) =>
    request<MCP>(`/api/v1/mcps/${id}/restart`, { method: "POST" }),
  update: (id: string) =>
    request<MCP>(`/api/v1/mcps/${id}/update`, { method: "POST" }),
  saveCredentials: (id: string, credentials: Record<string, string>) =>
    request<{ saved: string[] }>(`/api/v1/mcps/${id}/credentials`, {
      method: "POST",
      body: JSON.stringify({ credentials }),
    }),
  metrics: (id: string) => request<Metrics>(`/api/v1/mcps/${id}/metrics`),
  connectCursor: (mcpId: string) =>
    request<{ message: string; config_path: string }>(
      "/api/v1/integrations/cursor/connect",
      { method: "POST", body: JSON.stringify({ mcp_id: mcpId }) },
    ),
  localConnection: (id: string) =>
    request<LocalConnectionInfo>(`/api/v1/mcps/${id}/local-connection`),
  dashboard: () => request<DashboardStats>("/api/v1/dashboard/stats"),
  settings: () => request<Settings>("/api/v1/settings"),
  agents: {
    list: () => request<Agent[]>("/api/v1/agents"),
    create: (name: string) =>
      request<Agent & { token: string }>("/api/v1/agents", {
        method: "POST",
        body: JSON.stringify({ name }),
      }),
    delete: (id: string) =>
      request<{ message: string }>(`/api/v1/agents/${id}`, { method: "DELETE" }),
  },
  policies: {
    get: (agentId: string) =>
      request<AgentPolicy>(`/api/v1/agents/${agentId}/policy`),
    update: (agentId: string, policy: Omit<AgentPolicy, "agent_id">) =>
      request<AgentPolicy>(`/api/v1/agents/${agentId}/policy`, {
        method: "PUT",
        body: JSON.stringify(policy),
      }),
  },
};

export interface CatalogEntry {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  docker_image: string;
  credentials: { key: string; label: string; required: boolean }[];
  installed: boolean;
}

export interface MCP {
  id: string;
  catalog_id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  docker_image: string;
  status: "stopped" | "starting" | "running" | "error" | "updating";
  container_id: string | null;
  container_name: string | null;
  has_credentials: boolean;
  cursor_connected: boolean;
  local_endpoint: string | null;
  local_port: number | null;
  sse_endpoint: string | null;
}

export interface Metrics {
  cpu_percent: number;
  memory_usage_mb: number;
  memory_limit_mb: number;
  status: string;
}

export interface DashboardStats {
  active_count: number;
  error_count: number;
  total_count: number;
  total_cpu: number;
  total_memory_mb: number;
  updates_available: number;
}

export interface Settings {
  data_dir: string;
  cursor_config_path: string;
  wrapper_bin_dir: string;
  database_kind: "sqlite" | "postgresql" | "other";
  database_path: string | null;
  docker_running: boolean;
  docker_message: string;
  docker_socket: string | null;
}

export interface Agent {
  id: string;
  name: string;
  created_at: string;
}

export interface ArgumentRule {
  arg_name: string;
  match_type: "glob" | "regex" | "exact";
  pattern: string;
}

export interface ToolRule {
  tool_name: string;
  argument_rules: ArgumentRule[] | null;
}

export interface ServerPolicy {
  server_id: string;
  allowed_tools: ToolRule[] | null;
}

export interface AgentPolicy {
  agent_id: string;
  allowed_servers: ServerPolicy[] | null;
}

export interface LocalConnectionInfo {
  mcp_name: string;
  catalog_id: string;
  docker_image: string;
  credential_keys: string[];
  has_credentials: boolean;
  wrapper_path: string;
  mcp_id: string;
  docker_run_command: string;
  cursor_json_snippet: string;
  claude_json_snippet: string;
  vscode_json_snippet: string;
  harbor_endpoint: string | null;
  sse_endpoint: string | null;
  gateway_running: boolean;
}

export function requestRaw<T>(path: string, options?: RequestInit): Promise<T> {
  return request<T>(path, options);
}

export function getLogsStreamUrl(mcpId: string): string {
  return `${getApiBaseUrl()}/api/v1/mcps/${mcpId}/logs/stream`;
}
