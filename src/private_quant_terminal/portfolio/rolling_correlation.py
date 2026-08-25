from __future__ import annotations

from math import sqrt
from typing import Sequence


def rolling_correlation(
    first_returns: Sequence[float],
    second_returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """
    Calculate Pearson correlation over rolling windows.

    Args:
        first_returns: First sequence of returns.
        second_returns: Second sequence of returns.
        window: Number of observations in each rolling window.

    Returns:
        A tuple containing one correlation value for each rolling window.

    Raises:
        ValueError: If the sequences have different lengths, the window is
            invalid, or a rolling window has zero variance.
    """
    if len(first_returns) != len(second_returns):
        raise ValueError(
            "first_returns and second_returns must have the same length"
        )

    if window <= 1:
        raise ValueError("window must be greater than 1")

    if window > len(first_returns):
        raise ValueError(
            "window cannot be greater than the number of returns"
        )

    correlations: list[float] = []

    for start in range(len(first_returns) - window + 1):
        first_window = first_returns[start : start + window]
        second_window = second_returns[start : start + window]

        first_mean = sum(first_window) / window
        second_mean = sum(second_window) / window

        covariance = sum(
            (first_value - first_mean) * (second_value - second_mean)
            for first_value, second_value in zip(
                first_window,
                second_window,
                strict=True,
            )
        )

        first_variance = sum(
            (value - first_mean) ** 2
            for value in first_window
        )

        second_variance = sum(
            (value - second_mean) ** 2
            for value in second_window
        )

        denominator = sqrt(first_variance * second_variance)

        if denominator == 0:
            raise ValueError(
                "correlation is undefined when a rolling window has zero variance"
            )

        correlations.append(covariance / denominator)

    return tuple(correlations)