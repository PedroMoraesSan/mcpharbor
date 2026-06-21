#!/usr/bin/env bash
# Generate Tauri updater signing keys (run once per maintainer machine).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KEY_DIR="${ROOT}/.tauri"
PRIVATE_KEY="${KEY_DIR}/updater.key"
PUBLIC_KEY="${KEY_DIR}/updater.key.pub"

mkdir -p "${KEY_DIR}"

if [[ -f "${PRIVATE_KEY}" && "${1:-}" != "--force" ]]; then
  echo "Keys already exist at ${KEY_DIR}"
  echo "Public key:"
  cat "${PUBLIC_KEY}"
  exit 0
fi

cd "${ROOT}/apps/desktop"
CI=1 pnpm exec tauri signer generate -w "${PRIVATE_KEY}" -f --ci

echo ""
echo "Public key (already in apps/desktop/src-tauri/tauri.conf.json):"
cat "${PUBLIC_KEY}"
echo ""
echo "For CI, set GitHub secret TAURI_SIGNING_PRIVATE_KEY to the contents of:"
echo "  ${PRIVATE_KEY}"
