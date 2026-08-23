from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class RiskAdjustedMetrics:
    """Risk-adjusted metrics calculated from portfolio returns."""

    sharpe_ratio: float
    sortino_ratio: float
    downside_deviation: float
    calmar_ratio: float


def calculate_risk_adjusted_metrics(
    returns: tuple[float, ...],
    *,
    risk_free_rate: float = 0.0,
    target_return: float = 0.0,
    max_drawdown: float = 0.0,
) -> RiskAdjustedMetrics:
    """Calculate risk-adjusted metrics for a portfolio return series."""

    if not returns:
        return RiskAdjustedMetrics(
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            downside_deviation=0.0,
            calmar_ratio=0.0,
        )

    average_return = sum(returns) / len(returns)

    excess_returns = tuple(
        value - risk_free_rate
        for value in returns
    )

    average_excess_return = (
        sum(excess_returns) / len(excess_returns)
    )

    variance = (
        sum(
            (value - average_excess_return) ** 2
            for value in excess_returns
        )
        / len(excess_returns)
    )

    volatility = sqrt(variance)

    sharpe_ratio = (
        average_excess_return / volatility
        if volatility != 0.0
        else 0.0
    )

    downside_returns = tuple(
        min(value - target_return, 0.0)
        for value in returns
    )

    downside_deviation = sqrt(
        sum(
            value**2
            for value in downside_returns
        )
        / len(downside_returns)
    )

    average_target_excess_return = (
        average_return - target_return
    )

    sortino_ratio = (
        average_target_excess_return / downside_deviation
        if downside_deviation != 0.0
        else 0.0
    )

    total_return = sum(returns)

    calmar_ratio = (
        total_return / abs(max_drawdown)
        if max_drawdown != 0.0
        else 0.0
    )

    return RiskAdjustedMetrics(
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        downside_deviation=downside_deviation,
        calmar_ratio=calmar_ratio,
    )