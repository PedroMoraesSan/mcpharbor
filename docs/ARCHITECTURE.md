# Architecture

MCP Harbor is a **desktop-first** control plane for MCP servers. The UI is a React app; business logic lives in a local FastAPI service; Tauri provides the native shell and lifecycle management.

## System overview

```
┌─────────────────────────────────────────────────────────┐
│  apps/desktop (Tauri + React)                           │
│  ┌─────────────────┐    HTTP (127.0.0.1:8741)          │
│  │ React UI        │ ──────────────────────────────┐    │
│  └─────────────────┘                               │    │
│  ┌─────────────────▼─────────────────────────────┐ │    │
│  │ Tauri shell (spawn sidecar, permissions)      │ │    │
│  └─────────────────┬─────────────────────────────┘ │    │
└────────────────────┼───────────────────────────────┼────┘
                     │ spawn                         │
┌────────────────────▼───────────────────────────────▼────┐
│  services/api (FastAPI sidecar)                          │
│  Presentation → Application → Domain → Infrastructure  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┬──────────────┐
         ▼           ▼           ▼              ▼
    Docker SDK   OS Keyring   SQLite/PG    Cursor mcp.json
```

## Repository layout

```
mcpharbour/
├── apps/
│   └── desktop/             # React UI + Tauri shell
│       ├── src/             # Feature-based frontend
│       └── src-tauri/       # Rust shell, sidecar spawn
├── services/
│   └── api/                 # FastAPI service (Clean Architecture)
│       ├── src/
│       │   ├── domain/      # Entities, repository interfaces, domain services
│       │   ├── application/ # Use cases, DTOs
│       │   ├── infrastructure/ # Docker, DB, keyring, integrations
│       │   ├── presentation/   # HTTP routes, schemas
│       │   └── shared/      # Config, logging, settings
│       ├── alembic/         # Database migrations (Postgres + SQLite)
│       └── tests/
├── infra/
│   ├── compose/             # PostgreSQL for local dev
│   └── packaging/           # Release builds per OS
├── docs/
│   ├── ARCHITECTURE.md      # This file
│   ├── DEVELOPMENT.md       # Dev commands
│   └── product/             # Product vision docs (PT)
└── scripts/                 # Cross-cutting dev helpers
```

## Backend layers

| Layer | Responsibility | Depends on |
|-------|----------------|------------|
| **Domain** | Business rules, entities, ports | Nothing external |
| **Application** | Use cases orchestrating domain + ports | Domain |
| **Infrastructure** | Adapters (Docker, SQLAlchemy, keyring) | Domain ports |
| **Presentation** | HTTP API, request/response schemas | Application |

Dependency rule: inner layers never import from outer layers.

## Runtime modes

| Mode | UI | Backend | Database |
|------|-----|---------|----------|
| **Web dev** | Browser `:1420` | `uvicorn` `:8741` | PostgreSQL (Docker Compose) |
| **Tauri dev** | Tauri window | `pnpm dev:backend` | PostgreSQL or SQLite |
| **Desktop bundle** | Tauri `.app` | PyInstaller sidecar | SQLite (`~/.mcpharbour/mcpharbour.db`) |

## Configuration

Single source of truth: **`services/api/src/shared/config.py`**

- Creates `~/.mcpharbour/.env` on first run
- Desktop mode defaults to SQLite automatically
- Tauri only ensures `~/.mcpharbour/logs/` exists and passes env vars to the sidecar

## Database schema

**Alembic migrations only** — no `create_all` at runtime.

- Dev: `make migrate` against PostgreSQL
- Desktop/tests: `upgrade_database()` on startup
- Migrations use portable `sa.Uuid()` (SQLite + PostgreSQL)

## Security model

- API binds to `127.0.0.1` only
- Credentials in OS keyring (`mcpharbour` service)
- Cursor integration via wrapper script — tokens never written to `mcp.json`
- Wrapper receives `MCPHARBOR_DOCKER_IMAGE` and `MCPHARBOR_ENV_KEY` via env

## Cross-platform strategy

| Component | macOS | Windows | Linux |
|-----------|-------|---------|-------|
| Tauri shell | ✅ | CI + script | CI + script |
| PyInstaller sidecar | ✅ | ✅ | ✅ |
| SQLite | ✅ | ✅ | ✅ |
| Keyring | ✅ | Credential Manager | Secret Service |
| Auto-update | ✅ | ✅ | ✅ |

Sidecar binaries are named `{name}-{target-triple}` and placed in `apps/desktop/src-tauri/binaries/`.

## Key decisions

1. **Desktop-first, web as dev surface** — same React code; Tauri ships the product
2. **Sidecar pattern** — Python backend as separate process (like Docker Desktop)
3. **Dual database** — Postgres for dev ergonomics; SQLite for zero-config distribution
4. **Monorepo** — API service + desktop app stay together; shared release pipeline

## Related docs

- [DEVELOPMENT.md](DEVELOPMENT.md) — daily commands
- [RELEASE.md](RELEASE.md) — shipping builds, signing, auto-update
- [ROADMAP.md](ROADMAP.md) — engineering phases and MVP checklist
- [product/project_foundation.md](product/project_foundation.md) — product vision (PT)
- [../infra/packaging/README.md](../infra/packaging/README.md) — release builds
