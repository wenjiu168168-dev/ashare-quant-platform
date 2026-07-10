"""Central logging setup for console and rotating file output."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ashare_quant.config.settings import LoggingSettings, get_settings

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(settings: LoggingSettings | None = None) -> logging.Logger:
    """Configure project logging and return the root project logger."""

    logging_settings = settings or get_settings().logging
    logger = logging.getLogger("ashare_quant")
    logger.setLevel(logging_settings.level)
    logger.propagate = False
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT)

    if logging_settings.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging_settings.level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if logging_settings.file_enabled:
        log_dir = Path(logging_settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / logging_settings.log_file,
            maxBytes=logging_settings.max_bytes,
            backupCount=logging_settings.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging_settings.level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the project namespace."""

    return logging.getLogger(f"ashare_quant.{name}")
