#!/usr/bin/env bash
# Generate Tauri app icons from branding/app-icon.svg
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
SVG="${ROOT}/apps/desktop/branding/app-icon.svg"
DESKTOP="${ROOT}/apps/desktop"

if [[ ! -f "${SVG}" ]]; then
  echo "Missing icon source: ${SVG}"
  exit 1
fi

cd "${DESKTOP}"

if command -v rsvg-convert >/dev/null 2>&1; then
  rsvg-convert -w 1024 -h 1024 "${SVG}" -o /tmp/mcpharbour-icon.png
  pnpm tauri icon /tmp/mcpharbour-icon.png
elif command -v qlmanage >/dev/null 2>&1; then
  qlmanage -t -s 1024 -o /tmp "${SVG}" >/dev/null 2>&1
  pnpm tauri icon "/tmp/$(basename "${SVG}").png"
else
  echo "Install librsvg (rsvg-convert) or use macOS qlmanage to render SVG icons."
  exit 1
fi

echo "App icons generated in apps/desktop/src-tauri/icons/"
