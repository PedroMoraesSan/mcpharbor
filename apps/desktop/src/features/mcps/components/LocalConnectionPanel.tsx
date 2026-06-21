import { useMemo, useState } from "react";
import { Check, ChevronDown, Copy, Plug2 } from "lucide-react";
import type { LocalConnectionInfo } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  buildLocalConnectionInfo,
  type LocalConnectionInput,
} from "@/features/mcps/lib/local-connection";

type Tab = "harbor" | "docker" | "cursor" | "claude" | "vscode";

const TABS: { id: Tab; label: string }[] = [
  { id: "harbor", label: "Harbor" },
  { id: "docker", label: "Docker" },
  { id: "cursor", label: "Cursor" },
  { id: "claude", label: "Claude Desktop" },
  { id: "vscode", label: "VS Code" },
];

function CodeBlock({ code, language = "bash" }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="group relative rounded-lg bg-black/40 border border-border/40">
      <div className="flex items-center justify-between border-b border-border/30 px-3 py-1.5">
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground/60">
          {language}
        </span>
        <Button
          size="sm"
          variant="ghost"
          className="h-6 gap-1.5 px-2 text-xs text-muted-foreground hover:text-foreground"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="h-3 w-3 text-primary" />
          ) : (
            <Copy className="h-3 w-3" />
          )}
          {copied ? "Copied" : "Copy"}
        </Button>
      </div>
      <pre className="overflow-x-auto p-3 text-xs leading-relaxed text-foreground/90">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function TabNav({
  active,
  onChange,
  tabs,
}: {
  active: Tab;
  onChange: (t: Tab) => void;
  tabs: typeof TABS;
}) {
  return (
    <div className="flex flex-wrap gap-1 rounded-lg bg-muted/30 p-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            "rounded-md px-3 py-1.5 text-xs font-medium transition-all",
            active === tab.id
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

function CredentialWarning({ keys }: { keys: string[] }) {
  return (
    <div className="rounded-lg border border-warning/30 bg-warning/5 px-3 py-2 text-xs text-warning">
      This MCP requires credentials:{" "}
      <span className="font-mono">{keys.join(", ")}</span>. Save them first so
      the wrapper can read them from the system keychain.
    </div>
  );
}

function HarborEndpointContent({
  localEndpoint,
  sseEndpoint,
  isRunning,
}: {
  localEndpoint?: string | null;
  sseEndpoint?: string | null;
  isRunning: boolean;
}) {
  if (!isRunning || !localEndpoint) {
    return (
      <div className="rounded-lg border border-border/40 bg-muted/20 px-3 py-3 text-xs text-muted-foreground">
        Click <span className="font-medium text-foreground">Start</span> above to
        launch this MCP locally. Harbor will expose an HTTP endpoint you can connect
        from your app, SDK, or any MCP client that supports Streamable HTTP.
      </div>
    );
  }

  const clientSnippet = JSON.stringify(
    { url: localEndpoint, transport: "streamable-http" },
    null,
    2,
  );

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">
        Harbor is running this MCP and exposing it on localhost. Use the Streamable
        HTTP endpoint below from your application or MCP client.
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        <div className="rounded-lg border border-primary/30 bg-primary/5 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Streamable HTTP
          </p>
          <p className="mt-1 break-all font-mono text-xs text-primary">{localEndpoint}</p>
        </div>
        {sseEndpoint && (
          <div className="rounded-lg border border-border/40 bg-muted/20 px-3 py-2">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
              SSE (legacy)
            </p>
            <p className="mt-1 break-all font-mono text-xs">{sseEndpoint}</p>
          </div>
        )}
      </div>
      <CodeBlock language="json" code={clientSnippet} />
      <p className="text-xs text-muted-foreground">
        Example with the MCP SDK: point your client at{" "}
        <span className="font-mono text-foreground/70">{localEndpoint}</span> using
        transport <span className="font-mono text-foreground/70">streamable-http</span>.
      </p>
    </div>
  );
}

function ConnectionContent({ info, tab }: { info: LocalConnectionInfo; tab: Tab }) {
  switch (tab) {
    case "harbor":
      return (
        <HarborEndpointContent
          localEndpoint={info.harbor_endpoint}
          sseEndpoint={info.sse_endpoint}
          isRunning={info.gateway_running}
        />
      );

    case "docker":
      return (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            Run this MCP server directly via Docker. Set the required environment
            variables before executing.
          </p>
          {info.credential_keys.length > 0 && (
            <CodeBlock
              language="bash"
              code={info.credential_keys
                .map((k) => `export ${k}="your-token-here"`)
                .join("\n")}
            />
          )}
          <CodeBlock language="bash" code={info.docker_run_command} />
        </div>
      );

    case "cursor":
      return (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            Paste into{" "}
            <span className="font-mono text-foreground/70">~/.cursor/mcp.json</span>{" "}
            or use Connect Cursor above.
          </p>
          {!info.has_credentials && info.credential_keys.length > 0 && (
            <CredentialWarning keys={info.credential_keys} />
          )}
          <CodeBlock language="json" code={info.cursor_json_snippet} />
        </div>
      );

    case "claude":
      return (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            Paste into Claude Desktop config, then restart Claude.
          </p>
          {!info.has_credentials && info.credential_keys.length > 0 && (
            <CredentialWarning keys={info.credential_keys} />
          )}
          <CodeBlock language="json" code={info.claude_json_snippet} />
        </div>
      );

    case "vscode":
      return (
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground">
            Add to VS Code <span className="font-mono text-foreground/70">settings.json</span>.
          </p>
          {!info.has_credentials && info.credential_keys.length > 0 && (
            <CredentialWarning keys={info.credential_keys} />
          )}
          <CodeBlock language="json" code={info.vscode_json_snippet} />
        </div>
      );
  }
}

export type LocalConnectionPanelProps = LocalConnectionInput & {
  status: string;
  localEndpoint?: string | null;
  sseEndpoint?: string | null;
};

export function LocalConnectionPanel({
  mcpId,
  catalogId,
  mcpName,
  dockerImage,
  credentialKeys,
  hasCredentials,
  wrapperPath,
  status,
  localEndpoint,
  sseEndpoint,
}: LocalConnectionPanelProps) {
  const gatewayRunning = status === "running" && Boolean(localEndpoint);
  const [tab, setTab] = useState<Tab>("harbor");
  const [open, setOpen] = useState(false);

  const info = useMemo(
    () =>
      buildLocalConnectionInfo({
        mcpId,
        catalogId,
        mcpName,
        dockerImage,
        credentialKeys,
        hasCredentials,
        wrapperPath,
        harborEndpoint: localEndpoint ?? null,
        sseEndpoint: sseEndpoint ?? null,
        gatewayRunning,
      }),
    [
      mcpId,
      catalogId,
      mcpName,
      dockerImage,
      credentialKeys,
      hasCredentials,
      wrapperPath,
      localEndpoint,
      sseEndpoint,
      gatewayRunning,
    ],
  );

  return (
    <Card>
      <CardHeader className="cursor-pointer select-none" onClick={() => setOpen((v) => !v)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Plug2 className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Developer Connection</CardTitle>
          </div>
          <ChevronDown
            className={cn(
              "h-4 w-4 text-muted-foreground transition-transform",
              open && "rotate-180",
            )}
          />
        </div>
        <p className="text-xs text-muted-foreground">
          {gatewayRunning
            ? `Endpoint at ${localEndpoint}`
            : "Start the MCP to get a local HTTP endpoint for your app."}
        </p>
      </CardHeader>

      {open && (
        <CardContent className="space-y-4 pt-0">
          <TabNav active={tab} onChange={setTab} tabs={TABS} />
          <ConnectionContent info={info} tab={tab} />
        </CardContent>
      )}
    </Card>
  );
}
