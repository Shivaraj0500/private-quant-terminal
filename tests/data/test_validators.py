from datetime import datetime, timedelta

import pytest

from private_quant_terminal.data.validators import validate_candles
from private_quant_terminal.models import Candle


def make_candle(timestamp: datetime) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=1000.0,
    )


def test_validate_candles_accepts_single_candle() -> None:
    candle = make_candle(datetime(2026, 1, 1, 9, 15))

    validate_candles([candle])


def test_validate_candles_accepts_ordered_candles() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=1)),
        make_candle(start + timedelta(minutes=2)),
    ]

    validate_candles(candles)


def test_validate_candles_rejects_empty_collection() -> None:
    with pytest.raises(
        ValueError,
        match="candle collection cannot be empty",
    ):
        validate_candles([])


def test_validate_candles_rejects_unordered_timestamps() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start + timedelta(minutes=1)),
        make_candle(start),
    ]

    with pytest.raises(
        ValueError,
        match="candles must be ordered by timestamp",
    ):
        validate_candles(candles)


def test_validate_candles_rejects_duplicate_timestamps() -> None:
    timestamp = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(timestamp),
        make_candle(timestamp),
    ]

    with pytest.raises(
        ValueError,
        match="duplicate candle timestamps are not allowed",
    ):
        validate_candles(candles)


def test_validate_candles_accepts_multiple_unique_ordered_timestamps() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
        make_candle(start + timedelta(minutes=10)),
        make_candle(start + timedelta(minutes=15)),
    ]

    validate_candles(candles)