import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import { Check, Circle } from "lucide-react";

interface AgentPlanProps {
  title: string;
  steps: { label: string; done: boolean }[];
  progress: number;
  detail?: string;
}

export function AgentPlan({ title, steps, progress, detail }: AgentPlanProps) {
  return (
    <div className="console-floating-surface rounded-2xl border border-border/55 p-5 ring-1 ring-white/[0.06]">
      <h3 className="mb-4 font-display text-sm uppercase tracking-wider text-foreground">
        {title}
      </h3>
      <div className="mb-4 space-y-2">
        {steps.map((step) => (
          <div key={step.label} className="flex items-center gap-2 text-sm">
            {step.done ? (
              <Check className="h-4 w-4 text-primary" />
            ) : (
              <Circle className="h-4 w-4 text-muted-foreground" />
            )}
            <span className={cn(step.done ? "text-foreground" : "text-muted-foreground")}>
              {step.label}
            </span>
          </div>
        ))}
      </div>
      <Progress value={progress} className="mb-2" />
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{detail || "Processing..."}</span>
        <span>{Math.round(progress)}%</span>
      </div>
    </div>
  );
}
