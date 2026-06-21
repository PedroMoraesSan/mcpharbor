# Development guide

Day-to-day commands for working on MCP Harbor locally.

## First-time setup

```bash
cd "$(git rev-parse --show-toplevel)"
cp .env.example .env
make install
make db-up
make migrate
make dev
```

- Web UI: http://localhost:1420
- API: http://127.0.0.1:8741/health

## Daily workflow

```bash
make dev-stop    # if previous session left ports in use
make db-up       # if PostgreSQL is not running
make dev         # backend + frontend
```

Stop with `Ctrl+C`, then optionally:

```bash
make dev-stop    # kill orphaned processes on ports 8741 and 1420
make db-down     # stop PostgreSQL container
```

## Separate terminals

```bash
pnpm dev:backend   # API only
pnpm dev:web       # Vite web UI only
pnpm dev:desktop   # Tauri native window (spawns API sidecar automatically)
```

## Port conflicts

```bash
make dev-stop

# Manual cleanup
lsof -ti tcp:8741 | xargs kill -9
lsof -ti tcp:1420 | xargs kill -9

# Inspect listeners
lsof -nP -iTCP:8741 -sTCP:LISTEN
lsof -nP -iTCP:1420 -sTCP:LISTEN
```

## Testing and quality

```bash
make test
cd services/api && uv run ruff check src tests
cd services/api && uv run ruff format --check src tests
cd apps/desktop && pnpm exec tsc --noEmit
cd apps/desktop && pnpm build
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Desktop app (.app / .dmg)

```bash
make build-dmg
bash infra/packaging/macos/generate-app-icons.sh
bash services/api/scripts/build-sidecar.sh
```

The bundled desktop app uses **SQLite** automatically — no PostgreSQL setup required.

| Path | Purpose |
|------|---------|
| `~/.mcpharbour/mcpharbour.db` | Local SQLite database |
| `~/.mcpharbour/.env` | User configuration |
| `~/.mcpharbour/logs/api.log` | Backend logs |
| `~/.mcpharbour/logs/sidecar.log` | Sidecar startup logs |

**External requirement:** Docker Desktop (for running MCP containers).

## Database modes

| Mode | Database | How |
|------|----------|-----|
| Web dev (`make dev`) | PostgreSQL | `make db-up` + Alembic migrations |
| Desktop bundle | SQLite | Auto-created at `~/.mcpharbour/mcpharbour.db` |

See `.env.example` for all configuration variables.
