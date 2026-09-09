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
    ResearchExecutionEventType,
    ResearchExecutionResult,
)
from private_quant_terminal.research.risk_diagnostics import (
    ResearchRiskDiagnostics,
    ResearchRiskDiagnosticsCalculator,
)
from private_quant_terminal.research.risk_findings import (
    ResearchRiskFinding,
    ResearchRiskFindingsCalculator,
)
from private_quant_terminal.research.behavior_diagnostics import (
    ResearchBehaviorDiagnostics,
    ResearchBehaviorDiagnosticsCalculator,
)
from private_quant_terminal.research.behavior_findings import (
    ResearchBehaviorFinding,
    ResearchBehaviorFindingsCalculator,
)
from private_quant_terminal.research.trade_analytics import (
    ResearchTradeAnalytics,
    ResearchTradeAnalyticsCalculator,
)


@dataclass(frozen=True)
class ResearchEvidenceSummary:
    """Immutable summary of the evidence contained in a research result."""

    event_count: int
    completed_trade_count: int
    has_open_position: bool


@dataclass(frozen=True)
class ResearchPerformanceReport:
    """Immutable performance report for a research execution."""

    trading_performance: object
    returns: tuple[float, ...]
    max_drawdown: float
    max_drawdown_percent: float
    risk_adjusted: object
    evidence_summary: ResearchEvidenceSummary
    trade_analytics: ResearchTradeAnalytics
    behavior_diagnostics: ResearchBehaviorDiagnostics
    behavior_findings: tuple[ResearchBehaviorFinding, ...]
    risk_diagnostics: ResearchRiskDiagnostics
    risk_findings: tuple[ResearchRiskFinding, ...]


class ResearchPerformanceAnalyzer:
    """Calculate performance analytics from a research execution."""

    def analyze(
        self,
        execution: ResearchExecutionResult,
        simulation_steps=(),
    ) -> ResearchPerformanceReport:
        """Analyze the completed research execution."""

        trading_performance = PortfolioPerformanceCalculator().calculate(
            tuple(self._to_closed_trade(trade) for trade in execution.trades)
        )

        returns = self._calculate_returns(
            tuple(
                point.equity if hasattr(point, "equity") else float(point)
                for point in execution.equity_curve
            ),
        )

        max_drawdown, max_drawdown_percent = self._calculate_max_drawdown(
            tuple(
                point.equity if hasattr(point, "equity") else float(point)
                for point in execution.equity_curve
            ),
        )

        evidence_summary = ResearchEvidenceSummary(
            event_count=len(execution.events),
            completed_trade_count=len(execution.trades),
            has_open_position=(
                sum(
                    event.event_type is ResearchExecutionEventType.ENTRY
                    for event in execution.events
                )
                > sum(
                    event.event_type is ResearchExecutionEventType.EXIT
                    for event in execution.events
                )
            ),
        )

        risk_adjusted = calculate_risk_adjusted_metrics(
            returns,
            max_drawdown=max_drawdown,
        )

        trade_analytics = ResearchTradeAnalyticsCalculator().calculate(
            execution.trades,
        )
        behavior_diagnostics = ResearchBehaviorDiagnosticsCalculator().calculate(
            execution.trades,
        )
        behavior_findings = ResearchBehaviorFindingsCalculator().calculate(
            behavior_diagnostics,
        )
        risk_diagnostics = ResearchRiskDiagnosticsCalculator().calculate(
            tuple(simulation_steps),
        )
        risk_findings = ResearchRiskFindingsCalculator().calculate(
            risk_diagnostics,
        )

        return ResearchPerformanceReport(
            trading_performance=trading_performance,
            returns=returns,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            risk_adjusted=risk_adjusted,
            evidence_summary=evidence_summary,
            trade_analytics=trade_analytics,
            behavior_diagnostics=behavior_diagnostics,
            behavior_findings=behavior_findings,
            risk_diagnostics=risk_diagnostics,
            risk_findings=risk_findings,
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
