from dataclasses import dataclass

from private_quant_terminal.portfolio.performance import PerformanceSnapshot
from private_quant_terminal.portfolio.risk import PortfolioRisk
from private_quant_terminal.portfolio.snapshot import PortfolioSnapshot


@dataclass(frozen=True)
class PortfolioSummary:
    """Aggregate summary of current portfolio analytics."""

    snapshot: PortfolioSnapshot
    risk: PortfolioRisk
    closed_trade_count: int
    trading_performance: PerformanceSnapshot


def calculate_portfolio_summary(
    *,
    snapshot: PortfolioSnapshot,
    risk: PortfolioRisk,
    closed_trade_count: int,
    trading_performance: PerformanceSnapshot,
) -> PortfolioSummary:
    """Calculate an aggregate portfolio summary."""

    return PortfolioSummary(
        snapshot=snapshot,
        risk=risk,
        closed_trade_count=closed_trade_count,
        trading_performance=trading_performance,
    )
