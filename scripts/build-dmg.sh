#!/usr/bin/env bash
# Backward-compatible wrapper — use infra/packaging/macos/build-dmg.sh
exec bash "$(cd "$(dirname "$0")/.." && pwd)/infra/packaging/macos/build-dmg.sh" "$@"
