import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, KeyRound, Play, Plug } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AppIconBadge } from "@/components/icons/app-icon";
import { api } from "@/lib/api-client";
import { isSetupComplete } from "@/lib/setup-storage";

const steps = [
  { kind: "icon" as const, label: "Install GitHub MCP from the Catalog" },
  { kind: "key" as const, label: "Save your GitHub PAT in MCP details" },
  { kind: "play" as const, label: "Start the container" },
  { kind: "plug" as const, label: "Connect to Cursor and restart the IDE" },
];

export function WelcomeOnboarding() {
  const { data: mcps } = useQuery({
    queryKey: ["mcps"],
    queryFn: api.mcps,
  });

  if (!isSetupComplete() || (mcps && mcps.length > 0)) {
    return null;
  }

  return (
    <Card className="mb-4 border-primary/25 bg-primary/5">
      <CardHeader>
        <CardTitle className="font-display text-lg uppercase tracking-wider">
          Install your first MCP
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Get your first MCP running in under two minutes — no terminal required.
        </p>
        <ol className="space-y-2">
          {steps.map(({ kind, label }, index) => (
            <li key={label} className="flex items-center gap-3 text-sm">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/15 font-mono text-xs text-primary">
                {index + 1}
              </span>
              {kind === "icon" ? (
                <AppIconBadge kind="github" size="sm" />
              ) : kind === "key" ? (
                <KeyRound className="h-4 w-4 text-primary" />
              ) : kind === "play" ? (
                <Play className="h-4 w-4 text-primary" />
              ) : (
                <Plug className="h-4 w-4 text-primary" />
              )}
              <span>{label}</span>
            </li>
          ))}
        </ol>
        <Button asChild>
          <Link to="/catalog">
            Open Catalog <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
