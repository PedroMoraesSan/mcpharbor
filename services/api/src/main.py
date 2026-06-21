import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.persistence.database import engine
from infrastructure.persistence.migrate import upgrade_database
from infrastructure.mcp.gateway import gateway_manager
from presentation.api.v1.router import router as v1_router
from shared.config import ensure_runtime_environment
from shared.logging import configure_logging, get_logger
from shared.settings import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_runtime_environment()
    configure_logging(settings.log_level)
    if os.environ.get("MCPHARBOR_SKIP_DB_MIGRATE") != "1":
        try:
            await upgrade_database(settings.database_url)
        except Exception as exc:
            logger.error("database_init_failed", error=str(exc))
    yield
    await gateway_manager.stop_all()
    try:
        await engine.dispose()
    except Exception as exc:
        logger.error("database_dispose_failed", error=str(exc))


def create_app() -> FastAPI:
    app = FastAPI(
        title="MCP Harbor API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:1420",
            "http://127.0.0.1:1420",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "tauri://localhost",
            "https://tauri.localhost",
            "http://tauri.localhost",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    app.include_router(v1_router)
    return app


app = create_app()
