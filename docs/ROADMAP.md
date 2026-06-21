# Roadmap

Status of the MCP Harbor engineering phases and what comes next.

## Completed

| Phase | Focus | Highlights |
|-------|--------|------------|
| **1 — Estabilização** | Config, schema, testes | Bootstrap Python/Rust, Alembic no lifespan, testes lifecycle |
| **2 — Organização** | Docs e packaging | `docs/ARCHITECTURE.md`, `infra/packaging/`, `docs/DEVELOPMENT.md` |
| **3 — Multi-OS prep** | Sidecar e wrapper | Wrapper Cursor dinâmico, sidecar multi-target, CI release manual |
| **4 — Produto** | Release e updates | Tauri updater, `latest.json`, notarize script, `docs/RELEASE.md` |
| **5 — MVP polish** | UX e distribuição | Docker gate, onboarding dashboard, CI release macOS/Windows/Linux |
| **6 — Reorganização monorepo** | Estrutura | `services/api/`, `apps/desktop/`, docs e CI atualizados |

## In progress / next

| Item | Priority | Notes |
|------|----------|-------|
| **Primeiro release público** | Alta | Tag `v0.1.0`, secrets `TAURI_SIGNING_PRIVATE_KEY`, rebuild DMG |
| **Notarização macOS** | Alta | Requer Apple Developer + secrets no GitHub |
| **Integrações Claude / Cline / OpenCode** | Média | RF16–RF18 do product doc |
| **Catálogo expandido** | Média | Mais MCPs além do GitHub |
| **Testes E2E desktop** | Média | Fluxo install → creds → start → Cursor |

## MVP checklist (< 2 min, sem terminal)

- [x] Catálogo com GitHub MCP
- [x] Instalar / desinstalar MCP
- [x] Credenciais no keyring
- [x] Start / stop / restart / update
- [x] Integração Cursor (wrapper seguro)
- [x] Logs e métricas
- [x] App desktop macOS (DMG)
- [x] Auto-update configurado
- [ ] Release publicado no GitHub
- [ ] Instaladores Windows/Linux validados em CI
- [ ] Notarização macOS em produção

## Versioning

Follow [Semantic Versioning](https://semver.org/). Bump together:

- `apps/desktop/package.json`
- `apps/desktop/src-tauri/Cargo.toml`
- `apps/desktop/src-tauri/tauri.conf.json`

Then tag: `git tag vX.Y.Z && git push origin vX.Y.Z`

See [RELEASE.md](RELEASE.md) for the full release runbook.
