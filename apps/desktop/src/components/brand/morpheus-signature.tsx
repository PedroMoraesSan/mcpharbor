import { cn } from "@/lib/utils";

type MorpheusSignatureProps = {
  className?: string;
  /** Size of the Morpheus wordmark */
  size?: "sm" | "md";
};

const MORPHEUS_SIZE = {
  sm: "text-sm",
  md: "text-base",
} as const;

/**
 * "by Morpheus" signature — matches Morpheus/waffles Logo styling:
 * DotGothic16 + orange gradient (#ff670b → #ff8833 → #fe4d01).
 */
export function MorpheusSignature({ className, size = "sm" }: MorpheusSignatureProps) {
  return (
    <span className={cn("inline-flex items-baseline gap-1 leading-none", className)}>
      <span className="text-[10px] font-medium uppercase tracking-[0.16em] text-muted-foreground">
        by
      </span>
      <span
        className={cn(
          "font-display font-bold leading-none tracking-tight text-gradient-morpheus",
          MORPHEUS_SIZE[size],
        )}
      >
        Morpheus
      </span>
    </span>
  );
}
