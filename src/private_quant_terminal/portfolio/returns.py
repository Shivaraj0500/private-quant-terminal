from __future__ import annotations

from collections.abc import Sequence


def simple_returns(prices: Sequence[float]) -> tuple[float, ...]:
    """Calculate simple period-to-period returns from prices."""
    if len(prices) < 2:
        raise ValueError("at least two prices are required")

    if any(price <= 0 for price in prices):
        raise ValueError("prices must be greater than zero")

    return tuple(
        (current_price - previous_price) / previous_price
        for previous_price, current_price in zip(prices, prices[1:])
    )


def cumulative_return(returns: Sequence[float]) -> float:
    """Calculate the compounded cumulative return."""
    if len(returns) == 0:
        raise ValueError("at least one return is required")

    compounded = 1.0

    for period_return in returns:
        compounded *= 1.0 + period_return

    return compounded - 1.0


def average_return(returns: Sequence[float]) -> float:
    """Calculate the arithmetic average return."""
    if len(returns) == 0:
        raise ValueError("at least one return is required")

    return sum(returns) / len(returns)


def geometric_average_return(returns: Sequence[float]) -> float:
    """Calculate the geometric average return."""
    if len(returns) == 0:
        raise ValueError("at least one return is required")

    compounded = 1.0

    for period_return in returns:
        if period_return <= -1.0:
            raise ValueError("returns must be greater than -1")

        compounded *= 1.0 + period_return

    return compounded ** (1.0 / len(returns)) - 1.0