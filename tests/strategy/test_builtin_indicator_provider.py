from datetime import datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)


def candles(count: int = 40) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.5 + index,
            volume=1000.0 + index * 10,
        )
        for index in range(count)
    ]


def test_provider_identity() -> None:
    provider = BuiltinStrategyIndicatorProvider()

    assert provider.provider_id == "builtin_strategy"


def test_provider_supports_builtin_specs() -> None:
    provider = BuiltinStrategyIndicatorProvider()

    for spec in builtin_indicator_specs().values():
        assert provider.provider_id == spec.provider
        assert spec.provider == "builtin_strategy"


@pytest.mark.parametrize(
    "indicator_id,parameters",
    [
        ("SMA", {"period": 5}),
        ("EMA", {"period": 5}),
        ("RSI", {"period": 5}),
        ("ATR", {"period": 5}),
        ("SUPERTREND", {"period": 5, "multiplier": 2.0}),
        ("MOMENTUM", {"period": 5}),
        ("ROC", {"period": 5}),
        ("VOLUME_SMA", {"period": 5}),
        ("RELATIVE_VOLUME", {"period": 5}),
        ("OBV", {}),
    ],
)
def test_provider_calculates_all_builtin_indicators(
    indicator_id: str,
    parameters: dict[str, object],
) -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()[indicator_id]

    result = provider.calculate(
        spec,
        candles(),
        parameters,
    )

    assert "value" in result.outputs
    assert len(result.output("value")) == len(candles())


def test_provider_preserves_timestamps() -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()["SMA"]

    source = candles()

    result = provider.calculate(
        spec,
        source,
        {"period": 5},
    )

    series = result.output("value")

    assert series.timestamps == tuple(
        candle.timestamp
        for candle in source
    )


def test_provider_rejects_wrong_provider() -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()["SMA"]

    from dataclasses import replace

    foreign_spec = replace(
        spec,
        provider="external",
    )

    with pytest.raises(ValueError, match="Unsupported provider"):
        provider.calculate(
            foreign_spec,
            candles(),
            {"period": 5},
        )


def test_provider_rejects_boolean_parameter() -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()["SMA"]

    with pytest.raises(ValueError, match="cannot be boolean"):
        provider.calculate(
            spec,
            candles(),
            {"period": True},
        )


def test_provider_rejects_non_numeric_parameter() -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()["SMA"]

    with pytest.raises(ValueError, match="must be numeric"):
        provider.calculate(
            spec,
            candles(),
            {"period": "5"},
        )


def test_provider_uses_default_parameters() -> None:
    provider = BuiltinStrategyIndicatorProvider()
    spec = builtin_indicator_specs()["SMA"]

    result = provider.calculate(
        spec,
        candles(),
        {},
    )

    assert result.output("value").latest() is not None
