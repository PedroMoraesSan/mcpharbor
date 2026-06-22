import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

interface LogTerminalViewerProps {
  lines: string[];
}

export function LogTerminalViewer({ lines }: LogTerminalViewerProps) {
  const [filter, setFilter] = useState("");

  const filtered = filter
    ? lines.filter((l) => l.toLowerCase().includes(filter.toLowerCase()))
    : lines;

  return (
    <div className="console-floating-surface flex h-full flex-col overflow-hidden rounded-2xl border border-border/55 ring-1 ring-white/[0.06]">
      <div className="flex items-center gap-2 border-b border-border/50 px-4 py-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search logs..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="h-8 font-mono text-xs"
        />
      </div>
      <ScrollArea className="h-[400px] p-4">
        <pre className="font-mono text-xs leading-relaxed">
          {filtered.map((line, i) => (
            <div
              key={i}
              className={
                line.toLowerCase().includes("error") ? "text-destructive" : "text-foreground/90"
              }
            >
              {line}
            </div>
          ))}
        </pre>
      </ScrollArea>
    </div>
  );
}
