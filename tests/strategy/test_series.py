from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.strategy.series import (
    TimeSeries,
    aligned_series,
)


def timestamps(count: int) -> list[datetime]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        start + timedelta(minutes=index)
        for index in range(count)
    ]


def test_aligned_series_preserves_timeline() -> None:
    series = aligned_series(
        timestamps(4),
        [10.0, 20.0],
        warmup=2,
    )

    assert series.values == (
        None,
        None,
        10.0,
        20.0,
    )


def test_series_latest_and_previous() -> None:
    series = TimeSeries(
        timestamps=tuple(timestamps(3)),
        values=(10.0, 20.0, 30.0),
    )

    assert series.latest() == 30.0
    assert series.previous() == 20.0


def test_series_rejects_mismatched_lengths() -> None:
    with pytest.raises(
        ValueError,
        match="matching lengths",
    ):
        TimeSeries(
            timestamps=tuple(timestamps(2)),
            values=(1.0,),
        )


def test_aligned_series_rejects_wrong_warmup() -> None:
    with pytest.raises(
        ValueError,
        match="warmup",
    ):
        aligned_series(
            timestamps(3),
            [1.0, 2.0],
            warmup=0,
        )
