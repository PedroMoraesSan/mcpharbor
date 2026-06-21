.PHONY: dev dev-stop dev-tauri dev-web db-up db-down migrate test install build-dmg build-sidecar release-keys

dev:
	bash scripts/dev-stop.sh
	pnpm dev

dev-stop:
	bash scripts/dev-stop.sh

dev-tauri:
	bash scripts/prepare-tauri-dev.sh
	bash scripts/dev-stop.sh
	pnpm dev:tauri

dev-web:
	pnpm dev:web

db-up:
	docker compose -f infra/compose/docker-compose.yml --env-file .env up -d

db-down:
	docker compose -f infra/compose/docker-compose.yml down

migrate:
	cd services/api && uv run alembic upgrade head

test:
	cd services/api && uv run pytest
	cd apps/desktop && pnpm test

install:
	cd services/api && \
	  if [ -f .venv/bin/uvicorn ] && ! .venv/bin/uvicorn --version >/dev/null 2>&1; then \
	    echo "Recreating stale Python venv (broken after directory move)..."; \
	    rm -rf .venv; \
	  fi && \
	  uv sync --all-extras
	pnpm install

build-sidecar:
	bash services/api/scripts/build-sidecar.sh

build-dmg:
	bash infra/packaging/macos/build-dmg.sh

release-keys:
	bash infra/packaging/generate-updater-keys.sh
