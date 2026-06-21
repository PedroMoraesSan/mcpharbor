# Contributing to MCP Harbor

Thanks for your interest in contributing! This guide covers local setup, conventions, and how to submit changes.

## Development setup

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for day-to-day commands.

Quick start:

```bash
cp .env.example .env
make install
make db-up
make migrate
make dev
```

Open the web UI at http://localhost:1420 and the API at http://127.0.0.1:8741/health.

## Project structure

| Path | Description |
|------|-------------|
| `services/api/src/` | FastAPI API (Clean Architecture) |
| `apps/desktop/` | Tauri + React frontend |
| `infra/compose/` | PostgreSQL for local development |
| `docs/` | Product and development documentation |

## Code style

**Backend (Python)**

- Format and lint with Ruff: `cd services/api && uv run ruff check src tests && uv run ruff format src tests`
- Use type hints and keep use cases thin — business logic belongs in domain/application layers
- Prefer `shared.time.utc_now()` over `datetime.utcnow()`

**Frontend (TypeScript)**

- Typecheck: `cd apps/desktop && pnpm exec tsc --noEmit`
- UI copy in English
- Use existing shadcn/ui patterns and Tailwind utilities from `globals.css`

## Testing

```bash
make test
```

Add tests for new use cases and API routes. Backend tests use an in-memory SQLite database.

## Pull requests

1. Fork the repo and create a feature branch from `main`
2. Keep changes focused — one concern per PR when possible
3. Run `make test` before opening the PR
4. Fill in the PR template (summary + test plan)

## Reporting issues

Use GitHub Issues with the bug or feature template. Include OS, Docker version, and steps to reproduce for bugs.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be respectful and constructive.
