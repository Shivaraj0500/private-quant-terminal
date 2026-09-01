from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import indicator
from private_quant_terminal.strategy.indicators import (
    IndicatorEngine,
    default_indicator_registry,
)


def candles(closes: list[float]) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=close,
            high=close + 2.0,
            low=close - 2.0,
            close=close,
            volume=1000.0,
        )
        for index, close in enumerate(closes)
    ]


def test_supertrend_is_registered() -> None:
    registry = default_indicator_registry()

    assert "SUPERTREND" in registry.names()


def test_supertrend_is_aligned() -> None:
    data = candles(
        [
            100, 101, 102, 103, 104,
            105, 106, 107, 108, 109,
            110, 111, 112, 113, 114,
        ]
    )

    series = IndicatorEngine().calculate(
        indicator(
            "SUPERTREND",
            parameters={
                "period": 10,
                "multiplier": 2,
            },
        ),
        data,
    )

    assert len(series) == len(data)
    assert series.values[:9] == (None,) * 9
    assert all(
        value is not None
        for value in series.values[9:]
    )


def test_supertrend_rejects_invalid_multiplier() -> None:
    data = candles(list(range(100, 115)))

    with pytest.raises(
        ValueError,
        match="multiplier",
    ):
        IndicatorEngine().calculate(
            indicator(
                "SUPERTREND",
                parameters={
                    "period": 10,
                    "multiplier": 0,
                },
            ),
            data,
        )


def test_supertrend_parameter_changes_output() -> None:
    data = candles(
        [
            100, 102, 101, 104, 103,
            106, 105, 108, 107, 110,
            109, 112, 111, 114, 113,
        ]
    )

    engine = IndicatorEngine()

    fast = engine.calculate(
        indicator(
            "SUPERTREND",
            parameters={
                "period": 5,
                "multiplier": 1,
            },
        ),
        data,
    )

    slow = engine.calculate(
        indicator(
            "SUPERTREND",
            parameters={
                "period": 10,
                "multiplier": 3,
            },
        ),
        data,
    )

    assert fast.latest() != slow.latest()


def test_atr_is_now_a_historical_strategy_series() -> None:
    data = candles(list(range(100, 115)))

    series = IndicatorEngine().calculate(
        indicator(
            "ATR",
            parameters={"period": 5},
        ),
        data,
    )

    assert len(series) == len(data)
    assert series.values[:4] == (None,) * 4
    assert all(
        value is not None
        for value in series.values[4:]
    )
