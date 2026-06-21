import { Loader2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";

type RuntimeStartupPanelProps = {
  mcpName: string;
  detail: string;
};

export function RuntimeStartupPanel({ mcpName, detail }: RuntimeStartupPanelProps) {
  return (
    <div className="rounded-2xl border border-primary/25 bg-primary/5 p-4">
      <div className="flex items-start gap-3">
        <Loader2 className="mt-0.5 h-5 w-5 shrink-0 animate-spin text-primary" />
        <div className="min-w-0 flex-1 space-y-3">
          <div>
            <p className="font-display text-sm uppercase tracking-wider text-foreground">
              Starting {mcpName}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">{detail}</p>
          </div>
          <Progress className="h-1.5 [&>div]:animate-pulse [&>div]:w-2/3" value={0} />
          <p className="text-xs text-muted-foreground">
            Harbor is preparing the local runtime. Keep Docker Desktop running.
          </p>
        </div>
      </div>
    </div>
  );
}
