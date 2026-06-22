import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { AgentPlan } from "@/features/mcps/components/AgentPlan";
import { AppIconBadge, catalogIconId } from "@/components/icons/app-icon";
import { useInstallWizard, useAppStore } from "@/stores/app.store";
import { useDockerStatus } from "@/hooks/use-docker-status";
import { Download, Check, Loader2 } from "lucide-react";
import { useState } from "react";

export function CatalogPage() {
  const { data: catalog, isLoading } = useQuery({
    queryKey: ["catalog"],
    queryFn: api.catalog,
  });
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const searchQuery = useAppStore((s) => s.searchQuery);
  const { steps, progress, isOpen, setOpen, setSteps, setProgress } = useInstallWizard();
  const { data: docker } = useDockerStatus();
  const dockerReady = docker?.running !== false;
  const [installDetail, setInstallDetail] = useState("");
  const [installName, setInstallName] = useState("");

  const installMutation = useMutation({
    mutationFn: (catalogId: string) => api.install(catalogId),
    onSuccess: (mcp) => {
      setSteps([
        { label: "Pull Image", done: true },
        { label: "Configure Secrets", done: false },
        { label: "Start MCP", done: false },
        { label: "Connect Cursor", done: false },
      ]);
      setProgress(25);
      queryClient.invalidateQueries({ queryKey: ["catalog"] });
      queryClient.invalidateQueries({ queryKey: ["mcps"] });
      setTimeout(() => navigate(`/mcps/${mcp.id}`), 1500);
    },
  });

  const handleInstall = async (catalogId: string, name: string) => {
    setInstallName(name);
    setOpen(true);
    setSteps([
      { label: "Pull Image", done: false },
      { label: "Configure Secrets", done: false },
      { label: "Start MCP", done: false },
      { label: "Connect Cursor", done: false },
    ]);
    setProgress(10);
    setInstallDetail(`Pulling image for ${name}...`);

    try {
      setProgress(50);
      setInstallDetail("Pulling image...");
      await installMutation.mutateAsync(catalogId);
      setSteps([
        { label: "Pull Image", done: true },
        { label: "Configure Secrets", done: false },
        { label: "Start MCP", done: false },
        { label: "Connect Cursor", done: false },
      ]);
      setProgress(100);
      setInstallDetail("Installation complete!");
    } catch (e) {
      setInstallDetail(e instanceof Error ? e.message : "Installation failed");
      setProgress(0);
    }
  };

  const filtered = catalog?.filter(
    (e) =>
      !searchQuery ||
      e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.description.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div>
      <PageHeader title="Catalog" description="Browse and install MCP servers" />

      {isOpen && (
        <AgentPlan
          title={`Install ${installName || "MCP"}`}
          steps={steps}
          progress={progress}
          detail={installDetail}
        />
      )}

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading catalog...</p>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {filtered?.map((entry) => (
            <Card key={entry.id}>
              <CardHeader>
                <div className="flex items-start gap-4">
                  <AppIconBadge kind={catalogIconId(entry.id)} size="lg" />
                  <div className="min-w-0 flex-1 space-y-1">
                    <CardTitle>{entry.name}</CardTitle>
                    <CardDescription>{entry.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4 text-xs text-muted-foreground">
                  <span>{entry.author}</span>
                  <span>v{entry.version}</span>
                </div>
                <code className="block rounded-md border border-border/50 bg-background/40 px-2 py-1 font-mono text-xs">
                  {entry.docker_image}
                </code>
                {entry.installed ? (
                  <Button variant="secondary" disabled className="w-full">
                    <Check className="h-4 w-4" /> Installed
                  </Button>
                ) : entry.id === "docker" ? (
                  <Button variant="secondary" disabled className="w-full" title="Local gateway for Docker MCP coming soon">
                    Coming soon
                  </Button>
                ) : (
                  <Button
                    className="w-full"
                    onClick={() => handleInstall(entry.id, entry.name)}
                    disabled={installMutation.isPending || !dockerReady}
                    title={
                      dockerReady
                        ? undefined
                        : "Start Docker Desktop before installing MCPs"
                    }
                  >
                    {installMutation.isPending && installName === entry.name ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                    {installMutation.isPending && installName === entry.name
                      ? "Installing..."
                      : "Install"}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
