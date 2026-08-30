import pytest

from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.talib_indicator_provider import (
    TALibIndicatorProvider,
)


def registry() -> IndicatorRegistry:
    result = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        result.register_spec(spec)

    result.register_provider(
        BuiltinStrategyIndicatorProvider()
    )
    result.register_provider(
        TALibIndicatorProvider()
    )

    return result


def test_registry_resolves_spec_provider() -> None:
    result = registry()

    spec = builtin_indicator_specs()["SMA"]

    provider = result.resolve_provider_for(spec)

    assert provider.provider_id == "builtin_strategy"


def test_registry_rejects_incompatible_provider() -> None:
    result = registry()

    spec = builtin_indicator_specs()["SUPERTREND"]

    # Temporarily replace the canonical provider requirement with TA-Lib.
    from dataclasses import replace

    talib_spec = replace(
        spec,
        provider="talib",
    )

    with pytest.raises(
        ValueError,
        match="does not support",
    ):
        result.resolve_provider_for(talib_spec)


def test_registry_rejects_missing_provider() -> None:
    result = IndicatorRegistry()

    spec = builtin_indicator_specs()["SMA"]

    result.register_spec(spec)

    with pytest.raises(
        ValueError,
        match="No provider registered",
    ):
        result.resolve_provider_for(spec)


def test_registry_does_not_change_direct_provider_lookup() -> None:
    result = registry()

    provider = result.resolve_provider(
        "talib"
    )

    assert provider.provider_id == "talib"


def test_registry_resolves_talib_when_spec_requires_it() -> None:
    result = registry()

    from dataclasses import replace

    spec = replace(
        builtin_indicator_specs()["SMA"],
        provider="talib",
    )

    provider = result.resolve_provider_for(spec)

    assert provider.provider_id == "talib"
