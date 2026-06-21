#!/usr/bin/env bash
# Build latest.json for Tauri updater from release artifacts in a directory.
#
# Usage:
#   bash infra/packaging/generate-latest-json.sh <version> <artifacts-dir> [output-file]
#
# Optional env:
#   RELEASE_NOTES   Changelog text for latest.json
#   RELEASE_DATE    ISO8601 pub_date (defaults to now UTC)
#   RELEASE_URL_PREFIX  Base URL for download links (e.g. GitHub release asset URL)
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <version> <artifacts-dir> [output-file]" >&2
  exit 1
fi

VERSION="$1"
ARTIFACTS_DIR="$2"
OUTPUT="${3:-${ARTIFACTS_DIR}/latest.json}"
NOTES="${RELEASE_NOTES:-MCP Harbor ${VERSION}}"
PUB_DATE="${RELEASE_DATE:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"
URL_PREFIX="${RELEASE_URL_PREFIX:-}"

python3 - <<'PY' "${VERSION}" "${ARTIFACTS_DIR}" "${OUTPUT}" "${NOTES}" "${PUB_DATE}" "${URL_PREFIX}"
import json
import sys
from pathlib import Path

version, artifacts_dir, output, notes, pub_date, url_prefix = sys.argv[1:7]
root = Path(artifacts_dir)
platforms: dict[str, dict[str, str]] = {}


def platform_for(name: str) -> str | None:
    lower = name.lower()
    if lower.endswith(".dmg") or lower.endswith(".app.tar.gz"):
        if "aarch64" in lower or "arm64" in lower:
            return "darwin-aarch64"
        if "x86_64" in lower or "x64" in lower:
            return "darwin-x86_64"
        return "darwin-aarch64"
    if lower.endswith("-setup.exe") or lower.endswith(".msi"):
        return "windows-x86_64"
    if lower.endswith(".appimage"):
        return "linux-x86_64"
    return None


for sig in root.rglob("*.sig"):
    artifact = sig.with_suffix("")
    if not artifact.is_file():
        continue
    platform = platform_for(artifact.name)
    if not platform:
        continue
    url = (
        f"{url_prefix.rstrip('/')}/{artifact.name}"
        if url_prefix
        else artifact.name
    )
    platforms[platform] = {
        "signature": sig.read_text(encoding="utf-8").strip(),
        "url": url,
    }

payload = {
    "version": version,
    "notes": notes,
    "pub_date": pub_date,
    "platforms": platforms,
}

Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output} with platforms: {', '.join(platforms) or '(none)'}")
PY
