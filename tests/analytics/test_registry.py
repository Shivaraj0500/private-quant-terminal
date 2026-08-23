import pytest

from private_quant_terminal.analytics.registry import IndicatorRegistry


class TestIndicatorRegistry:

    def test_registry_registers_indicator(self) -> None:
        registry = IndicatorRegistry()

        registry.register("sma", object())

        assert "sma" in registry.names()

    def test_registry_returns_names(self) -> None:
        registry = IndicatorRegistry()

        registry.register("rsi", object())
        registry.register("sma", object())

        assert registry.names() == ["rsi", "sma"]

    def test_registry_rejects_empty_name(self) -> None:
        registry = IndicatorRegistry()

        with pytest.raises(ValueError):
            registry.register("", object())

    def test_registry_rejects_duplicate_name(self) -> None:
        registry = IndicatorRegistry()

        registry.register("sma", object())

        with pytest.raises(ValueError):
            registry.register("sma", object())

    def test_registry_rejects_unknown_indicator(self) -> None:
        registry = IndicatorRegistry()

        with pytest.raises(KeyError):
            registry.get("unknown")