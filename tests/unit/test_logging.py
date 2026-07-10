import logging
from pathlib import Path

from ashare_quant.config.settings import LoggingSettings
from ashare_quant.utils.logging import configure_logging, get_logger


def test_configure_logging_adds_console_and_rotating_file_handlers(tmp_path: Path) -> None:
    settings = LoggingSettings(log_dir=tmp_path, log_file="test.log", level="DEBUG")

    logger = configure_logging(settings)

    assert logger.name == "ashare_quant"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
    logger.debug("logging smoke test")
    assert (tmp_path / "test.log").exists()


def test_get_logger_uses_project_namespace() -> None:
    logger = get_logger("unit.test")

    assert logger.name == "ashare_quant.unit.test"
