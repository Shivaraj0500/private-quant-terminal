from private_quant_terminal.portfolio.closed_trade import ClosedTrade
from private_quant_terminal.portfolio.drawdown import (
    DrawdownCalculator,
    DrawdownMetrics,
)
from private_quant_terminal.portfolio.metrics import (
    PortfolioMetrics,
    calculate_metrics,
)
from private_quant_terminal.portfolio.performance import PerformanceSnapshot
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)
from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.portfolio.risk import PortfolioRisk
from private_quant_terminal.portfolio.risk_adjusted import (
    RiskAdjustedMetrics,
    calculate_risk_adjusted_metrics,
)
from private_quant_terminal.portfolio.risk_calculator import (
    PortfolioRiskCalculator,
)
from private_quant_terminal.portfolio.rolling_performance import (
    PortfolioRollingMetrics,
    calculate_rolling_metrics,
)
from private_quant_terminal.portfolio.snapshot import PortfolioSnapshot
from private_quant_terminal.portfolio.valuation import (
    PortfolioValuationService,
)


class PortfolioService:
    """Provide a unified interface for portfolio state and analytics."""

    def __init__(
        self,
        position_manager: PositionManager,
        valuation_service: PortfolioValuationService,
        risk_calculator: PortfolioRiskCalculator,
        performance_calculator: PortfolioPerformanceCalculator,
        drawdown_calculator: DrawdownCalculator,
    ) -> None:
        """Initialize the portfolio service."""
        self._position_manager = position_manager
        self._valuation_service = valuation_service
        self._risk_calculator = risk_calculator
        self._performance_calculator = performance_calculator
        self._drawdown_calculator = drawdown_calculator

    def positions(self) -> tuple[Position, ...]:
        """Return all currently open portfolio positions."""
        return self._position_manager.positions()

    def closed_trades(self) -> tuple[ClosedTrade, ...]:
        """Return all completed portfolio trades."""
        return self._position_manager.closed_trades()

    def snapshot(
        self,
        prices: dict[str, float],
    ) -> PortfolioSnapshot:
        """Return a portfolio snapshot using current market prices."""
        return self._valuation_service.snapshot(prices)

    def risk(
        self,
        prices: dict[str, float],
    ) -> PortfolioRisk:
        """Return portfolio risk metrics using current market prices."""
        return self._risk_calculator.calculate(
            positions=self._position_manager.positions(),
            prices=prices,
        )

    def performance(
        self,
        returns: tuple[float, ...],
    ) -> PortfolioMetrics:
        """Return summary performance metrics for a return series."""
        return calculate_metrics(returns)

    def risk_adjusted(
        self,
        returns: tuple[float, ...],
        *,
        risk_free_rate: float = 0.0,
        target_return: float = 0.0,
        max_drawdown: float = 0.0,
    ) -> RiskAdjustedMetrics:
        """Return risk-adjusted metrics for a portfolio return series."""
        return calculate_risk_adjusted_metrics(
            returns,
            risk_free_rate=risk_free_rate,
            target_return=target_return,
            max_drawdown=max_drawdown,
        )

    def rolling_performance(
        self,
        returns: tuple[float, ...],
        window: int,
    ) -> PortfolioRollingMetrics:
        """Return rolling analytics for a portfolio return series."""
        return calculate_rolling_metrics(
            returns=returns,
            window=window,
        )

    def trading_performance(self) -> PerformanceSnapshot:
        """Return trading performance calculated from closed trades."""
        return self._performance_calculator.calculate(
            closed_trades=self._position_manager.closed_trades(),
        )

    def drawdown(
        self,
        peak_value: float,
        current_value: float,
    ) -> DrawdownMetrics:
        """Return portfolio drawdown metrics."""
        return self._drawdown_calculator.calculate(
            peak_value=peak_value,
            current_value=current_value,
        )
