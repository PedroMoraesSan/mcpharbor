# Release packaging

Platform-specific build scripts for distributable artifacts.

See [docs/RELEASE.md](../../docs/RELEASE.md) for the full release checklist (signing, notarization, GitHub releases, auto-update).

## macOS

```bash
bash infra/packaging/macos/build-dmg.sh
```

Produces:

- `apps/desktop/src-tauri/target/release/bundle/dmg/*.dmg` (+ `.sig` for updater)
- `apps/desktop/src-tauri/target/release/bundle/macos/*.app`

Optional notarization:

```bash
bash infra/packaging/macos/notarize-dmg.sh path/to/app.dmg
```

### Sidecar binaries

The Tauri app bundles a PyInstaller-built Python sidecar. Binary naming follows Rust target triples:

| Platform | Example filename |
|----------|------------------|
| macOS ARM | `mcpharbour-api-aarch64-apple-darwin` |
| macOS Intel | `mcpharbour-api-x86_64-apple-darwin` |
| Windows | `mcpharbour-api-x86_64-pc-windows-msvc.exe` |
| Linux | `mcpharbour-api-x86_64-unknown-linux-gnu` |

Build the sidecar on each target platform:

```bash
bash services/api/scripts/build-sidecar.sh
```

Tauri selects the matching binary from `apps/desktop/src-tauri/binaries/` at bundle time.

## Windows

```bash
bash infra/packaging/windows/build-installer.sh
```

Produces NSIS installer under `apps/desktop/src-tauri/target/release/bundle/nsis/`.

## Linux

```bash
bash infra/packaging/linux/build-appimage.sh
```

Produces AppImage under `apps/desktop/src-tauri/target/release/bundle/appimage/`.

## Updater artifacts

Set `createUpdaterArtifacts: true` in `tauri.conf.json` (already enabled). After a signed build, generate `latest.json`:

```bash
bash infra/packaging/generate-latest-json.sh 0.1.0 path/to/artifacts/
```

Generate signing keys once:

```bash
bash infra/packaging/generate-updater-keys.sh
```
