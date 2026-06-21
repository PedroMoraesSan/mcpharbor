"""Run Alembic migrations programmatically (dev, tests, and bundled sidecar)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine


def _service_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "alembic.ini").is_file():
            return parent
    return here.parents[3]


def _alembic_config(database_url: str) -> Config:
    root = _service_root()
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", database_url)
    if not getattr(sys, "frozen", False):
        cfg.set_main_option("prepend_sys_path", str(root / "src"))
    return cfg


async def _prepare_sqlite(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return

    connect_args = {"check_same_thread": False}
    engine = create_async_engine(database_url, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA foreign_keys=ON"))
    await engine.dispose()


def _sync_sqlite_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite"):
        return database_url.replace("sqlite+aiosqlite", "sqlite", 1)
    return database_url


def _stamp_sqlite_if_schema_present(database_url: str) -> None:
    """Recover DBs where tables exist but alembic_version was never stamped."""
    if not database_url.startswith("sqlite"):
        return

    sync_url = _sync_sqlite_url(database_url)
    engine = create_engine(sync_url, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        tables = {
            row[0]
            for row in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        }
        if "installed_mcps" not in tables:
            return

        expected = {"installed_mcps", "credentials", "integrations"}
        if not expected.issubset(tables):
            return

        if "alembic_version" in tables:
            stamped = conn.execute(text("SELECT version_num FROM alembic_version")).fetchall()
            if stamped:
                return

    command.stamp(_alembic_config(database_url), "head")


def _upgrade_sync(database_url: str) -> None:
    _stamp_sqlite_if_schema_present(database_url)
    command.upgrade(_alembic_config(database_url), "head")


async def upgrade_database(database_url: str) -> None:
    await _prepare_sqlite(database_url)
    await asyncio.to_thread(_upgrade_sync, database_url)
