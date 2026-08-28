from datetime import datetime, timedelta

import pytest

from private_quant_terminal.data.identity import (
    candle_dataset_hash,
    canonical_candle_json,
    create_dataset_identity,
)
from private_quant_terminal.models import Candle


def make_candle(
    timestamp: datetime,
    close: float = 105.0,
) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=100.0,
        high=110.0,
        low=90.0,
        close=close,
        volume=1000.0,
    )


def test_canonical_candle_json_is_deterministic() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
    ]

    assert canonical_candle_json(candles) == canonical_candle_json(
        candles
    )


def test_dataset_hash_is_deterministic() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
    ]

    first_hash = candle_dataset_hash(candles)
    second_hash = candle_dataset_hash(candles)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_dataset_hash_changes_when_candle_changes() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    original = [
        make_candle(start),
        make_candle(start + timedelta(minutes=5)),
    ]

    changed = [
        make_candle(start),
        make_candle(
            start + timedelta(minutes=5),
            close=106.0,
        ),
    ]

    assert candle_dataset_hash(original) != candle_dataset_hash(
        changed
    )


def test_dataset_identity_contains_metadata() -> None:
    start = datetime(2026, 1, 1, 9, 15)
    latest = start + timedelta(minutes=5)

    candles = [
        make_candle(start),
        make_candle(latest),
    ]

    identity = create_dataset_identity(
        symbol="RELIANCE",
        timeframe="5m",
        candles=candles,
    )

    assert identity.symbol == "RELIANCE"
    assert identity.timeframe == "5m"
    assert identity.start_time == start
    assert identity.end_time == latest
    assert identity.candle_count == 2
    assert len(identity.dataset_hash) == 64


def test_dataset_identity_rejects_empty_symbol() -> None:
    candles = [
        make_candle(datetime(2026, 1, 1, 9, 15)),
    ]

    with pytest.raises(
        ValueError,
        match="symbol cannot be empty",
    ):
        create_dataset_identity(
            symbol="",
            timeframe="5m",
            candles=candles,
        )


def test_dataset_identity_rejects_empty_timeframe() -> None:
    candles = [
        make_candle(datetime(2026, 1, 1, 9, 15)),
    ]

    with pytest.raises(
        ValueError,
        match="timeframe cannot be empty",
    ):
        create_dataset_identity(
            symbol="RELIANCE",
            timeframe="",
            candles=candles,
        )


def test_dataset_identity_reuses_candle_validation() -> None:
    start = datetime(2026, 1, 1, 9, 15)

    candles = [
        make_candle(start + timedelta(minutes=5)),
        make_candle(start),
    ]

    with pytest.raises(
        ValueError,
        match="candles must be ordered by timestamp",
    ):
        create_dataset_identity(
            symbol="RELIANCE",
            timeframe="5m",
            candles=candles,
        )
