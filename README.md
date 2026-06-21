# MCP Harbor

Docker Desktop for MCPs — install, configure, and run MCP servers without touching the terminal.

[![CI](https://github.com/morpheus/mcpharbour/actions/workflows/ci.yml/badge.svg)](https://github.com/morpheus/mcpharbour/actions/workflows/ci.yml)

## Features

- Browse and install MCP servers from a catalog
- Store credentials in the OS keychain (never in the database)
- Start, stop, restart, update, and uninstall MCP containers via Docker
- Connect installed MCPs to Cursor with a secure wrapper script
- Live logs and resource metrics per MCP
- Native desktop app (macOS `.dmg`) with embedded SQLite — zero config

## Quick start

### Prerequisites

- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- Node.js 22+ and pnpm
- Docker Desktop (running — required for MCP containers)
- PostgreSQL via Docker Compose (web dev only)
- Rust + Cargo (native Tauri shell only — [rustup.rs](https://rustup.rs))

### Setup

```bash
git clone https://github.com/morpheus/mcpharbour.git
cd mcpharbour
cp .env.example .env
make install
make db-up
make migrate
make dev
```

Open http://localhost:1420 in your browser.

For more commands see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### MVP flow (< 2 minutes)

1. Open MCP Harbor
2. Go to **Catalog** → Install **GitHub MCP**
3. Open MCP details → Save your **GitHub PAT**
4. Click **Start**
5. Click **Connect Cursor**
6. Restart Cursor — GitHub MCP tools are available

## Desktop app

Build and install the macOS app:

```bash
make build-dmg
```

The bundled app:

- Runs a local FastAPI sidecar on `127.0.0.1:8741`
- Uses **SQLite** at `~/.mcpharbour/mcpharbour.db` (no PostgreSQL setup)
- Writes logs to `~/.mcpharbour/logs/`
- Still requires **Docker Desktop** for MCP containers

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design, runtime modes, and cross-platform strategy.

Release builds and auto-update: [docs/RELEASE.md](docs/RELEASE.md) · Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)

```
Frontend (React + Tauri)
        ↓ REST
FastAPI (Presentation)
        ↓
Application (Use Cases)
        ↓
Infrastructure (Docker, Keyring, SQLite / PostgreSQL)
```

Clean Architecture with Domain, Application, Infrastructure, and Presentation layers.

## Project structure

```
apps/desktop/src/     # React UI + Tauri shell
services/api/src/     # Python API (Clean Architecture)
infra/compose/        # PostgreSQL dev setup
docs/                 # Product & development docs
scripts/              # Build and dev helpers
```

## API

Backend runs at `http://127.0.0.1:8741`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/catalog` | MCP catalog |
| GET | `/api/v1/mcps` | Installed MCPs |
| POST | `/api/v1/mcps/install` | Install MCP |
| DELETE | `/api/v1/mcps/{id}` | Uninstall MCP |
| POST | `/api/v1/mcps/{id}/start` | Start container |
| POST | `/api/v1/mcps/{id}/stop` | Stop container |
| POST | `/api/v1/mcps/{id}/restart` | Restart container |
| POST | `/api/v1/mcps/{id}/update` | Pull latest image |
| POST | `/api/v1/mcps/{id}/credentials` | Save credentials |
| POST | `/api/v1/integrations/cursor/connect` | Configure Cursor |
| GET | `/api/v1/dashboard/stats` | Dashboard metrics |
| GET | `/api/v1/settings` | App settings |

## Security

- Credentials stored in OS keyring (never in SQLite/PostgreSQL)
- Cursor integration uses a wrapper script (no tokens in `mcp.json`)
- API binds to `127.0.0.1` only
- Logs never contain secrets

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). We follow the [Contributor Covenant](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE)
