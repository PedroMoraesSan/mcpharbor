#!/usr/bin/env bash
# Build the PyInstaller sidecar for the current platform.
#
# Output: apps/desktop/src-tauri/binaries/mcpharbour-api-<target-triple>
#
# Cross-platform builds require running this script on each target OS:
#   macOS ARM:  mcpharbour-api-aarch64-apple-darwin
#   macOS Intel: mcpharbour-api-x86_64-apple-darwin
#   Windows:    mcpharbour-api-x86_64-pc-windows-msvc.exe
#   Linux:      mcpharbour-api-x86_64-unknown-linux-gnu
set -euo pipefail

cd "$(dirname "$0")/.."
TARGET=$(rustc --print host-tuple)
uv run pyinstaller scripts/fastapi-server.spec --distpath /tmp/mcpharbour-build --workpath /tmp/mcpharbour-build/work

SOURCE="/tmp/mcpharbour-build/mcpharbour-api"
DEST="../../apps/desktop/src-tauri/binaries/mcpharbour-api-${TARGET}"
if [[ -f "${SOURCE}.exe" ]]; then
  cp "${SOURCE}.exe" "${DEST}.exe"
  echo "Built sidecar: ${DEST}.exe"
else
  cp "${SOURCE}" "${DEST}"
  echo "Built sidecar: ${DEST}"
fi
