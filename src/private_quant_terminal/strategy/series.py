from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isnan
from typing import Sequence


@dataclass(frozen=True)
class TimeSeries:
    """A timestamp-aligned immutable numerical series."""

    timestamps: tuple[datetime, ...]
    values: tuple[float | None, ...]

    def __post_init__(self) -> None:
        if len(self.timestamps) != len(self.values):
            raise ValueError(
                "timestamps and values must have matching lengths"
            )

    def __len__(self) -> int:
        return len(self.values)

    def value_at(self, index: int) -> float | None:
        return self.values[index]

    def latest(self) -> float | None:
        if not self.values:
            return None
        return self.values[-1]

    def previous(self) -> float | None:
        if len(self.values) < 2:
            return None
        return self.values[-2]

    def is_ready(self, index: int | None = None) -> bool:
        """Return whether the selected point contains a valid value."""

        if not self.values:
            return False

        selected = -1 if index is None else index
        value = self.values[selected]

        return (
            value is not None
            and not isnan(value)
        )


def aligned_series(
    timestamps: Sequence[datetime],
    values: Sequence[float],
    *,
    warmup: int = 0,
) -> TimeSeries:
    """Align calculated values to the original candle timeline."""

    if warmup < 0:
        raise ValueError("warmup cannot be negative")

    if len(values) + warmup != len(timestamps):
        raise ValueError(
            "values plus warmup must equal timestamp length"
        )

    return TimeSeries(
        timestamps=tuple(timestamps),
        values=(
            (None,) * warmup
            + tuple(float(value) for value in values)
        ),
    )
