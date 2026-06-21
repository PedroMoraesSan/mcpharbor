#!/usr/bin/env bash
# Creates the Tauri sidecar launcher used in dev (`tauri dev`) and as compile-time externalBin.
# Release builds replace this with the PyInstaller binary from build-sidecar.sh.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN_DIR="${ROOT}/apps/desktop/src-tauri/binaries"
TARGET="$(rustc --print host-tuple 2>/dev/null || echo "aarch64-apple-darwin")"
LAUNCHER="${BIN_DIR}/mcpharbour-api-${TARGET}"

mkdir -p "${BIN_DIR}"

cat > "${LAUNCHER}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
ROOT="${ROOT}"
cd "\${ROOT}/services/api"
exec uv run python src/cli.py "\$@"
EOF
chmod +x "${LAUNCHER}"
echo "Tauri dev sidecar launcher: ${LAUNCHER}"
