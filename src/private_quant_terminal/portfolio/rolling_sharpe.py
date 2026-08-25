from __future__ import annotations

from math import sqrt
from typing import Sequence


def rolling_sharpe_ratio(
    returns: Sequence[float],
    window: int,
    risk_free_rate: float = 0.0,
) -> tuple[float, ...]:
    """
    Calculate the Sharpe ratio over rolling return windows.

    The risk-free rate is treated as a per-period rate.
    Volatility uses the population standard deviation.
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
        excess_returns = tuple(
            value - risk_free_rate
            for value in return_window
        )

        mean_excess_return = sum(excess_returns) / window

        variance = sum(
            (value - mean_excess_return) ** 2
            for value in excess_returns
        ) / window

        volatility = sqrt(variance)

        if volatility == 0:
            raise ValueError(
                "Sharpe ratio is undefined when volatility is zero"
            )

        ratios.append(mean_excess_return / volatility)

    return tuple(ratios)