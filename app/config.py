"""Application configuration sourced exclusively from environment variables."""

from dataclasses import dataclass
from os import getenv


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "TaskFlow API"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./taskflow.db"
    log_level: str = "INFO"
    simulate_failure: bool = False

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            version=getenv("APP_VERSION", "1.0.0"),
            database_url=getenv("DATABASE_URL", "sqlite:///./taskflow.db"),
            log_level=getenv("LOG_LEVEL", "INFO"),
            simulate_failure=_as_bool(getenv("SIMULATE_FAILURE")),
        )


settings = Settings.from_environment()
