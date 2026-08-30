from datetime import datetime, timedelta

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.canonical_indicator_engine import (
    CanonicalIndicatorEngine,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)


def candles(count: int = 30) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15)

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


def engine() -> CanonicalIndicatorEngine:
    registry = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        registry.register_spec(spec)

    registry.register_provider(
        BuiltinStrategyIndicatorProvider()
    )

    return CanonicalIndicatorEngine(registry)


def test_ema_canonical_readiness_is_parameter_aware() -> None:
    result = engine().calculate(
        __import__(
            "private_quant_terminal.strategy.expressions",
            fromlist=["indicator"],
        ).indicator(
            "EMA",
            parameters={"period": 5},
        ),
        candles(),
    ).output("value")

    assert result.value_at(0) is None
    assert result.value_at(1) is None
    assert result.value_at(2) is None
    assert result.value_at(3) is None
    assert result.value_at(4) is not None


def test_sma_canonical_readiness_is_preserved() -> None:
    result = engine().calculate(
        __import__(
            "private_quant_terminal.strategy.expressions",
            fromlist=["indicator"],
        ).indicator(
            "SMA",
            parameters={"period": 5},
        ),
        candles(),
    ).output("value")

    assert result.value_at(0) is None
    assert result.value_at(3) is None
    assert result.value_at(4) is not None


def test_rsi_canonical_readiness_is_preserved() -> None:
    result = engine().calculate(
        __import__(
            "private_quant_terminal.strategy.expressions",
            fromlist=["indicator"],
        ).indicator(
            "RSI",
            parameters={"period": 5},
        ),
        candles(),
    ).output("value")

    assert all(
        result.value_at(index) is None
        for index in range(5)
    )
    assert result.value_at(5) is not None


def test_canonical_series_keeps_original_timestamps() -> None:
    source = candles()

    result = engine().calculate(
        __import__(
            "private_quant_terminal.strategy.expressions",
            fromlist=["indicator"],
        ).indicator(
            "EMA",
            parameters={"period": 5},
        ),
        source,
    ).output("value")

    assert result.timestamps == tuple(
        candle.timestamp
        for candle in source
    )


def test_canonical_warmup_does_not_change_series_length() -> None:
    source = candles()

    result = engine().calculate(
        __import__(
            "private_quant_terminal.strategy.expressions",
            fromlist=["indicator"],
        ).indicator(
            "EMA",
            parameters={"period": 5},
        ),
        source,
    ).output("value")

    assert len(result) == len(source)
