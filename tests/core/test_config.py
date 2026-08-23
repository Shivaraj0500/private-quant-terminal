from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from private_quant_terminal.core.config import Settings, settings


class TestSettings:
    def test_default_settings_values(self) -> None:
        config = Settings()

        assert config.project_name == "Private Quant Terminal"
        assert config.environment == "development"
        assert config.debug is True
        assert config.data_dir == Path("data")
        assert config.raw_data_dir == Path("data/raw")
        assert config.processed_data_dir == Path("data/processed")
        assert config.reports_dir == Path("reports")

    def test_settings_supports_custom_values(self) -> None:
        config = Settings(
            project_name="Test Terminal",
            environment="production",
            debug=False,
            data_dir=Path("custom_data"),
            raw_data_dir=Path("custom_data/raw"),
            processed_data_dir=Path("custom_data/processed"),
            reports_dir=Path("custom_reports"),
        )

        assert config.project_name == "Test Terminal"
        assert config.environment == "production"
        assert config.debug is False
        assert config.data_dir == Path("custom_data")
        assert config.raw_data_dir == Path("custom_data/raw")
        assert config.processed_data_dir == Path("custom_data/processed")
        assert config.reports_dir == Path("custom_reports")

    def test_settings_is_immutable(self) -> None:
        config = Settings()

        with pytest.raises(FrozenInstanceError):
            config.environment = "production"

    def test_global_settings_is_default_settings_instance(self) -> None:
        assert isinstance(settings, Settings)
        assert settings == Settings()

    def test_global_settings_is_immutable(self) -> None:
        with pytest.raises(FrozenInstanceError):
            settings.debug = False
