import { CheckCircle2, KeyRound, Lock, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { CredentialFieldDef } from "./CredentialsModal";

type CredentialsPanelProps = {
  fields: CredentialFieldDef[];
  configured: boolean;
  onConfigure: () => void;
};

export function CredentialsPanel({ fields, configured, onConfigure }: CredentialsPanelProps) {
  if (fields.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <KeyRound className="h-4 w-4 text-muted-foreground" />
            Credentials
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No credentials required for this MCP.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        configured
          ? "border-primary/20"
          : "border-warning/30",
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <KeyRound className="h-4 w-4 text-muted-foreground" />
              Credentials
            </CardTitle>
            <p className="mt-1 text-xs text-muted-foreground">
              {configured
                ? "Secrets stored in your OS keychain"
                : "Required before starting or connecting"}
            </p>
          </div>
          <div
            className={cn(
              "flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider",
              configured
                ? "bg-primary/10 text-primary"
                : "bg-warning/10 text-warning",
            )}
          >
            {configured ? (
              <>
                <CheckCircle2 className="h-3 w-3" />
                Configured
              </>
            ) : (
              <>
                <Lock className="h-3 w-3" />
                Missing
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <ul className="space-y-2">
          {fields.map((field) => (
            <li
              key={field.key}
              className="flex items-center justify-between gap-2 rounded-lg border border-border/40 bg-secondary/15 px-3 py-2"
            >
              <span className="text-sm text-foreground">{field.label}</span>
              <span className="font-mono text-[10px] text-muted-foreground">{field.key}</span>
            </li>
          ))}
        </ul>

        <Button
          variant={configured ? "secondary" : "default"}
          className="w-full gap-2 sm:w-auto"
          onClick={onConfigure}
        >
          {configured ? (
            <>
              <KeyRound className="h-4 w-4" />
              Update credentials
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" />
              Add credentials
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
