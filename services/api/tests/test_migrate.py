import asyncio
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, text

from infrastructure.persistence.migrate import upgrade_database


def test_upgrade_stamps_existing_sqlite_schema_without_version():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "legacy.db"
        url = f"sqlite+aiosqlite:///{db.as_posix()}"
        sync_url = f"sqlite:///{db.as_posix()}"

        engine = create_engine(sync_url)
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE installed_mcps (
                        id CHAR(32) NOT NULL PRIMARY KEY,
                        catalog_id VARCHAR(100) NOT NULL UNIQUE,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        author VARCHAR(255),
                        version VARCHAR(100),
                        docker_image VARCHAR(500) NOT NULL,
                        status VARCHAR(50),
                        container_id VARCHAR(100),
                        container_name VARCHAR(255),
                        installed_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE credentials (
                        id CHAR(32) NOT NULL PRIMARY KEY,
                        mcp_id CHAR(32) NOT NULL,
                        key_name VARCHAR(255) NOT NULL,
                        keyring_ref VARCHAR(500) NOT NULL,
                        created_at DATETIME NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE integrations (
                        id CHAR(32) NOT NULL PRIMARY KEY,
                        client VARCHAR(50) NOT NULL,
                        mcp_id CHAR(32) NOT NULL,
                        config_path VARCHAR(500) NOT NULL,
                        connected_at DATETIME NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)")
            )

        asyncio.run(upgrade_database(url))

        with engine.connect() as conn:
            assert conn.execute(text("SELECT version_num FROM alembic_version")).fetchall() == [
                ("002",)
            ]
