#!/usr/bin/env bash
# Backward-compatible wrapper — use infra/packaging/macos/generate-app-icons.sh
exec bash "$(cd "$(dirname "$0")/.." && pwd)/infra/packaging/macos/generate-app-icons.sh" "$@"
