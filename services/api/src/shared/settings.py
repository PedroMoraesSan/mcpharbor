from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.config import (
    CONFIG_DIR,
    SQLITE_DB_FILE,
    default_database_url,
    env_files,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCPHARBOR_",
        env_file=env_files(),
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "info"
    api_host: str = "127.0.0.1"
    api_port: int = 8741
    database_url: str = Field(
        default_factory=default_database_url,
        validation_alias="DATABASE_URL",
    )
    docker_host: str | None = Field(default=None, validation_alias="DOCKER_HOST")
    data_dir: Path = CONFIG_DIR
    cursor_config_path: Path = Path.home() / ".cursor" / "mcp.json"
    wrapper_bin_dir: Path = CONFIG_DIR / "bin"

    @property
    def database_path(self) -> Path | None:
        if self.database_url.startswith("sqlite"):
            return SQLITE_DB_FILE
        return None


settings = Settings()
