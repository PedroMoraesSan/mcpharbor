# Release

How to ship MCP Harbor desktop builds and enable auto-updates.

## Prerequisites

| Requirement | macOS | Windows | Linux |
|-------------|-------|---------|-------|
| Node 22 + pnpm | ✅ | ✅ | ✅ |
| Rust stable | ✅ | ✅ | ✅ |
| Python 3.13 + uv | ✅ | ✅ | ✅ |
| Docker (runtime) | User machine | User machine | User machine |
| Apple Developer (sign + notarize) | Optional | — | — |

## Updater signing keys

Generate once (private key stays local / in CI secrets):

```bash
bash infra/packaging/generate-updater-keys.sh
```

- **Public key** lives in `apps/desktop/src-tauri/tauri.conf.json`
- **Private key** → `.tauri/updater.key` (gitignored)
- **CI secret** → `TAURI_SIGNING_PRIVATE_KEY` (file contents)

The app checks:

`https://github.com/morpheus/mcpharbour/releases/latest/download/latest.json`

## Local builds

```bash
make build-dmg          # macOS DMG
make build-sidecar      # PyInstaller sidecar only

# Other platforms (run on target OS)
bash infra/packaging/windows/build-installer.sh
bash infra/packaging/linux/build-appimage.sh
```

Signed builds (updater artifacts):

```bash
export TAURI_SIGNING_PRIVATE_KEY="$(cat .tauri/updater.key)"
make build-dmg
```

## macOS notarization

After building a DMG:

```bash
export APPLE_ID="you@example.com"
export APPLE_TEAM_ID="XXXXXXXXXX"
export APPLE_APP_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"

bash infra/packaging/macos/notarize-dmg.sh \
  "apps/desktop/src-tauri/target/release/bundle/dmg/MCP Harbor_0.1.0_aarch64.dmg"
```

Or set `NOTARIZE=1` with the same env vars during CI (see `.github/workflows/release.yml`).

## GitHub release (tag)

1. Bump version in `apps/desktop/package.json`, `apps/desktop/src-tauri/Cargo.toml`, `apps/desktop/src-tauri/tauri.conf.json`
2. Commit and tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The **Release** workflow will:

1. Build sidecar + signed DMG (with updater `.sig` files)
2. Optionally notarize when Apple secrets are configured
3. Generate `latest.json` and attach assets to the GitHub Release

Manual dispatch is also available from Actions → Release.

## latest.json

For manual or dry-run releases:

```bash
VERSION=0.1.0
ARTIFACTS=apps/desktop/src-tauri/target/release/bundle/dmg
RELEASE_URL_PREFIX="https://github.com/morpheus/mcpharbour/releases/download/v${VERSION}" \
  bash infra/packaging/generate-latest-json.sh "${VERSION}" "${ARTIFACTS}"
```

Upload `latest.json` next to the signed bundles on the release page.

## CI secrets checklist

| Secret | Purpose |
|--------|---------|
| `TAURI_SIGNING_PRIVATE_KEY` | Sign updater bundles |
| `APPLE_CERTIFICATE` | Base64 `.p12` for code signing (optional) |
| `APPLE_CERTIFICATE_PASSWORD` | Certificate password |
| `APPLE_SIGNING_IDENTITY` | e.g. `Developer ID Application: …` |
| `APPLE_ID` | Notarization |
| `APPLE_TEAM_ID` | Notarization |
| `APPLE_APP_SPECIFIC_PASSWORD` | Notarization |

## User experience

- On startup (desktop bundle), the app silently checks for updates and prompts to install
- **Settings → Application** shows version, manual check, and install button
