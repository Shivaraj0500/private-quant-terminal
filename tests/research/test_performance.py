from datetime import UTC, datetime
from math import isclose

from private_quant_terminal.research import (
    ResearchExecutionResult,
    ResearchTrade,
)
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