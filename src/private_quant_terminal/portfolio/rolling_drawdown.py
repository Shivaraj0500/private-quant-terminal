from __future__ import annotations


def rolling_drawdown(
    values: tuple[float, ...],
    window: int,
) -> tuple[float, ...]:
    """Calculate the drawdown at each rolling window endpoint."""
    _validate_window(values, window)

    return tuple(
        _drawdown(values[index : index + window])
        for index in range(len(values) - window + 1)
    )


def rolling_max_drawdown(
    values: tuple[float, ...],
    window: int,
) -> tuple[float, ...]:
    """Calculate the maximum drawdown within each rolling window."""
    _validate_window(values, window)

    return tuple(
        _max_drawdown(values[index : index + window])
        for index in range(len(values) - window + 1)
    )


def _drawdown(values: tuple[float, ...]) -> float:
    peak = values[0]
    current_value = values[-1]

    for value in values:
        peak = max(peak, value)

    return (current_value - peak) / peak


def _max_drawdown(values: tuple[float, ...]) -> float:
    peak = values[0]
    max_drawdown = 0.0

    for value in values:
        peak = max(peak, value)
        drawdown = (value - peak) / peak
        max_drawdown = min(max_drawdown, drawdown)

    return max_drawdown


def _validate_window(
    values: tuple[float, ...],
    window: int,
) -> None:
    if not values:
        raise ValueError("values must not be empty")

    if window <= 0:
        raise ValueError("window must be greater than zero")

    if window > len(values):
        raise ValueError("window must not exceed the number of values")

    if any(value <= 0 for value in values):
        raise ValueError("values must be greater than zero")