from dataclasses import replace
from datetime import UTC, datetime, timedelta
from math import isclose

from private_quant_terminal.research import (
    ResearchExecutionResult,
    ResearchTrade,
)
from private_quant_terminal.research.execution import ResearchEquityPoint
from private_quant_terminal.research.performance import (
    ResearchPerformanceAnalyzer,
)


def make_result() -> ResearchExecutionResult:
    return ResearchExecutionResult(
        run_id="performance-test",
        events=(),
        trades=(
            ResearchTrade(
                symbol="RELIANCE",
                entry_time=datetime(2026, 1, 1, tzinfo=UTC),
                exit_time=datetime(2026, 1, 2, tzinfo=UTC),
                entry_price=100.0,
                exit_price=110.0,
                quantity=10.0,
                gross_pnl=100.0,
                transaction_cost=2.0,
                net_pnl=98.0,
            ),
            ResearchTrade(
                symbol="RELIANCE",
                entry_time=datetime(2026, 1, 3, tzinfo=UTC),
                exit_time=datetime(2026, 1, 4, tzinfo=UTC),
                entry_price=110.0,
                exit_price=105.0,
                quantity=10.0,
                gross_pnl=-50.0,
                transaction_cost=2.0,
                net_pnl=-52.0,
            ),
        ),
        equity_curve=(
            100000.0,
            101000.0,
            99000.0,
            102000.0,
            100000.0,
        ),
        final_equity=100046.0,
    )


def test_analyzer_returns_evidence_summary() -> None:
    result = ResearchPerformanceAnalyzer().analyze(make_result())

    assert result.evidence_summary.event_count == 0
    assert result.evidence_summary.completed_trade_count == 2
    assert result.evidence_summary.has_open_position is False


def test_analyzer_returns_trade_performance() -> None:
    result = ResearchPerformanceAnalyzer().analyze(make_result())

    assert result.trading_performance.realized_pnl == 46.0
    assert result.trading_performance.winning_trades == 1
    assert result.trading_performance.losing_trades == 1
    assert result.trading_performance.win_rate == 50.0

    assert result.trade_analytics.total_trades == 2
    assert result.trade_analytics.average_trade == 23.0
    assert result.trade_analytics.best_trade == 98.0
    assert result.trade_analytics.worst_trade == -52.0
    assert result.trade_analytics.shortest_holding_time == timedelta(days=1)
    assert result.trade_analytics.longest_holding_time == timedelta(days=1)
    assert result.trade_analytics.average_holding_time == timedelta(days=1)
    assert result.trade_analytics.max_consecutive_wins == 1
    assert result.trade_analytics.max_consecutive_losses == 1


def test_analyzer_calculates_equity_returns() -> None:
    result = ResearchPerformanceAnalyzer().analyze(make_result())

    assert result.returns == (
        0.01,
        -2000 / 101000,
        3000 / 99000,
        -2000 / 102000,
    )


def test_analyzer_calculates_drawdown() -> None:
    result = ResearchPerformanceAnalyzer().analyze(make_result())

    assert result.max_drawdown == 2000.0
    assert isclose(
        result.max_drawdown_percent,
        2000 / 102000 * 100,
        rel_tol=1e-9,
    )


def test_analyzer_is_deterministic() -> None:
    execution = make_result()

    analyzer = ResearchPerformanceAnalyzer()

    assert analyzer.analyze(execution) == analyzer.analyze(execution)


def test_empty_equity_curve_is_supported() -> None:
    execution = ResearchExecutionResult(
        run_id="empty",
        events=(),
        trades=(),
        equity_curve=(),
        final_equity=100000.0,
    )

    result = ResearchPerformanceAnalyzer().analyze(execution)

    assert result.returns == ()
    assert result.max_drawdown == 0.0
    assert result.max_drawdown_percent == 0.0

def test_performance_period_calculates_cagr():
    from datetime import datetime, timezone

    result = make_result()
    result = replace(
        result,
        equity_curve=(
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                equity=100_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
                equity=110_000,
            ),
        ),
    )

    report = ResearchPerformanceAnalyzer().analyze(result)

    assert report.performance_period.start_timestamp == datetime(
        2024, 1, 1, tzinfo=timezone.utc
    )
    assert report.performance_period.end_timestamp == datetime(
        2025, 1, 1, tzinfo=timezone.utc
    )
    assert report.performance_period.cagr is not None
    assert 0.099 < report.performance_period.cagr < 0.101


def test_performance_period_detects_drawdown_recovery():
    from datetime import datetime, timezone

    result = make_result()
    result = replace(
        result,
        equity_curve=(
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                equity=100_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                equity=90_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 3, tzinfo=timezone.utc),
                equity=95_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 4, tzinfo=timezone.utc),
                equity=100_000,
            ),
        ),
    )

    report = ResearchPerformanceAnalyzer().analyze(result)

    assert report.performance_period.drawdown_recovered is True
    assert report.performance_period.recovery_timestamp == datetime(
        2024, 1, 4, tzinfo=timezone.utc
    )
    assert report.performance_period.recovery_duration is not None
    assert report.performance_period.recovery_duration.total_seconds() == 2 * 24 * 60 * 60


def test_performance_period_marks_unrecovered_drawdown():
    from datetime import datetime, timezone

    result = make_result()
    result = replace(
        result,
        equity_curve=(
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                equity=100_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                equity=90_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 3, tzinfo=timezone.utc),
                equity=95_000,
            ),
        ),
    )

    report = ResearchPerformanceAnalyzer().analyze(result)

    assert report.performance_period.drawdown_recovered is False
    assert report.performance_period.recovery_timestamp is None
    assert report.performance_period.recovery_duration is None


def test_performance_period_zero_drawdown_is_recovered():
    from datetime import datetime, timezone

    result = make_result()
    result = replace(
        result,
        equity_curve=(
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                equity=100_000,
            ),
            ResearchEquityPoint(
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                equity=101_000,
            ),
        ),
    )

    report = ResearchPerformanceAnalyzer().analyze(result)

    assert report.performance_period.drawdown_recovered is True
    assert report.performance_period.recovery_duration.total_seconds() == 0
    assert report.performance_period.recovery_timestamp == datetime(
        2024, 1, 1, tzinfo=timezone.utc
    )
