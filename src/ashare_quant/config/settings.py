"""Typed project settings loaded from versioned configuration files.

The project intentionally centralizes configuration here. Application modules should use
``get_settings()`` instead of direct environment access so that defaults, validation, and
auditability remain consistent.
"""

from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ashare_quant.utils.exceptions import ConfigurationError

DEFAULT_CONFIG_FILE = Path("configs/settings.toml")
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class AppSettings(BaseSettings):
    """Application-level settings."""

    name: str = "A-Share Quant Research Platform"
    environment: str = "development"

    model_config = SettingsConfigDict(extra="forbid")


class LoggingSettings(BaseSettings):
    """Logging settings for console and rotating file handlers."""

    level: LogLevel = "INFO"
    console_enabled: bool = True
    file_enabled: bool = True
    log_dir: Path = Path("logs")
    log_file: str = "ashare_quant.log"
    max_bytes: int = Field(default=1_048_576, ge=1)
    backup_count: int = Field(default=5, ge=0)

    model_config = SettingsConfigDict(extra="forbid")


class Settings(BaseSettings):
    """Top-level settings object."""

    app: AppSettings = Field(default_factory=AppSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    model_config = SettingsConfigDict(extra="forbid")


def _load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML configuration file with a project-specific error."""

    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")
    try:
        with path.open("rb") as config_file:
            data = tomllib.load(config_file)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"Invalid TOML configuration: {path}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Configuration root must be a table: {path}")
    return data


@lru_cache(maxsize=1)
def get_settings(config_file: Path | str = DEFAULT_CONFIG_FILE) -> Settings:
    """Return validated settings loaded from ``configs/``.

    Args:
        config_file: Path to the TOML settings file. Defaults to the repository's
            versioned `configs/settings.toml`.
    """

    path = Path(config_file)
    return Settings.model_validate(_load_toml(path))
