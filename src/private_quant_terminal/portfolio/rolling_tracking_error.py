from __future__ import annotations

from math import sqrt
from typing import Sequence


def rolling_tracking_error(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """
    Calculate tracking error over rolling return windows.

    Tracking error is the population standard deviation of active returns,
    where active return equals portfolio return minus benchmark return.
    """
    if len(portfolio_returns) != len(benchmark_returns):
        raise ValueError(
            "portfolio_returns and benchmark_returns must have the same length"
        )

    if window <= 1:
        raise ValueError("window must be greater than 1")

    if window > len(portfolio_returns):
        raise ValueError(
            "window cannot be greater than the number of returns"
        )

    errors: list[float] = []

    for start in range(len(portfolio_returns) - window + 1):
        active_returns = tuple(
            portfolio_return - benchmark_return
            for portfolio_return, benchmark_return in zip(
                portfolio_returns[start : start + window],
                benchmark_returns[start : start + window],
                strict=True,
            )
        )

        mean_active_return = sum(active_returns) / window

        variance = sum(
            (value - mean_active_return) ** 2
            for value in active_returns
        ) / window

        errors.append(sqrt(variance))

    return tuple(errors)