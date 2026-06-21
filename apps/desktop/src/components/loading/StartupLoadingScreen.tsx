import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { HarborLogo } from "@/components/brand/harbor-logo";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

type StartupLoadingScreenProps = {
  title: string;
  subtitle?: string;
  steps?: string[];
  activeStepIndex?: number;
  progress?: number;
  className?: string;
};

export function StartupLoadingScreen({
  title,
  subtitle,
  steps,
  activeStepIndex = 0,
  progress = 0,
  className,
}: StartupLoadingScreenProps) {
  const totalSteps = steps?.length ?? 0;
  const normalizedProgress =
    progress > 0
      ? progress
      : totalSteps > 0
        ? Math.round(((activeStepIndex + 1) / totalSteps) * 100)
        : 35;

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-6 bg-background p-8 text-center",
        className,
      )}
    >
      <div className="flex flex-col items-center gap-3">
        <HarborLogo size={48} className="text-primary" />
        <Loader2 className="h-5 w-5 animate-spin text-primary" aria-hidden />
      </div>

      <div className="max-w-md space-y-2">
        <h1 className="font-display text-lg uppercase tracking-wider text-foreground">{title}</h1>
        {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
      </div>

      {steps && steps.length > 0 ? (
        <ul className="w-full max-w-sm space-y-2 text-left">
          {steps.map((step, index) => {
            const done = index < activeStepIndex;
            const active = index === activeStepIndex;

            return (
              <li
                key={step}
                className={cn(
                  "flex items-center gap-2.5 rounded-lg border px-3 py-2 text-sm transition-all duration-300",
                  done && "border-primary/20 bg-primary/5 text-foreground",
                  active && "border-primary/30 bg-primary/10 text-foreground shadow-sm shadow-primary/5",
                  !done && !active && "border-border/40 text-muted-foreground",
                )}
              >
                {done ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-primary" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 shrink-0 animate-spin text-primary" />
                ) : (
                  <Circle className="h-4 w-4 shrink-0 opacity-50" />
                )}
                <span>{step}</span>
              </li>
            );
          })}
        </ul>
      ) : null}

      <div className="w-full max-w-sm space-y-2">
        <Progress value={normalizedProgress} className="h-1.5 transition-all duration-500" />
        <p className="text-xs text-muted-foreground">
          {normalizedProgress >= 100 ? "Ready" : "Starting services…"}
        </p>
      </div>
    </div>
  );
}
