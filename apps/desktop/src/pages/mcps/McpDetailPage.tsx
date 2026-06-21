import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError, getLogsStreamUrl } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { AppIconBadge, catalogIconId } from "@/components/icons/app-icon";
import { StatusIndicator } from "@/components/status/StatusIndicator";
import { LogTerminalViewer } from "@/features/logs/components/LogTerminalViewer";
import { AgentPlan } from "@/features/mcps/components/AgentPlan";
import { CredentialsModal } from "@/features/mcps/components/CredentialsModal";
import { CredentialsPanel } from "@/features/mcps/components/CredentialsPanel";
import { ConfirmActionModal } from "@/features/mcps/components/ConfirmActionModal";
import { LocalConnectionPanel } from "@/features/mcps/components/LocalConnectionPanel";
import { RuntimeStartupPanel } from "@/features/mcps/components/RuntimeStartupPanel";
import { useRuntimeStartupMessages } from "@/hooks/use-runtime-startup-messages";
import { Play, Square, RotateCcw, RefreshCw, Plug, Trash2, Loader2 } from "lucide-react";

type PendingAction = "start" | "stop" | "restart" | "update" | "connect" | "uninstall" | null;

export function McpDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [logs, setLogs] = useState<string[]>([]);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"info" | "error">("info");
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [showCredModal, setShowCredModal] = useState(false);

  const { data: mcp } = useQuery({
    queryKey: ["mcp", id],
    queryFn: () => api.mcp(id!),
    enabled: !!id,
    refetchInterval: 3000,
  });

  const { data: catalogEntries } = useQuery({
    queryKey: ["catalog"],
    queryFn: api.catalog,
  });

  const catalogEntry = catalogEntries?.find((e) => e.id === mcp?.catalog_id);
  const credentialFields = catalogEntry?.credentials ?? [];
  const requiredCredentialFields = credentialFields.filter((f) => f.required);

  const { data: metrics, isError: metricsFailed, error: metricsError } = useQuery({
    queryKey: ["metrics", id],
    queryFn: () => api.metrics(id!),
    enabled: !!id && mcp?.status === "running",
    refetchInterval: 3000,
    retry: 1,
  });

  useEffect(() => {
    if (!id || mcp?.status !== "running") return;
    const eventSource = new EventSource(getLogsStreamUrl(id));
    eventSource.addEventListener("log", (e) => {
      const data = JSON.parse(e.data);
      setLogs((prev) => [...prev.slice(-500), data.line]);
    });
    return () => eventSource.close();
  }, [id, mcp?.status]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["mcp", id] });
    queryClient.invalidateQueries({ queryKey: ["mcps"] });
    queryClient.invalidateQueries({ queryKey: ["catalog"] });
    queryClient.invalidateQueries({ queryKey: ["metrics", id] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const showMessage = (text: string, type: "info" | "error" = "info") => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(""), 6000);
  };

  const startMutation = useMutation({
    mutationFn: () => api.start(id!),
    onSuccess: () => {
      showMessage("MCP started");
      setPendingAction(null);
      invalidate();
    },
    onError: (e: Error) => {
      if (e instanceof ApiError && e.code === "missing_credentials") {
        showMessage("Configure the required credentials first.", "error");
        setShowCredModal(true);
        setPendingAction(null);
        return;
      }
      showMessage(e.message || "Failed to start MCP runtime.", "error");
      setPendingAction(null);
      invalidate();
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => api.stop(id!),
    onSuccess: () => {
      showMessage("MCP stopped");
      setPendingAction(null);
      invalidate();
    },
    onError: (e: Error) => showMessage(e.message, "error"),
  });

  const restartMutation = useMutation({
    mutationFn: () => api.restart(id!),
    onSuccess: () => {
      showMessage("MCP restarted");
      setPendingAction(null);
      invalidate();
    },
    onError: (e: Error) => showMessage(e.message, "error"),
  });

  const updateMutation = useMutation({
    mutationFn: () => api.update(id!),
    onSuccess: () => {
      showMessage("MCP updated to latest image");
      setPendingAction(null);
      invalidate();
    },
    onError: (e: Error) => showMessage(e.message, "error"),
  });

  const credMutation = useMutation({
    mutationFn: (values: Record<string, string>) => api.saveCredentials(id!, values),
    onSuccess: () => {
      showMessage("Credentials saved securely");
      setShowCredModal(false);
      invalidate();
    },
    onError: (e: Error) => showMessage(e.message, "error"),
  });

  const connectMutation = useMutation({
    mutationFn: () => api.connectCursor(id!),
    onSuccess: (data) => {
      showMessage(data.message);
      setPendingAction(null);
      invalidate();
    },
    onError: (e: Error) => showMessage(e.message, "error"),
  });

  const uninstallMutation = useMutation({
    mutationFn: () => api.uninstall(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mcps"] });
      queryClient.invalidateQueries({ queryKey: ["catalog"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      navigate("/mcps");
    },
    onError: (e: Error) => {
      showMessage(e.message, "error");
      setPendingAction(null);
    },
  });

  const isStartingRuntime = startMutation.isPending || mcp?.status === "starting";
  const startupDetail = useRuntimeStartupMessages(isStartingRuntime);

  if (!mcp) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  const isTransitioning =
    mcp.status === "starting" || mcp.status === "updating";
  const canStart = mcp.status === "stopped" || mcp.status === "error";
  const canStop = mcp.status === "running" || mcp.status === "starting";
  const canRestart = mcp.status === "running";
  const canUpdate = mcp.status !== "updating" && mcp.status !== "starting";

  const planSteps = [
    { label: "Pull Image", done: true },
    {
      label: "Configure Secrets",
      done:
        requiredCredentialFields.length === 0 || mcp.has_credentials,
    },
    { label: "Start Runtime", done: mcp.status === "running" },
    { label: "Connect Cursor", done: mcp.cursor_connected },
  ];
  const planProgress =
    (planSteps.filter((s) => s.done).length / planSteps.length) * 100;

  const openCredentialsModal = () => setShowCredModal(true);

  const missingRequiredCredentials =
    requiredCredentialFields.length > 0 && !mcp.has_credentials;

  const handleStart = () => {
    if (missingRequiredCredentials) {
      showMessage("Add the required credentials before starting.", "error");
      openCredentialsModal();
      return;
    }
    setPendingAction("start");
  };

  const handleConnectCursor = () => {
    if (missingRequiredCredentials) {
      showMessage("Add the required credentials first.", "error");
      openCredentialsModal();
      return;
    }
    setPendingAction("connect");
  };

  const handleConfirmAction = () => {
    switch (pendingAction) {
      case "start":
        startMutation.mutate();
        break;
      case "stop":
        stopMutation.mutate();
        break;
      case "restart":
        restartMutation.mutate();
        break;
      case "update":
        updateMutation.mutate();
        break;
      case "connect":
        connectMutation.mutate();
        break;
      case "uninstall":
        uninstallMutation.mutate();
        break;
    }
  };

  const isActionPending =
    startMutation.isPending ||
    stopMutation.isPending ||
    restartMutation.isPending ||
    updateMutation.isPending ||
    connectMutation.isPending ||
    uninstallMutation.isPending;

  const actionConfirmConfig: Record<
    Exclude<PendingAction, null>,
    {
      title: string;
      description: ReactNode;
      confirmLabel: string;
      pendingLabel: string;
      variant: "default" | "destructive" | "success";
    }
  > = {
    start: {
      title: `Start ${mcp.name}?`,
      description: (
        <>
          <p>
            Harbor will start this MCP locally and expose a developer endpoint on
            localhost (Streamable HTTP).
          </p>
          {mcp.local_endpoint && (
            <p className="font-mono text-xs text-foreground/80">
              Previous endpoint: {mcp.local_endpoint}
            </p>
          )}
        </>
      ),
      confirmLabel: "Start",
      pendingLabel: "Starting...",
      variant: "success",
    },
    stop: {
      title: `Stop ${mcp.name}?`,
      description: (
        <>
          <p>
            This will shut down the local gateway and disconnect any clients using
            the developer endpoint.
          </p>
          {mcp.local_endpoint && (
            <p className="font-mono text-xs text-foreground/80">{mcp.local_endpoint}</p>
          )}
        </>
      ),
      confirmLabel: "Stop",
      pendingLabel: "Stopping...",
      variant: "default",
    },
    restart: {
      title: `Restart ${mcp.name}?`,
      description: (
        <p>
          The gateway will be stopped and started again. Active connections will be
          interrupted briefly.
        </p>
      ),
      confirmLabel: "Restart",
      pendingLabel: "Restarting...",
      variant: "default",
    },
    update: {
      title: `Update ${mcp.name}?`,
      description: (
        <p>
          Pulls the latest Docker image ({mcp.docker_image}) and updates this MCP.
          If it is running, the gateway may restart during the update.
        </p>
      ),
      confirmLabel: "Update",
      pendingLabel: "Updating...",
      variant: "default",
    },
    connect: {
      title: `Connect ${mcp.name} to Cursor?`,
      description: (
        <p>
          Writes the MCP configuration to{" "}
          <span className="font-mono text-foreground/80">~/.cursor/mcp.json</span>.
          Restart Cursor completely, then check Tools &amp; MCP.
        </p>
      ),
      confirmLabel: "Connect Cursor",
      pendingLabel: "Connecting...",
      variant: "default",
    },
    uninstall: {
      title: `Uninstall ${mcp.name}?`,
      description: (
        <p>
          Stops the gateway, removes credentials from the system keychain, and
          disconnects Cursor. This action cannot be undone.
        </p>
      ),
      confirmLabel: "Uninstall",
      pendingLabel: "Uninstalling...",
      variant: "destructive",
    },
  };

  const confirmConfig = pendingAction ? actionConfirmConfig[pendingAction] : null;
  const startPendingLabel = isStartingRuntime ? startupDetail : "Starting…";

  return (
    <div className="space-y-6">
      <PageHeader
        title={mcp.name}
        description={mcp.description}
        leading={<AppIconBadge kind={catalogIconId(mcp.catalog_id)} size="lg" branded />}
      >
        <div className="flex items-center gap-3">
          <StatusIndicator status={mcp.status} />
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setPendingAction("uninstall")}
            disabled={uninstallMutation.isPending}
            className="gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Uninstall
          </Button>
        </div>
      </PageHeader>

      {message && (
        <div
          className={
            messageType === "error"
              ? "rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-2 text-sm text-destructive"
              : "rounded-lg border border-primary/30 bg-primary/5 px-4 py-2 text-sm text-primary"
          }
        >
          {message}
        </div>
      )}

      <AgentPlan
        title={`Setup ${mcp.name}`}
        steps={planSteps}
        progress={isStartingRuntime ? Math.max(planProgress, 50) : planProgress}
        detail={isStartingRuntime ? startupDetail : undefined}
      />

      {isStartingRuntime ? (
        <RuntimeStartupPanel mcpName={mcp.name} detail={startupDetail} />
      ) : null}

      <div className="flex flex-wrap gap-2">
        <Button
          variant="success"
          onClick={handleStart}
          disabled={!canStart || startMutation.isPending || isTransitioning}
        >
          {startMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          {startMutation.isPending ? "Starting…" : "Start"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => setPendingAction("stop")}
          disabled={!canStop || stopMutation.isPending}
        >
          <Square className="h-4 w-4" />
          {stopMutation.isPending ? "Stopping..." : "Stop"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => setPendingAction("restart")}
          disabled={!canRestart || restartMutation.isPending}
        >
          <RotateCcw className="h-4 w-4" />
          {restartMutation.isPending ? "Restarting..." : "Restart"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => setPendingAction("update")}
          disabled={!canUpdate || updateMutation.isPending}
        >
          <RefreshCw className="h-4 w-4" />
          {updateMutation.isPending || mcp.status === "updating"
            ? "Updating..."
            : "Update"}
        </Button>
        <Button
          onClick={handleConnectCursor}
          disabled={connectMutation.isPending || mcp.cursor_connected}
        >
          <Plug className="h-4 w-4" />
          {connectMutation.isPending
            ? "Connecting..."
            : mcp.cursor_connected
              ? "Connected"
              : "Connect Cursor"}
        </Button>
      </div>

      {missingRequiredCredentials && (
        <p className="text-sm text-warning">
          This MCP requires credentials before you can start it or connect Cursor.
        </p>
      )}
      {mcp.cursor_connected && (
        <p className="text-sm text-primary">
          Cursor is configured — restart Cursor, then open Tools &amp; MCP.
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <CredentialsPanel
          fields={requiredCredentialFields.length > 0 ? requiredCredentialFields : credentialFields}
          configured={
            !missingRequiredCredentials &&
            (credentialFields.length === 0 || mcp.has_credentials)
          }
          onConfigure={openCredentialsModal}
        />

        <Card>
          <CardHeader>
            <CardTitle>Resource Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 font-mono text-sm">
            {metricsFailed && (
              <p className="text-xs text-destructive">
                Could not load metrics:{" "}
                {metricsError?.message ?? "backend unavailable"}
              </p>
            )}
            {metrics?.status === "unavailable" && (
              <p className="text-xs text-warning">
                Docker metrics unavailable — check Docker Desktop.
              </p>
            )}
            {(metrics?.status === "exited" || metrics?.status === "dead") && (
              <p className="text-xs text-warning">
                Container stopped ({metrics.status}). Click Start to run again.
              </p>
            )}
            <div className="flex justify-between">
              <span className="text-muted-foreground">CPU</span>
              <span>{metrics?.cpu_percent ?? 0}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Memory</span>
              <span>
                {metrics?.memory_usage_mb ?? 0} /{" "}
                {metrics?.memory_limit_mb ?? 0} MB
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Container</span>
              <span>{metrics?.status ?? mcp.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Version</span>
              <span>v{mcp.version}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <LocalConnectionPanel
        mcpId={mcp.id}
        catalogId={mcp.catalog_id}
        mcpName={mcp.name}
        dockerImage={mcp.docker_image}
        credentialKeys={credentialFields.map((f) => f.key)}
        hasCredentials={mcp.has_credentials}
        status={mcp.status}
        localEndpoint={mcp.local_endpoint}
        sseEndpoint={mcp.sse_endpoint}
      />

      <div>
        <h2 className="mb-3 font-display text-sm uppercase tracking-wider text-foreground">
          Logs
        </h2>
        <LogTerminalViewer lines={logs.length ? logs : ["Waiting for logs..."]} />
      </div>

      <CredentialsModal
        open={showCredModal}
        onOpenChange={setShowCredModal}
        mcpName={mcp.name}
        fields={credentialFields}
        onSave={(values) => credMutation.mutate(values)}
        isSaving={credMutation.isPending}
        isUpdate={mcp.has_credentials}
      />

      <ConfirmActionModal
        open={pendingAction !== null}
        onOpenChange={(open) => {
          if (!open && !isActionPending) setPendingAction(null);
        }}
        title={confirmConfig?.title ?? ""}
        description={confirmConfig?.description ?? ""}
        confirmLabel={confirmConfig?.confirmLabel ?? "Confirm"}
        pendingLabel={
          pendingAction === "start" && startMutation.isPending
            ? startPendingLabel
            : confirmConfig?.pendingLabel
        }
        variant={confirmConfig?.variant}
        onConfirm={handleConfirmAction}
        isPending={isActionPending}
      />
    </div>
  );
}
