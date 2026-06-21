import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { ConsoleBackground } from "@/components/layout/console-background";
import { DockerGate } from "@/components/DockerGate";
import { AppSetupOverlay } from "@/components/onboarding/AppSetupOverlay";
import { MorpheusSignature } from "@/components/brand/morpheus-signature";
import { useStartupUpdateCheck } from "@/hooks/use-startup-update-check";

export function AppLayout() {
  useStartupUpdateCheck();

  return (
    <div className="relative flex h-dvh flex-col overflow-hidden bg-background">
      <AppSetupOverlay />
      <ConsoleBackground />
      <div className="relative z-10 flex min-h-0 flex-1 gap-3 p-3">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col gap-3">
          <header className="console-floating-surface flex h-14 shrink-0 items-center gap-3 rounded-2xl border border-border/55 px-4 sm:px-6">
            <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-muted-foreground/80">
              MCP Control Plane
            </p>
            <span className="text-muted-foreground/30">·</span>
            <MorpheusSignature />
          </header>
          <main className="console-floating-surface min-h-0 flex-1 overflow-y-auto rounded-2xl border border-border/55 p-4 sm:p-6">
            <div className="mb-4">
              <DockerGate />
            </div>
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
