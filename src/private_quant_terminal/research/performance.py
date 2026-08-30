from dataclasses import dataclass

from private_quant_terminal.portfolio.drawdown import DrawdownCalculator
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)
from private_quant_terminal.portfolio.returns import simple_returns
from private_quant_terminal.portfolio.risk_adjusted import (
    calculate_risk_adjusted_metrics,
)
from private_quant_terminal.research.execution import (
    ResearchExecutionResult,
)


@dataclass(frozen=True)
class ResearchPerformanceReport:
    """Immutable performance report for a research execution."""

    trading_performance: object
    returns: tuple[float, ...]
    max_drawdown: float
    max_drawdown_percent: float
    risk_adjusted: object


class ResearchPerformanceAnalyzer:
    """Calculate performance analytics from a research execution."""

    def analyze(
        self,
        execution: ResearchExecutionResult,
    ) -> ResearchPerformanceReport:
        """Analyze the completed research execution."""

        trading_performance = (
            PortfolioPerformanceCalculator().calculate(
                tuple(
                    self._to_closed_trade(trade)
                    for trade in execution.trades
                )
            )
        )

        returns = self._calculate_returns(
            execution.equity_curve,
        )

        max_drawdown, max_drawdown_percent = (
            self._calculate_max_drawdown(
                execution.equity_curve,
            )
        )

        risk_adjusted = calculate_risk_adjusted_metrics(
            returns,
            max_drawdown=max_drawdown,
        )

        return ResearchPerformanceReport(
            trading_performance=trading_performance,
            returns=returns,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            risk_adjusted=risk_adjusted,
        )

    @staticmethod
    def _to_closed_trade(trade):
        from private_quant_terminal.portfolio.closed_trade import (
            ClosedTrade,
        )

        return ClosedTrade(
            symbol=trade.symbol,
            quantity=int(trade.quantity),
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            realized_pnl=trade.net_pnl,
        )

    @staticmethod
    def _calculate_returns(
        equity_curve: tuple[float, ...],
    ) -> tuple[float, ...]:
        if len(equity_curve) < 2:
            return ()

        return simple_returns(equity_curve)

    @staticmethod
    def _calculate_max_drawdown(
        equity_curve: tuple[float, ...],
    ) -> tuple[float, float]:
        if not equity_curve:
            return 0.0, 0.0

        peak = equity_curve[0]
        max_drawdown = 0.0
        max_drawdown_percent = 0.0

        calculator = DrawdownCalculator()

        for value in equity_curve:
            peak = max(peak, value)

            metrics = calculator.calculate(
                peak_value=peak,
                current_value=value,
            )

            if metrics.drawdown >= max_drawdown:
                max_drawdown = metrics.drawdown
                max_drawdown_percent = metrics.drawdown_percent

        return max_drawdown, max_drawdown_percent
