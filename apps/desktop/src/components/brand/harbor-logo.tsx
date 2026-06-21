import { cn } from "@/lib/utils";

type HarborLogoProps = {
  className?: string;
  size?: number;
};

/** Pixel "H" with dock base — Aegis glyph style adapted for MCP Harbor. */
const VIEWBOX = "96 64 320 320";

export function HarborLogo({ className, size = 32 }: HarborLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox={VIEWBOX}
      xmlns="http://www.w3.org/2000/svg"
      className={cn("block shrink-0", className)}
      aria-hidden
    >
      <g fill="currentColor">
        <rect x="96" y="128" width="64" height="256" />
        <rect x="352" y="128" width="64" height="256" />
        <rect x="160" y="224" width="192" height="64" />
        <rect x="128" y="352" width="256" height="32" />
      </g>
    </svg>
  );
}
