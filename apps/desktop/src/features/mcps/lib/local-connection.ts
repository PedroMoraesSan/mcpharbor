import type { LocalConnectionInfo } from "@/lib/api-client";

const DEFAULT_WRAPPER_PATH = "~/.mcpharbour/bin/mcpharbour-mcp-wrapper";

/** Extra `docker run` flags per catalog entry (e.g. socket mounts). */
const CATALOG_DOCKER_FLAGS: Record<string, string> = {
  docker: "-v /var/run/docker.sock:/var/run/docker.sock",
};

export type LocalConnectionInput = {
  mcpId: string;
  catalogId: string;
  mcpName: string;
  dockerImage: string;
  credentialKeys: string[];
  hasCredentials: boolean;
  wrapperPath?: string;
  harborEndpoint?: string | null;
  sseEndpoint?: string | null;
  gatewayRunning?: boolean;
};

export function buildLocalConnectionInfo(input: LocalConnectionInput): LocalConnectionInfo {
  const {
    mcpId,
    catalogId,
    mcpName,
    dockerImage,
    credentialKeys,
    hasCredentials,
    wrapperPath = DEFAULT_WRAPPER_PATH,
    harborEndpoint = null,
    sseEndpoint = null,
    gatewayRunning = false,
  } = input;

  const extraFlags = CATALOG_DOCKER_FLAGS[catalogId] ?? "";
  const envFlags = credentialKeys.map((k) => `-e ${k}="\${${k}}"`).join(" ");
  const dockerRun = ["docker run -i --rm", extraFlags, envFlags, dockerImage]
    .filter(Boolean)
    .join(" ")
    .replace(/\s+/g, " ")
    .trim();

  const serverBlockWrapper: Record<string, unknown> = {
    command: wrapperPath,
    args: [catalogId],
    env: {
      MCPHARBOR_MCP_ID: mcpId,
      MCPHARBOR_DOCKER_IMAGE: dockerImage,
      ...(credentialKeys[0] ? { MCPHARBOR_ENV_KEY: credentialKeys[0] } : {}),
    },
  };

  const dockerArgs = ["run", "-i", "--rm"];
  if (extraFlags) {
    for (const flag of extraFlags.split(/\s+/)) {
      if (flag) dockerArgs.push(flag);
    }
  }
  for (const key of credentialKeys) {
    dockerArgs.push("-e", key);
  }
  dockerArgs.push(dockerImage);

  const envVars = Object.fromEntries(
    credentialKeys.map((k) => [k, `<${k}>`]),
  );

  const cursorJsonSnippet = JSON.stringify(
    { mcpServers: { [catalogId]: serverBlockWrapper } },
    null,
    2,
  );

  const claudeJsonSnippet = cursorJsonSnippet;

  const vscodeJsonSnippet = JSON.stringify(
    {
      mcp: {
        servers: {
          [catalogId]: {
            type: "stdio",
            command: "docker",
            args: dockerArgs,
            env: envVars,
          },
        },
      },
    },
    null,
    2,
  );

  return {
    mcp_name: mcpName,
    catalog_id: catalogId,
    docker_image: dockerImage,
    credential_keys: credentialKeys,
    has_credentials: hasCredentials,
    wrapper_path: wrapperPath,
    mcp_id: mcpId,
    docker_run_command: dockerRun,
    cursor_json_snippet: cursorJsonSnippet,
    claude_json_snippet: claudeJsonSnippet,
    vscode_json_snippet: vscodeJsonSnippet,
    harbor_endpoint: harborEndpoint,
    sse_endpoint: sseEndpoint,
    gateway_running: gatewayRunning,
  };
}
