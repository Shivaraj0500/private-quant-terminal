from __future__ import annotations

from collections.abc import Sequence
from math import sqrt


def rolling_sortino_ratio(
    returns: Sequence[float],
    window: int,
    target_return: float = 0.0,
) -> tuple[float, ...]:
    """
    Calculate the Sortino ratio over rolling return windows.

    The target return is treated as a per-period rate. Downside deviation
    is calculated using only returns below the target return.

    Raises:
        ValueError: If the window is invalid or downside deviation is zero.
    """
    if window <= 1:
        raise ValueError("window must be greater than 1")

    if window > len(returns):
        raise ValueError(
            "window cannot be greater than the number of returns"
        )

    ratios: list[float] = []

    for start in range(len(returns) - window + 1):
        return_window = returns[start : start + window]

        mean_return = sum(return_window) / window

        downside_variance = sum(
            min(value - target_return, 0.0) ** 2
            for value in return_window
        ) / window

        downside_deviation = sqrt(downside_variance)

        if downside_deviation == 0:
            raise ValueError(
                "Sortino ratio is undefined when downside deviation is zero"
            )

        ratios.append(
            (mean_return - target_return) / downside_deviation
        )

    return tuple(ratios)