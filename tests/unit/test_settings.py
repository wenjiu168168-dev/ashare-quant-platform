from pathlib import Path

import pytest

from ashare_quant.config.settings import get_settings
from ashare_quant.utils.exceptions import ConfigurationError


def test_get_settings_loads_versioned_config() -> None:
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app.name == "A-Share Quant Research Platform"
    assert settings.app.environment == "development"
    assert settings.logging.level == "INFO"
    assert settings.logging.log_dir == Path("logs")


def test_get_settings_raises_project_error_for_missing_file(tmp_path: Path) -> None:
    get_settings.cache_clear()

    with pytest.raises(ConfigurationError):
        get_settings(tmp_path / "missing.toml")
