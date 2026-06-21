#!/usr/bin/env bash
# Stops MCP Harbor dev servers (uvicorn reload often leaves orphans on Ctrl+C).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORTS=(8741 1420)

for port in "${PORTS[@]}"; do
  pids="$(lsof -ti "tcp:${port}" 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Stopping port ${port}: ${pids//$'\n'/ }"
    # shellcheck disable=SC2086
    kill -9 ${pids} 2>/dev/null || true
  fi
done

pkill -f "uvicorn main:app.*--port 8741" 2>/dev/null || true
pkill -f "src/cli.py.*--port 8741" 2>/dev/null || true
pkill -f "${ROOT}/apps/desktop.*vite" 2>/dev/null || true

echo "Dev ports cleared (8741 backend, 1420 frontend)."
