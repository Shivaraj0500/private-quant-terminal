import pytest

from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.indicator_providers import (
    IndicatorProvider,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)


def registry() -> IndicatorRegistry:
    result = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        result.register_spec(spec)

    result.register_provider(BuiltinStrategyIndicatorProvider())

    return result


def test_register_and_resolve_by_id() -> None:
    result = registry()

    spec = result.resolve_spec("SMA")

    assert spec.id == "SMA"
    assert spec.version == "1.0.0"


def test_resolution_is_case_insensitive() -> None:
    result = registry()

    assert result.resolve_spec("sma").id == "SMA"
    assert result.resolve_spec("SMA").id == "SMA"


def test_unknown_indicator_fails() -> None:
    result = registry()

    with pytest.raises(KeyError, match="Unknown indicator"):
        result.resolve_spec("DOES_NOT_EXIST")


def test_duplicate_indicator_id_fails() -> None:
    result = IndicatorRegistry()

    spec = builtin_indicator_specs()["SMA"]

    result.register_spec(spec)

    with pytest.raises(ValueError, match="already registered"):
        result.register_spec(spec)


def test_provider_registration() -> None:
    result = IndicatorRegistry()

    provider = BuiltinStrategyIndicatorProvider()

    result.register_provider(provider)

    assert result.resolve_provider("builtin_strategy") is provider


def test_unknown_provider_fails() -> None:
    result = IndicatorRegistry()

    with pytest.raises(KeyError, match="Unknown indicator provider"):
        result.resolve_provider("missing_provider")


def test_resolve_provider_for_indicator() -> None:
    result = registry()

    provider = result.resolve_provider_for(result.resolve_spec("SMA"))

    assert provider.provider_id == "builtin_strategy"


def test_missing_indicator_provider_fails() -> None:
    result = IndicatorRegistry()

    result.register_spec(builtin_indicator_specs()["SMA"])

    with pytest.raises(
        ValueError,
        match="No provider registered",
    ):
        result.resolve_provider_for(result.resolve_spec("SMA"))


def test_duplicate_provider_id_fails() -> None:
    result = IndicatorRegistry()

    first = BuiltinStrategyIndicatorProvider()
    second = BuiltinStrategyIndicatorProvider()

    result.register_provider(first)

    with pytest.raises(ValueError, match="already registered"):
        result.register_provider(second)


def test_missing_required_provider_is_rejected() -> None:
    result = IndicatorRegistry()

    result.register_spec(builtin_indicator_specs()["SMA"])

    class WrongProvider(IndicatorProvider):
        @property
        def provider_id(self) -> str:
            return "wrong_provider"

        def calculate(
            self,
            spec,
            candles,
            parameters,
        ):
            raise AssertionError("Provider should not be called")

    result.register_provider(WrongProvider())

    with pytest.raises(
        ValueError,
        match="No provider registered",
    ):
        result.resolve_provider_for(result.resolve_spec("SMA"))


def test_catalog_returns_registered_specs() -> None:
    result = registry()

    catalog = result.specs()

    assert set(catalog) == {
        "SMA",
        "EMA",
        "RSI",
        "ATR",
        "BBANDS",
        "SUPERTREND",
        "MOMENTUM",
        "ROC",
        "VOLUME_SMA",
        "RELATIVE_VOLUME",
        "OBV",
    }


def test_provider_registry_returns_registered_providers() -> None:
    result = registry()

    providers = result.providers()

    assert list(providers) == ["builtin_strategy"]


def test_alias_resolution() -> None:
    result = IndicatorRegistry()

    from dataclasses import replace

    spec = replace(
        builtin_indicator_specs()["SMA"],
        aliases=("SIMPLE_MA",),
    )

    result.register_spec(spec)

    assert result.resolve_spec("SIMPLE_MA").id == "SMA"


def test_duplicate_alias_fails() -> None:
    result = IndicatorRegistry()

    from dataclasses import replace

    first = replace(
        builtin_indicator_specs()["SMA"],
        aliases=("MOVING_AVERAGE",),
    )

    second = replace(
        builtin_indicator_specs()["EMA"],
        aliases=("MOVING_AVERAGE",),
    )

    result.register_spec(first)

    with pytest.raises(ValueError, match="already registered"):
        result.register_spec(second)
