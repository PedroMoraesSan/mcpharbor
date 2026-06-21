import { useEffect, useState } from "react";

const STARTUP_MESSAGES = [
  "Preparing Harbor wrapper…",
  "Pulling container image (first run may take a while)…",
  "Starting MCP server process…",
  "Exposing local HTTP endpoint…",
];

export function useRuntimeStartupMessages(active: boolean, intervalMs = 3500) {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (!active) {
      setIndex(0);
      return;
    }

    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % STARTUP_MESSAGES.length);
    }, intervalMs);

    return () => window.clearInterval(timer);
  }, [active, intervalMs]);

  return STARTUP_MESSAGES[index] ?? STARTUP_MESSAGES[0];
}
