from datetime import UTC, datetime, timedelta

import pytest

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
from private_quant_terminal.strategy.expressions import indicator
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.indicators import (
    IndicatorEngine,
)


def candles(count: int = 60) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

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


def registry() -> IndicatorRegistry:
    registry = IndicatorRegistry()

    for spec in builtin_indicator_specs().values():
        registry.register_spec(spec)

    registry.register_provider(
        BuiltinStrategyIndicatorProvider()
    )

    return registry


def engine() -> CanonicalIndicatorEngine:
    return CanonicalIndicatorEngine(
        registry()
    )


@pytest.mark.parametrize(
    "name,parameters",
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
def test_canonical_engine_calculates_builtin_indicator(
    name: str,
    parameters: dict[str, float],
) -> None:
    result = engine().calculate(
        indicator(
            name,
            parameters=parameters,
        ),
        candles(),
    )

    series = result.output("value")

    assert len(series) == len(candles())


@pytest.mark.parametrize(
    "name,parameters",
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
def test_canonical_matches_existing_indicator_engine(
    name: str,
    parameters: dict[str, float],
) -> None:
    source = candles()

    canonical = engine().calculate(
        indicator(
            name,
            parameters=parameters,
        ),
        source,
    ).output("value")

    existing = IndicatorEngine().calculate(
        indicator(
            name,
            parameters=parameters,
        ),
        source,
    )

    assert canonical.timestamps == existing.timestamps

    from private_quant_terminal.strategy.indicator_warmup import (
        canonical_warmup,
    )

    warmup = canonical_warmup(
        name,
        parameters,
    )

    assert all(
        canonical.value_at(index) is None
        for index in range(min(warmup, len(canonical)))
    )

    assert canonical.values[warmup:] == existing.values[warmup:]


def test_unknown_indicator_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unknown indicator"):
        engine().calculate(
            indicator("DOES_NOT_EXIST"),
            candles(),
        )


def test_empty_candles_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="candles cannot be empty",
    ):
        engine().calculate(
            indicator(
                "SMA",
                parameters={"period": 5},
            ),
            [],
        )
