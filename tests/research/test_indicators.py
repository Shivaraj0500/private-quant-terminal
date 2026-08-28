from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.research.indicators import (
    calculate_indicator,
    calculate_indicators,
)


def make_candles() -> list[Candle]:
    start = datetime(2026, 1, 1, 9, 15, tzinfo=UTC)

    closes = [
        100.0,
        101.0,
        102.0,
        101.0,
        103.0,
        104.0,
        105.0,
        106.0,
        105.0,
        107.0,
        108.0,
        109.0,
        110.0,
        111.0,
        112.0,
    ]

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=close,
            high=close + 1,
            low=close - 1,
            close=close,
            volume=1000.0,
        )
        for index, close in enumerate(closes)
    ]


@pytest.mark.parametrize(
    "indicator",
    [
        "SMA_5",
        "EMA_5",
        "RSI_5",
        "MOMENTUM_3",
        "ROC_3",
        "RELATIVE_STRENGTH_INDEX_5",
    ],
)
def test_calculate_indicator_returns_float(indicator: str) -> None:
    result = calculate_indicator(indicator, make_candles())

    assert isinstance(result, float)


def test_calculate_sma_uses_latest_value() -> None:
    candles = make_candles()

    result = calculate_indicator("SMA_5", candles)

    assert result == pytest.approx(
        sum(candle.close for candle in candles[-5:]) / 5
    )


def test_calculate_indicators_returns_named_values() -> None:
    result = calculate_indicators(
        ("SMA_5", "EMA_5"),
        make_candles(),
    )

    assert set(result) == {"SMA_5", "EMA_5"}
    assert all(isinstance(value, float) for value in result.values())


def test_empty_indicator_name_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="indicator name cannot be empty",
    ):
        calculate_indicator("", make_candles())


def test_invalid_indicator_specification_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Invalid indicator specification",
    ):
        calculate_indicator("EMA", make_candles())


def test_unsupported_indicator_is_rejected() -> None:
    with pytest.raises(
        KeyError,
        match="Unsupported research indicator",
    ):
        calculate_indicator("MAGIC_20", make_candles())
