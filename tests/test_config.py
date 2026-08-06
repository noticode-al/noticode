from pathlib import Path

import pytest
from pydantic import ValidationError

from packages.core.config import AppConfig


def test_config_is_created_with_defaults() -> None:
    config = AppConfig()

    assert config.app_name == "Noticode"
    assert config.environment == "development"
    assert config.debug is False
    assert config.workspace_root == Path.cwd()
    assert config.data_directory == Path("data")
    assert config.log_level == "INFO"


def test_config_accepts_custom_values() -> None:
    config = AppConfig(
        environment="production",
        debug=True,
        workspace_root=Path("/srv/noticode"),
        data_directory=Path("/srv/noticode/data"),
        log_level="WARNING",
    )

    assert config.environment == "production"
    assert config.debug is True
    assert config.workspace_root == Path("/srv/noticode")
    assert config.data_directory == Path("/srv/noticode/data")
    assert config.log_level == "WARNING"


def test_config_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        AppConfig(
            unknown_setting="invalid",  # type: ignore[call-arg]
        )


def test_config_rejects_short_app_name() -> None:
    with pytest.raises(ValidationError):
        AppConfig(app_name="N")
