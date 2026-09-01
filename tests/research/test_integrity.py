from datetime import UTC, datetime, timedelta

from private_quant_terminal.research import (
    ResearchEquityPoint,
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchExecutionResult,
    ResearchExecutor,
    ResearchIntegrityAnalyzer,
    ResearchIntegritySeverity,
    ResearchIntegrityStatus,
    ResearchTrade,
)
from tests.research.test_executor import make_candle, make_request


def make_trade(
    *,
    gross_pnl: float = 100.0,
    transaction_cost: float = 2.0,
    net_pnl: float = 98.0,
) -> ResearchTrade:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return ResearchTrade(
        symbol="RELIANCE",
        entry_time=start,
        exit_time=start + timedelta(minutes=5),
        entry_price=100.0,
        exit_price=110.0,
        quantity=10.0,
        gross_pnl=gross_pnl,
        transaction_cost=transaction_cost,
        net_pnl=net_pnl,
    )


def make_valid_result() -> ResearchExecutionResult:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return ResearchExecutionResult(
        run_id="integrity-test",
        events=(
            ResearchExecutionEvent(
                timestamp=start,
                event_type=ResearchExecutionEventType.ENTRY,
                symbol="RELIANCE",
                price=100.0,
                quantity=10.0,
            ),
            ResearchExecutionEvent(
                timestamp=start + timedelta(minutes=5),
                event_type=ResearchExecutionEventType.EXIT,
                symbol="RELIANCE",
                price=110.0,
                quantity=10.0,
            ),
        ),
        trades=(make_trade(),),
        equity_curve=(
            ResearchEquityPoint(
                timestamp=start,
                equity=100000.0,
            ),
            ResearchEquityPoint(
                timestamp=start + timedelta(minutes=5),
                equity=100098.0,
            ),
        ),
        final_equity=100098.0,
    )


def test_valid_execution_passes_integrity() -> None:
    report = ResearchIntegrityAnalyzer().analyze(make_valid_result())

    assert report.status is ResearchIntegrityStatus.PASS
    assert report.passed
    assert report.failures == 0
    assert report.warnings == 0
    assert report.findings[0].severity is ResearchIntegritySeverity.PASS


def test_gross_pnl_mismatch_fails() -> None:
    execution = make_valid_result()
    corrupted_trade = make_trade(gross_pnl=101.0)

    execution = ResearchExecutionResult(
        run_id=execution.run_id,
        events=execution.events,
        trades=(corrupted_trade,),
        equity_curve=execution.equity_curve,
        final_equity=execution.final_equity,
    )

    report = ResearchIntegrityAnalyzer().analyze(execution)

    assert report.status is ResearchIntegrityStatus.FAIL
    assert any(
        finding.code == "GROSS_PNL_MISMATCH"
        for finding in report.findings
    )


def test_net_pnl_mismatch_fails() -> None:
    execution = make_valid_result()
    corrupted_trade = make_trade(net_pnl=97.0)

    execution = ResearchExecutionResult(
        run_id=execution.run_id,
        events=execution.events,
        trades=(corrupted_trade,),
        equity_curve=execution.equity_curve,
        final_equity=execution.final_equity,
    )

    report = ResearchIntegrityAnalyzer().analyze(execution)

    assert report.status is ResearchIntegrityStatus.FAIL
    assert any(
        finding.code == "NET_PNL_MISMATCH"
        for finding in report.findings
    )


def test_invalid_quantity_fails() -> None:
    execution = make_valid_result()
    corrupted_trade = ResearchTrade(
        symbol="RELIANCE",
        entry_time=make_trade().entry_time,
        exit_time=make_trade().exit_time,
        entry_price=100.0,
        exit_price=110.0,
        quantity=0.0,
        gross_pnl=0.0,
        transaction_cost=0.0,
        net_pnl=0.0,
    )

    execution = ResearchExecutionResult(
        run_id=execution.run_id,
        events=execution.events,
        trades=(corrupted_trade,),
        equity_curve=execution.equity_curve,
        final_equity=execution.final_equity,
    )

    report = ResearchIntegrityAnalyzer().analyze(execution)

    assert report.status is ResearchIntegrityStatus.FAIL
    assert any(
        finding.code == "INVALID_TRADE_QUANTITY"
        for finding in report.findings
    )


def test_non_chronological_events_fail() -> None:
    execution = make_valid_result()

    events = (
        execution.events[1],
        execution.events[0],
    )

    corrupted = ResearchExecutionResult(
        run_id=execution.run_id,
        events=events,
        trades=execution.trades,
        equity_curve=execution.equity_curve,
        final_equity=execution.final_equity,
    )

    report = ResearchIntegrityAnalyzer().analyze(corrupted)

    assert report.status is ResearchIntegrityStatus.FAIL
    assert any(
        finding.code == "EVENTS_NOT_CHRONOLOGICAL"
        for finding in report.findings
    )


def test_final_equity_mismatch_fails() -> None:
    execution = make_valid_result()

    corrupted = ResearchExecutionResult(
        run_id=execution.run_id,
        events=execution.events,
        trades=execution.trades,
        equity_curve=execution.equity_curve,
        final_equity=100099.0,
    )

    report = ResearchIntegrityAnalyzer().analyze(corrupted)

    assert report.status is ResearchIntegrityStatus.FAIL
    assert any(
        finding.code == "FINAL_EQUITY_MISMATCH"
        for finding in report.findings
    )


def test_empty_equity_curve_warns() -> None:
    execution = make_valid_result()

    result = ResearchExecutionResult(
        run_id=execution.run_id,
        events=execution.events,
        trades=execution.trades,
        equity_curve=(),
        final_equity=execution.final_equity,
    )

    report = ResearchIntegrityAnalyzer().analyze(result)

    assert report.status is ResearchIntegrityStatus.WARN
    assert report.warnings == 1
    assert report.failures == 0


def test_open_position_warns() -> None:
    execution = make_valid_result()

    result = ResearchExecutionResult(
        run_id=execution.run_id,
        events=(execution.events[0],),
        trades=(),
        equity_curve=execution.equity_curve[:1],
        final_equity=100000.0,
    )

    report = ResearchIntegrityAnalyzer().analyze(result)

    assert report.status is ResearchIntegrityStatus.WARN
    assert any(
        finding.code == "OPEN_POSITION"
        for finding in report.findings
    )


def test_analyzer_is_deterministic() -> None:
    execution = make_valid_result()
    analyzer = ResearchIntegrityAnalyzer()

    assert analyzer.analyze(execution) == analyzer.analyze(execution)
def test_real_executor_result_passes_integrity() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    request = make_request(
        (
            make_candle(start, 101.0),
            make_candle(start + timedelta(minutes=5), 94.0),
        )
    )

    execution = ResearchExecutor(initial_equity=100000.0).execute(request)

    report = ResearchIntegrityAnalyzer().analyze(execution)

    assert report.status is ResearchIntegrityStatus.PASS
    assert report.passed
    assert report.failures == 0