"""Alembic migration environment."""

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

# Ensure `src/` is on PYTHONPATH (same layout as pytest / uvicorn --app-dir src)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from alembic import context
from sqlalchemy import create_engine, pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from infrastructure.persistence.models import Base
from shared.settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

placeholder_url = "driver://user:pass@localhost/dbname"
configured_url = config.get_main_option("sqlalchemy.url")
if not configured_url or configured_url == placeholder_url:
    config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def _database_url() -> str:
    return config.get_main_option("sqlalchemy.url")


def _sync_sqlite_url(url: str) -> str:
    if url.startswith("sqlite+aiosqlite"):
        return url.replace("sqlite+aiosqlite", "sqlite", 1)
    return url


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    if connection.dialect.name == "sqlite":
        connection.execute(text("PRAGMA foreign_keys=ON"))
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    if connection.dialect.name == "sqlite":
        context.run_migrations()
        connection.commit()
        return
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    section = config.get_section(config.config_ini_section, {}) or {}
    section["sqlalchemy.url"] = _database_url()
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_sqlite_migrations() -> None:
    url = _sync_sqlite_url(_database_url())
    connectable = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        do_run_migrations(connection)


def run_migrations_online() -> None:
    if _database_url().startswith("sqlite"):
        run_sqlite_migrations()
        return
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
