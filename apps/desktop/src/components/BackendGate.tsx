import { useBackendReady } from "@/hooks/use-backend-ready";
import { useApiStartupProgress } from "@/hooks/use-api-startup-progress";
import { HarborLogo } from "@/components/brand/harbor-logo";
import { StartupLoadingScreen } from "@/components/loading/StartupLoadingScreen";
import { Button } from "@/components/ui/button";

const API_STARTUP_STEPS = [
  "Launching MCP Harbor sidecar",
  "Connecting to local API",
  "Preparing control plane",
];

export function BackendGate({ children }: { children: React.ReactNode }) {
  const { isLoading, isError, isSuccess, refetch, isFetching, failureCount } = useBackendReady();
  const { visible, activeStep, progress } = useApiStartupProgress(
    isLoading,
    isSuccess,
    API_STARTUP_STEPS.length,
  );

  if (visible) {
    return (
      <StartupLoadingScreen
        className="h-screen"
        title="Starting MCP Harbor"
        subtitle={
          failureCount > 0
            ? `Retrying connection (${failureCount})…`
            : "Waiting for the embedded API on 127.0.0.1:8741"
        }
        steps={API_STARTUP_STEPS}
        activeStepIndex={activeStep}
        progress={progress}
      />
    );
  }

  if (isError) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-background p-8 text-center">
        <HarborLogo size={48} className="text-primary" />
        <div className="max-w-md space-y-2">
          <h1 className="font-display text-lg uppercase tracking-wider text-foreground">
            Backend unavailable
          </h1>
          <p className="text-sm text-muted-foreground">
            Could not connect to the embedded API on{" "}
            <span className="font-mono">127.0.0.1:8741</span>.
          </p>
          <p className="text-xs text-muted-foreground">
            Check logs in <span className="font-mono">~/.mcpharbour/logs/</span>.
          </p>
        </div>
        <Button variant="secondary" disabled={isFetching} onClick={() => refetch()}>
          {isFetching ? "Retrying…" : "Retry"}
        </Button>
      </div>
    );
  }

  return children;
}
