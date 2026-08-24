from __future__ import annotations

from collections.abc import Sequence
from math import sqrt


def rolling_cumulative_return(
    returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate compounded cumulative returns for each rolling window."""
    _validate_window(returns, window)

    return tuple(
        _cumulative_return(returns[index : index + window])
        for index in range(len(returns) - window + 1)
    )


def rolling_mean_return(
    returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate the arithmetic mean return for each rolling window."""
    _validate_window(returns, window)

    return tuple(
        sum(returns[index : index + window]) / window
        for index in range(len(returns) - window + 1)
    )


def rolling_return_volatility(
    returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """Calculate population standard deviation for each rolling window."""
    _validate_window(returns, window)

    return tuple(
        _population_standard_deviation(returns[index : index + window])
        for index in range(len(returns) - window + 1)
    )


def _cumulative_return(returns: Sequence[float]) -> float:
    cumulative = 1.0

    for value in returns:
        cumulative *= 1.0 + value

    return cumulative - 1.0


def _population_standard_deviation(
    values: Sequence[float],
) -> float:
    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    return sqrt(variance)


def _validate_window(
    values: Sequence[float],
    window: int,
) -> None:
    if window <= 0:
        raise ValueError("window must be greater than zero")

    if window > len(values):
        raise ValueError(
            "window cannot be greater than the number of values"
        )