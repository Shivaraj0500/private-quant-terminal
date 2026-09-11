from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import pairwise

from private_quant_terminal.data.economics import (
    HistoricalInstrumentEconomicsProvider,
)
from private_quant_terminal.portfolio.drawdown import DrawdownCalculator
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)
from private_quant_terminal.portfolio.returns import simple_returns
from private_quant_terminal.portfolio.risk_adjusted import (
    calculate_risk_adjusted_metrics,
)
from private_quant_terminal.research.behavior_diagnostics import (
    ResearchBehaviorDiagnostics,
    ResearchBehaviorDiagnosticsCalculator,
)
from private_quant_terminal.research.behavior_findings import (
    ResearchBehaviorFinding,
    ResearchBehaviorFindingsCalculator,
)
from private_quant_terminal.research.execution import (
    ResearchExecutionEventType,
    ResearchExecutionResult,
)
from private_quant_terminal.research.option_diagnostics import (
    ResearchOptionDiagnostics,
    ResearchOptionDiagnosticsCalculator,
)
from private_quant_terminal.research.risk_diagnostics import (
    ResearchRiskDiagnostics,
    ResearchRiskDiagnosticsCalculator,
)
from private_quant_terminal.research.risk_findings import (
    ResearchRiskFinding,
    ResearchRiskFindingsCalculator,
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
class ResearchPerformancePeriod:
    """Immutable time-based performance and recovery evidence."""

    start_timestamp: datetime | None
    end_timestamp: datetime | None
    duration: timedelta | None
    cagr: float | None
    recovery_duration: timedelta | None
    recovery_timestamp: datetime | None
    drawdown_recovered: bool


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
    option_diagnostics: ResearchOptionDiagnostics
    performance_period: ResearchPerformancePeriod


class ResearchPerformanceAnalyzer:
    """Calculate performance analytics from a research execution."""

    def analyze(
        self,
        execution: ResearchExecutionResult,
        simulation_steps=(),
        option_fills=(),
        economics_provider: HistoricalInstrumentEconomicsProvider | None = None,
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
        risk_diagnostics = ResearchRiskDiagnosticsCalculator(
            economics_provider=economics_provider,
        ).calculate(
            tuple(simulation_steps),
        )
        risk_findings = ResearchRiskFindingsCalculator().calculate(
            risk_diagnostics,
        )
        option_diagnostics = ResearchOptionDiagnosticsCalculator().calculate(
            tuple(option_fills),
        )

        performance_period = self._calculate_performance_period(
            execution.equity_curve,
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
            option_diagnostics=option_diagnostics,
            performance_period=performance_period,
        )

    @staticmethod
    def _calculate_performance_period(equity_curve):
        if not equity_curve:
            return ResearchPerformancePeriod(
                start_timestamp=None,
                end_timestamp=None,
                duration=None,
                cagr=None,
                recovery_duration=None,
                recovery_timestamp=None,
                drawdown_recovered=False,
            )

        if not all(hasattr(point, "timestamp") for point in equity_curve):
            return ResearchPerformancePeriod(
                start_timestamp=None,
                end_timestamp=None,
                duration=None,
                cagr=None,
                recovery_duration=None,
                recovery_timestamp=None,
                drawdown_recovered=False,
            )

        points = tuple(equity_curve)

        for point in points:
            if point.timestamp.tzinfo is None:
                raise ValueError("Research equity timestamps must be timezone-aware.")

        for previous, current in pairwise(points):
            if current.timestamp <= previous.timestamp:
                raise ValueError("Research equity timestamps must be strictly increasing.")

        start = points[0]
        end = points[-1]
        duration = end.timestamp - start.timestamp

        cagr = None
        if start.equity > 0 and end.equity > 0 and duration.total_seconds() > 0:
            years = duration.total_seconds() / (365.25 * 24 * 60 * 60)
            exponent = 1 / years
            if abs(exponent) <= 300:
                cagr = (end.equity / start.equity) ** exponent - 1

        peak_equity = start.equity
        peak_timestamp = start.timestamp
        maximum_drawdown = 0.0
        maximum_drawdown_peak_timestamp = None
        maximum_drawdown_trough_timestamp = None

        for point in points[1:]:
            if point.equity > peak_equity:
                peak_equity = point.equity
                peak_timestamp = point.timestamp
                continue

            drawdown = peak_equity - point.equity

            if drawdown > maximum_drawdown:
                maximum_drawdown = drawdown
                maximum_drawdown_peak_timestamp = peak_timestamp
                maximum_drawdown_trough_timestamp = point.timestamp

        if maximum_drawdown == 0.0:
            return ResearchPerformancePeriod(
                start_timestamp=start.timestamp,
                end_timestamp=end.timestamp,
                duration=duration,
                cagr=cagr,
                recovery_duration=timedelta(0),
                recovery_timestamp=start.timestamp,
                drawdown_recovered=True,
            )

        recovery_timestamp = None

        for point in points:
            if (
                maximum_drawdown_peak_timestamp is not None
                and maximum_drawdown_trough_timestamp is not None
                and point.timestamp > maximum_drawdown_trough_timestamp
                and point.timestamp > maximum_drawdown_peak_timestamp
                and point.equity
                >= (
                    next(
                        peak.equity
                        for peak in points
                        if peak.timestamp == maximum_drawdown_peak_timestamp
                    )
                )
            ):
                recovery_timestamp = point.timestamp
                break

        recovery_duration = None
        if recovery_timestamp is not None and maximum_drawdown_trough_timestamp is not None:
            recovery_duration = recovery_timestamp - maximum_drawdown_trough_timestamp

        return ResearchPerformancePeriod(
            start_timestamp=start.timestamp,
            end_timestamp=end.timestamp,
            duration=duration,
            cagr=cagr,
            recovery_duration=recovery_duration,
            recovery_timestamp=recovery_timestamp,
            drawdown_recovered=recovery_timestamp is not None,
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
