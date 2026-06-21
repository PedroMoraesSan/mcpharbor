import { ExternalLink } from "lucide-react";
import { AppIconBadge } from "@/components/icons/app-icon";
import { useDockerStatus } from "@/hooks/use-docker-status";
import { isSetupComplete } from "@/lib/setup-storage";

const DOCKER_INSTALL_URL = "https://docs.docker.com/desktop/setup/install/mac-install/";

export function DockerGate() {
  const { data: docker } = useDockerStatus();

  if (docker?.running !== false || !isSetupComplete()) {
    return null;
  }

  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-warning/40 bg-warning/10 px-4 py-3 text-sm text-foreground"
    >
      <AppIconBadge kind="docker" size="sm" className="mt-0.5" />
      <div className="space-y-2">
        <p className="font-medium">Docker is not running</p>
        <p className="text-muted-foreground">
          {docker?.message ||
            "Open Docker Desktop and wait until the engine is ready to install or run MCPs."}
        </p>
        <a
          href={DOCKER_INSTALL_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-primary hover:underline"
        >
          Docker install guide
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>
    </div>
  );
}
