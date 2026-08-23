from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class PortfolioMetrics:
    """Summary metrics calculated from portfolio returns."""

    total_return: float
    average_return: float
    best_return: float
    worst_return: float
    volatility: float


def calculate_metrics(
    returns: tuple[float, ...],
) -> PortfolioMetrics:
    """Calculate summary metrics for a portfolio return series."""

    if not returns:
        return PortfolioMetrics(
            total_return=0.0,
            average_return=0.0,
            best_return=0.0,
            worst_return=0.0,
            volatility=0.0,
        )

    total_return = sum(returns)
    average_return = total_return / len(returns)
    best_return = max(returns)
    worst_return = min(returns)

    variance = (
        sum(
            (value - average_return) ** 2
            for value in returns
        )
        / len(returns)
    )

    volatility = sqrt(variance)

    return PortfolioMetrics(
        total_return=total_return,
        average_return=average_return,
        best_return=best_return,
        worst_return=worst_return,
        volatility=volatility,
    )