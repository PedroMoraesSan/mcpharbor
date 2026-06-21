#!/usr/bin/env bash
# Notarize a macOS DMG with Apple notarytool (requires Apple Developer account).
#
# Required env:
#   APPLE_ID              Apple ID email
#   APPLE_TEAM_ID         Team ID
#   APPLE_APP_SPECIFIC_PASSWORD  App-specific password
#
# Usage:
#   bash infra/packaging/macos/notarize-dmg.sh path/to/app.dmg
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path-to-dmg>" >&2
  exit 1
fi

DMG="$1"
: "${APPLE_ID:?Set APPLE_ID}"
: "${APPLE_TEAM_ID:?Set APPLE_TEAM_ID}"
: "${APPLE_APP_SPECIFIC_PASSWORD:?Set APPLE_APP_SPECIFIC_PASSWORD}"

if [[ ! -f "${DMG}" ]]; then
  echo "DMG not found: ${DMG}" >&2
  exit 1
fi

echo "==> Submitting ${DMG} for notarization..."
xcrun notarytool submit "${DMG}" \
  --apple-id "${APPLE_ID}" \
  --team-id "${APPLE_TEAM_ID}" \
  --password "${APPLE_APP_SPECIFIC_PASSWORD}" \
  --wait

echo "==> Stapling ticket..."
xcrun stapler staple "${DMG}"

echo "Done. Notarized DMG: ${DMG}"
