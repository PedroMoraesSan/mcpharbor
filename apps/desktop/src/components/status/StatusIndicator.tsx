import { cn } from "@/lib/utils";

const statusConfig = {
  running: { label: "Running", color: "text-success", dot: "bg-success" },
  stopped: { label: "Stopped", color: "text-muted", dot: "bg-muted" },
  error: { label: "Error", color: "text-error", dot: "bg-error" },
  starting: { label: "Starting", color: "text-info", dot: "bg-info" },
  updating: { label: "Updating", color: "text-warning", dot: "bg-warning" },
} as const;

interface StatusIndicatorProps {
  status: keyof typeof statusConfig | string;
  className?: string;
}

export function StatusIndicator({ status, className }: StatusIndicatorProps) {
  const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.stopped;

  return (
    <span className={cn("inline-flex items-center gap-2 text-sm font-medium", config.color, className)}>
      <span className={cn("h-2 w-2 rounded-full", config.dot)} />
      {config.label}
    </span>
  );
}
