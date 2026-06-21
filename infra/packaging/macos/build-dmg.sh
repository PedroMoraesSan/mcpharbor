#!/usr/bin/env bash
# Build MCP Harbor macOS DMG (Tauri + PyInstaller sidecar).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "${ROOT}"

echo "==> Generating app icons..."
bash infra/packaging/macos/generate-app-icons.sh

echo "==> Building Python API sidecar (PyInstaller)..."
bash services/api/scripts/build-sidecar.sh

echo "==> Cleaning stale Tauri build artifacts (paths may reference old desktop/)..."
if [[ -d apps/desktop/src-tauri/target ]] && rg -q 'mcpharbour/desktop/src-tauri' apps/desktop/src-tauri/target 2>/dev/null; then
  rm -rf apps/desktop/src-tauri/target
fi

echo "==> Building Tauri app + DMG..."
pnpm --filter @mcpharbour/desktop tauri build --bundles dmg

BUNDLE_DIR="${ROOT}/apps/desktop/src-tauri/target/release/bundle"
echo ""
echo "Done. Artifacts:"
find "${BUNDLE_DIR}" -maxdepth 3 \( -name "*.dmg" -o -name "*.app" \) 2>/dev/null | sort || true
