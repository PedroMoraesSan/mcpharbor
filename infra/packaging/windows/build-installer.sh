#!/usr/bin/env bash
# Build MCP Harbor Windows installer (Tauri NSIS + PyInstaller sidecar).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${ROOT}"

echo "==> Building Python API sidecar..."
bash services/api/scripts/build-sidecar.sh

echo "==> Building Tauri Windows installer..."
pnpm --filter @mcpharbour/desktop tauri build --bundles nsis

BUNDLE_DIR="${ROOT}/apps/desktop/src-tauri/target/release/bundle"
echo ""
echo "Done. Artifacts:"
find "${BUNDLE_DIR}" -maxdepth 3 \( -name "*.exe" -o -name "*.msi" \) 2>/dev/null | sort || true
