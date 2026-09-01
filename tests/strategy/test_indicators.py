from datetime import UTC, datetime, timedelta

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.expressions import (
    indicator,
)
from private_quant_terminal.strategy.indicators import (
    IndicatorEngine,
    default_indicator_registry,
)


def candles(count: int = 30) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.0 + index,
            volume=1000.0 + index,
        )
        for index in range(count)
    ]


def test_registry_contains_core_indicators() -> None:
    registry = default_indicator_registry()

    assert "EMA" in registry.names()
    assert "SMA" in registry.names()
    assert "RSI" in registry.names()
    assert "ATR" in registry.names()


def test_ema_series_is_aligned_to_candles() -> None:
    data = candles()

    series = IndicatorEngine().calculate(
        indicator(
            "EMA",
            parameters={"period": 10},
        ),
        data,
    )

    assert len(series) == len(data)
    assert all(
        value is not None
        for value in series.values
    )


def test_sma_has_warmup_period() -> None:
    data = candles()

    series = IndicatorEngine().calculate(
        indicator(
            "SMA",
            parameters={"period": 10},
        ),
        data,
    )

    assert len(series) == len(data)
    assert series.values[:9] == (None,) * 9
    assert series.latest() is not None


def test_rsi_has_warmup_period() -> None:
    data = candles()

    series = IndicatorEngine().calculate(
        indicator(
            "RSI",
            parameters={"period": 14},
        ),
        data,
    )

    assert len(series) == len(data)
    assert series.values[:14] == (None,) * 14
    assert series.latest() is not None


def test_unknown_indicator_is_rejected() -> None:
    data = candles()

    try:
        IndicatorEngine().calculate(
            indicator("DOES_NOT_EXIST"),
            data,
        )
    except KeyError as exc:
        assert "Unknown strategy indicator" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown indicator to fail"
        )
