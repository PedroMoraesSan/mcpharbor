import { Link } from "react-router-dom";
import { HarborLogo } from "@/components/brand/harbor-logo";
import { cn } from "@/lib/utils";

const LOGO_SIZE = 28;
const WORDMARK_SIZE = "1.625rem";

type BrandMarkProps = {
  className?: string;
  onClick?: () => void;
};

export function BrandMark({ className, onClick }: BrandMarkProps) {
  return (
    <Link
      to="/"
      onClick={onClick}
      aria-label="MCP Harbor"
      className={cn(
        "group flex items-center gap-2.5 outline-none transition-opacity hover:opacity-90",
        className,
      )}
    >
      <HarborLogo size={LOGO_SIZE} className="shrink-0 text-primary" />
      <span
        className="font-display leading-none tracking-tight text-gradient-primary"
        style={{ fontSize: WORDMARK_SIZE }}
      >
        harbor
      </span>
    </Link>
  );
}
