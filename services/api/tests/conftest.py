import asyncio
import os
import tempfile
from pathlib import Path

_tmp_dir = tempfile.mkdtemp(prefix="mcpharbour-pytest-")
_db_path = Path(_tmp_dir) / "pytest.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_db_path.as_posix()}"
os.environ["MCPHARBOR_SKIP_DB_MIGRATE"] = "1"

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def test_database_url():
    return os.environ["DATABASE_URL"]


@pytest.fixture(scope="session", autouse=True)
def migrated_database(test_database_url):
    from infrastructure.persistence.migrate import upgrade_database

    asyncio.run(upgrade_database(test_database_url))
