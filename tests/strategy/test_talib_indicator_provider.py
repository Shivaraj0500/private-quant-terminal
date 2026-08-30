from datetime import datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.talib_indicator_provider import (
    TALibIndicatorProvider,
)


def candles(count: int = 60) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index * 0.4,
            high=101.0 + index * 0.5,
            low=99.0 + index * 0.3,
            close=100.2 + index * 0.45,
            volume=1000.0 + index * 20.0,
        )
        for index in range(count)
    ]


@pytest.fixture
def provider() -> TALibIndicatorProvider:
    return TALibIndicatorProvider()


@pytest.mark.parametrize(
    "name,parameters",
    [
        ("SMA", {"period": 5}),
        ("EMA", {"period": 5}),
        ("RSI", {"period": 5}),
        ("ATR", {"period": 5}),
        ("MOMENTUM", {"period": 5}),
        ("ROC", {"period": 5}),
        ("OBV", {}),
    ],
)
def test_provider_calculates_supported_indicators(
    provider: TALibIndicatorProvider,
    name: str,
    parameters: dict[str, float],
) -> None:
    spec = builtin_indicator_specs()[name]

    result = provider.calculate(
        spec,
        candles(),
        parameters,
    )

    series = result.output("value")

    assert len(series) == len(candles())
    assert series.timestamps == tuple(
        candle.timestamp for candle in candles()
    )


def test_provider_id(
    provider: TALibIndicatorProvider,
) -> None:
    assert provider.provider_id == "talib"


@pytest.mark.parametrize(
    "name",
    [
        "SUPERTREND",
        "VOLUME_SMA",
        "RELATIVE_VOLUME",
    ],
)
def test_unsupported_indicators_are_rejected(
    provider: TALibIndicatorProvider,
    name: str,
) -> None:
    spec = builtin_indicator_specs()[name]

    with pytest.raises(
        ValueError,
        match="does not support",
    ):
        provider.calculate(
            spec,
            candles(),
            {},
        )


def test_missing_period_is_rejected(
    provider: TALibIndicatorProvider,
) -> None:
    spec = builtin_indicator_specs()["SMA"]

    with pytest.raises(
        ValueError,
        match="period",
    ):
        provider.calculate(
            spec,
            candles(),
            {},
        )


def test_invalid_period_is_rejected(
    provider: TALibIndicatorProvider,
) -> None:
    spec = builtin_indicator_specs()["SMA"]

    with pytest.raises(
        ValueError,
        match="period",
    ):
        provider.calculate(
            spec,
            candles(),
            {"period": 0},
        )


def test_empty_candles_are_rejected(
    provider: TALibIndicatorProvider,
) -> None:
    spec = builtin_indicator_specs()["SMA"]

    with pytest.raises(
        ValueError,
        match="candles",
    ):
        provider.calculate(
            spec,
            [],
            {"period": 5},
        )
