"""App settings loaded from environment variables and .env."""

from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Env = Literal["development", "test", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class Settings(BaseSettings):
    """Settings for the app.

    Each field reads the env var TODO_<FIELD_NAME>.
    For example, log_level reads TODO_LOG_LEVEL.
    """

    model_config = SettingsConfigDict(
        env_prefix="TODO_",
        env_file=".env",
        extra="ignore",
        # Allow Settings(env=...) in code, not only the alias.
        validate_by_name=True,
    )

    app_name: str = "Todo API"
    # `fastapi dev` sets FASTAPI_ENV=development, so we read it here.
    # We use "production" as a safe default.
    env: Env = Field(
        default="production",
        validation_alias=AliasChoices("FASTAPI_ENV", "TODO_ENV"),
    )
    # When True, FastAPI returns a traceback page for unhandled errors.
    # Never turn this on in production.
    debug: bool = False
    log_level: LogLevel = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return one shared Settings object."""
    return Settings()
