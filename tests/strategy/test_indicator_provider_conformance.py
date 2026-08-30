from datetime import datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.builtin_indicator_provider import (
    BuiltinStrategyIndicatorProvider,
)
from private_quant_terminal.strategy.builtin_indicator_specs import (
    builtin_indicator_specs,
)
from private_quant_terminal.strategy.talib_indicator_provider import (
    TALibIndicatorProvider,
)


def candles(count: int = 60) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15)

    closes = [
        100.0, 101.2, 99.8, 102.5, 101.7,
        103.4, 104.1, 102.8, 105.2, 106.0,
        104.9, 107.3, 108.1, 106.6, 109.4,
        110.2, 108.7, 111.5, 112.1, 110.8,
        113.6, 114.4, 112.9, 115.7, 116.3,
        114.8, 117.1, 118.0, 116.5, 119.2,
        120.1, 118.7, 121.4, 122.0, 120.6,
        123.3, 124.1, 122.8, 125.5, 126.2,
    ]

    values = (closes * ((count + len(closes) - 1) // len(closes)))[:count]

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=close - 0.3,
            high=close + 0.8,
            low=close - 0.9,
            close=close,
            volume=1000.0 + index * 25.0,
        )
        for index, close in enumerate(values)
    ]


@pytest.fixture
def specs():
    return builtin_indicator_specs()


@pytest.fixture
def builtin():
    return BuiltinStrategyIndicatorProvider()


@pytest.fixture
def talib():
    return TALibIndicatorProvider()


@pytest.mark.parametrize(
    ("indicator_id", "parameters"),
    [
        ("SMA", {"period": 5}),
        ("RSI", {"period": 5}),
        ("MOMENTUM", {"period": 5}),
        ("ROC", {"period": 5}),
    ],
)
def test_shared_indicators_are_numerically_conformant(
    indicator_id,
    parameters,
    specs,
    builtin,
    talib,
):
    spec = specs[indicator_id]

    builtin_series = builtin.calculate(
        spec,
        candles(),
        parameters,
    ).output("value")

    talib_series = talib.calculate(
        spec,
        candles(),
        parameters,
    ).output("value")

    assert builtin_series.timestamps == talib_series.timestamps

    for left, right in zip(
        builtin_series.values,
        talib_series.values,
    ):
        if left is None or right is None:
            assert left is None and right is None
        else:
            assert left == pytest.approx(
                right,
                rel=1e-10,
                abs=1e-10,
            )


def test_ema_provider_warmup_is_distinct_from_canonical_warmup(
    specs,
    builtin,
    talib,
):
    spec = specs["EMA"]
    source = candles()

    builtin_series = builtin.calculate(
        spec,
        source,
        {"period": 5},
    ).output("value")

    talib_series = talib.calculate(
        spec,
        source,
        {"period": 5},
    ).output("value")

    # TA-Lib has provider-native warmup.
    assert all(
        value is None
        for value in talib_series.values[:4]
    )

    # The built-in provider may emit raw values earlier.
    assert all(
        value is not None
        for value in builtin_series.values[:4]
    )

    # Provider-native numerical values are not required to match.
    assert builtin_series.values[4] != pytest.approx(
        talib_series.values[4],
        rel=1e-10,
        abs=1e-10,
    )


def test_atr_is_not_required_to_match_talib(
    specs,
    builtin,
    talib,
):
    spec = specs["ATR"]
    source = candles()

    builtin_series = builtin.calculate(
        spec,
        source,
        {"period": 5},
    ).output("value")

    talib_series = talib.calculate(
        spec,
        source,
        {"period": 5},
    ).output("value")

    assert builtin_series.timestamps == talib_series.timestamps

    # ATR has intentionally different smoothing semantics between
    # the canonical built-in implementation and TA-Lib.
    assert builtin_series.values[6] != pytest.approx(
        talib_series.values[6],
        rel=1e-10,
        abs=1e-10,
    )


def test_obv_is_not_required_to_match_talib(
    specs,
    builtin,
    talib,
):
    spec = specs["OBV"]
    source = candles()

    builtin_series = builtin.calculate(
        spec,
        source,
        {},
    ).output("value")

    talib_series = talib.calculate(
        spec,
        source,
        {},
    ).output("value")

    assert builtin_series.timestamps == talib_series.timestamps

    # The canonical built-in implementation and TA-Lib use
    # different starting/cumulative semantics.
    assert builtin_series.values != talib_series.values


def test_builtin_provider_supports_all_canonical_indicators(
    specs,
    builtin,
):
    for spec in specs.values():
        assert builtin.supports(spec) is True


def test_talib_provider_supports_only_declared_talib_indicators(
    specs,
    talib,
):
    talib_supported = {
        "SMA",
        "EMA",
        "RSI",
        "ATR",
        "MOMENTUM",
        "ROC",
        "OBV",
    }

    for indicator_id, spec in specs.items():
        assert talib.supports(spec) is (
            indicator_id in talib_supported
        )
