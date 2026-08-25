from __future__ import annotations

from math import isclose, sqrt
from typing import Sequence


def rolling_information_ratio(
    portfolio_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int,
) -> tuple[float, ...]:
    """
    Calculate the Information Ratio over rolling return windows.

    Information Ratio = mean active return / tracking error.

    Active return equals portfolio return minus benchmark return.
    Tracking error is calculated as the sample standard deviation of
    active returns.
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

    ratios: list[float] = []

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
        ) / (window - 1)

        tracking_error = sqrt(variance)

        if isclose(tracking_error, 0.0, abs_tol=1e-12):
            raise ValueError(
                "Information ratio is undefined when tracking error is zero"
            )

        ratios.append(mean_active_return / tracking_error)

    return tuple(ratios)