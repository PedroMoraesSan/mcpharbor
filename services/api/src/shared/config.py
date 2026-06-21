"""User-level configuration paths and bootstrap for bundled/desktop runs."""

from __future__ import annotations

import contextlib
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".mcpharbour"
CONFIG_FILE = CONFIG_DIR / ".env"
LOG_DIR = CONFIG_DIR / "logs"
API_LOG_FILE = LOG_DIR / "api.log"
SQLITE_DB_FILE = CONFIG_DIR / "mcpharbour.db"

POSTGRES_DEFAULT_URL = "postgresql+asyncpg://mcpharbour:mcpharbour@localhost:5432/mcpharbour"

_SEED_KEYS = ("DATABASE_URL", "DOCKER_HOST", "MCPHARBOR_LOG_LEVEL")


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def is_desktop_mode() -> bool:
    return is_frozen() or os.environ.get("MCPHARBOR_ENV") == "production"


def sqlite_database_url(db_path: Path | None = None) -> str:
    path = (db_path or SQLITE_DB_FILE).resolve()
    return f"sqlite+aiosqlite:///{path.as_posix()}"


def default_database_url() -> str:
    if is_desktop_mode():
        return sqlite_database_url()
    return POSTGRES_DEFAULT_URL


def _parse_env_lines(content: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pnpm-workspace.yaml").is_file():
            return parent
    return here.parents[4]


def _dev_env_candidates() -> list[Path]:
    if is_frozen():
        return []

    candidates: list[Path] = []
    repo_root = _repo_root()
    candidates.append(repo_root / ".env")
    candidates.append(Path.cwd() / ".env")
    candidates.append(Path.cwd().parent / ".env")
    return [path for path in candidates if path.is_file()]


def _seed_from_dev_env() -> dict[str, str]:
    for path in _dev_env_candidates():
        values = _parse_env_lines(path.read_text(encoding="utf-8"))
        seeded = {key: values[key] for key in _SEED_KEYS if key in values}
        if seeded:
            return seeded
    return {}


def _render_env(values: dict[str, str]) -> str:
    base = {
        "MCPHARBOR_ENV": "production" if is_desktop_mode() else "development",
        "MCPHARBOR_LOG_LEVEL": "info",
        "MCPHARBOR_API_HOST": "127.0.0.1",
        "MCPHARBOR_API_PORT": "8741",
        "DATABASE_URL": default_database_url(),
    }
    base.update(values)
    lines = [
        "# MCP Harbor user configuration",
        "# Desktop app uses a local SQLite database automatically.",
    ]
    for key in (
        "MCPHARBOR_ENV",
        "MCPHARBOR_LOG_LEVEL",
        "MCPHARBOR_API_HOST",
        "MCPHARBOR_API_PORT",
        "DATABASE_URL",
        "DOCKER_HOST",
    ):
        if key in base:
            lines.append(f"{key}={base[key]}")
    return "\n".join(lines) + "\n"


def _maybe_migrate_desktop_database_url() -> None:
    """Move legacy desktop installs from external Postgres to bundled SQLite."""
    if not is_desktop_mode() or not CONFIG_FILE.exists():
        return

    try:
        values = _parse_env_lines(CONFIG_FILE.read_text(encoding="utf-8"))
    except OSError:
        return

    current = values.get("DATABASE_URL", "")
    if not current.startswith("postgresql"):
        return

    values["DATABASE_URL"] = default_database_url()
    with contextlib.suppress(OSError):
        CONFIG_FILE.write_text(_render_env(values), encoding="utf-8")


def ensure_runtime_environment() -> None:
    """Prepare process env for desktop/GUI launches (minimal PATH, Docker helpers)."""
    if sys.platform == "darwin":
        extra_paths = [
            "/Applications/Docker.app/Contents/Resources/bin",
            "/usr/local/bin",
            "/opt/homebrew/bin",
        ]
        current = os.environ.get("PATH", "")
        parts = [p for p in current.split(os.pathsep) if p]
        for path in extra_paths:
            if Path(path).is_dir() and path not in parts:
                parts.insert(0, path)
        if parts:
            os.environ["PATH"] = os.pathsep.join(parts)


def ensure_user_config() -> Path:
    """Create ~/.mcpharbour/.env on first run (desktop bundle has no repo .env)."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        return CONFIG_FILE

    if CONFIG_FILE.exists():
        _maybe_migrate_desktop_database_url()
        return CONFIG_FILE

    seeded = _seed_from_dev_env()
    if is_desktop_mode():
        seeded["DATABASE_URL"] = default_database_url()

    with contextlib.suppress(OSError):
        CONFIG_FILE.write_text(_render_env(seeded), encoding="utf-8")
    return CONFIG_FILE


def env_files() -> tuple[str, ...]:
    ensure_user_config()
    files: list[str] = [str(CONFIG_FILE)]
    if not is_frozen() and not is_desktop_mode():
        files.extend([".env", "../.env"])
    return tuple(files)


def database_kind(database_url: str) -> str:
    if database_url.startswith("sqlite"):
        return "sqlite"
    if database_url.startswith("postgresql"):
        return "postgresql"
    return "other"
