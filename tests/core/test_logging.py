import logging
from unittest.mock import patch

from private_quant_terminal.core.logging import configure_logging


class TestConfigureLogging:
    def test_configure_logging_uses_default_info_level(self) -> None:
        with patch(
            "private_quant_terminal.core.logging.logging.basicConfig"
        ) as mock_basic_config:
            configure_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format=(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
        )

    def test_configure_logging_uses_custom_level(self) -> None:
        with patch(
            "private_quant_terminal.core.logging.logging.basicConfig"
        ) as mock_basic_config:
            configure_logging(logging.DEBUG)

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format=(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
        )

    def test_configure_logging_accepts_warning_level(self) -> None:
        with patch(
            "private_quant_terminal.core.logging.logging.basicConfig"
        ) as mock_basic_config:
            configure_logging(logging.WARNING)

        mock_basic_config.assert_called_once_with(
            level=logging.WARNING,
            format=(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
        )