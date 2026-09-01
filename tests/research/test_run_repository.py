from datetime import UTC, datetime

import pytest

from private_quant_terminal.persistence import Database
from private_quant_terminal.research import (
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchExecutionResult,
    ResearchIntegrityFinding,
    ResearchIntegrityReport,
    ResearchIntegritySeverity,
    ResearchIntegrityStatus,
    ResearchParameters,
    ResearchRun,
    ResearchRunRepository,
    ResearchRunStatus,
    ResearchTrade,
    canonical_parameters_json,
    parameters_hash,
)


def make_run(run_id: str = "run-1") -> ResearchRun:
    parameters = ResearchParameters(
        values={
            "lookback": 20,
            "risk": 0.02,
        }
    )

    return ResearchRun(
        run_id=run_id,
        strategy_id="strategy-1",
        strategy_version=1,
        strategy_hash="a" * 64,
        dataset_hash="b" * 64,
        symbol="RELIANCE",
        timeframe="1h",
        start_time=datetime(2026, 1, 1, tzinfo=UTC),
        end_time=datetime(2026, 1, 2, tzinfo=UTC),
        parameters_json=canonical_parameters_json(parameters),
        parameters_hash=parameters_hash(parameters),
        status=ResearchRunStatus.CREATED,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_save_result_persists_and_restores_integrity(
    tmp_path,
) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()
    repository.save(run)

    execution = ResearchExecutionResult(
        run_id=run.run_id,
        events=(
            ResearchExecutionEvent(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                event_type=ResearchExecutionEventType.ENTRY,
                symbol="RELIANCE",
                price=100.0,
                quantity=1.0,
            ),
            ResearchExecutionEvent(
                timestamp=datetime(2026, 1, 2, tzinfo=UTC),
                event_type=ResearchExecutionEventType.EXIT,
                symbol="RELIANCE",
                price=110.0,
                quantity=1.0,
            ),
        ),
        trades=(
            ResearchTrade(
                symbol="RELIANCE",
                entry_time=datetime(2026, 1, 1, tzinfo=UTC),
                exit_time=datetime(2026, 1, 2, tzinfo=UTC),
                entry_price=100.0,
                exit_price=110.0,
                quantity=1.0,
                gross_pnl=10.0,
                transaction_cost=1.0,
                net_pnl=9.0,
            ),
        ),
        equity_curve=(),
        final_equity=100009.0,
    )

    integrity = ResearchIntegrityReport(
        status=ResearchIntegrityStatus.PASS,
        findings=(
            ResearchIntegrityFinding(
                severity=ResearchIntegritySeverity.PASS,
                code="INTEGRITY_OK",
                message="Research execution passed integrity checks.",
            ),
        ),
    )

    performance = {
        "realized_pnl": 9.0,
        "unrealized_pnl": 0.0,
        "total_pnl": 9.0,
        "winning_trades": 1,
        "losing_trades": 0,
        "win_rate": 1.0,
        "average_win": 9.0,
        "average_loss": 0.0,
        "profit_factor": 0.0,
        "returns": [0.00009],
        "max_drawdown": 0.0,
        "max_drawdown_percent": 0.0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "downside_deviation": 0.0,
        "calmar_ratio": 0.0,
    }

    repository.save_result(
        execution,
        performance,
        integrity,
    )

    restored_execution, restored_integrity, restored_performance = (
        repository.get_result(run.run_id)
    )

    assert restored_execution == execution
    assert restored_integrity == integrity
    assert restored_performance == performance


def test_save_and_get_round_trip(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()

    repository.save(run)

    assert repository.get(run.run_id) == run


def test_save_same_run_is_idempotent(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()

    repository.save(run)
    repository.save(run)

    assert repository.get(run.run_id) == run


def test_save_rejects_same_run_with_different_identity(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    first = make_run()

    second = ResearchRun(
        run_id=first.run_id,
        strategy_id=first.strategy_id,
        strategy_version=first.strategy_version,
        strategy_hash=first.strategy_hash,
        dataset_hash="c" * 64,
        symbol=first.symbol,
        timeframe=first.timeframe,
        start_time=first.start_time,
        end_time=first.end_time,
        parameters_json=first.parameters_json,
        parameters_hash=first.parameters_hash,
        status=first.status,
        created_at=first.created_at,
    )

    repository.save(first)

    with pytest.raises(
        ValueError,
        match="Research run identity is immutable",
    ):
        repository.save(second)


def test_unknown_run_raises(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    with pytest.raises(
        KeyError,
        match="Unknown research run",
    ):
        repository.get("missing")


def test_update_status_transitions_created_to_running(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()
    repository.save(run)

    repository.update_status(
        run.run_id,
        ResearchRunStatus.RUNNING,
    )

    assert repository.get(run.run_id).status is ResearchRunStatus.RUNNING


def test_update_status_transitions_running_to_completed(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()
    repository.save(run)
    repository.update_status(
        run.run_id,
        ResearchRunStatus.RUNNING,
    )

    repository.update_status(
        run.run_id,
        ResearchRunStatus.COMPLETED,
    )

    assert repository.get(run.run_id).status is ResearchRunStatus.COMPLETED


def test_update_status_transitions_running_to_failed(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()
    repository.save(run)
    repository.update_status(
        run.run_id,
        ResearchRunStatus.RUNNING,
    )

    repository.update_status(
        run.run_id,
        ResearchRunStatus.FAILED,
    )

    assert repository.get(run.run_id).status is ResearchRunStatus.FAILED


def test_update_status_rejects_invalid_transition(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    run = make_run()
    repository.save(run)

    with pytest.raises(
        ValueError,
        match="Invalid research run status transition",
    ):
        repository.update_status(
            run.run_id,
            ResearchRunStatus.COMPLETED,
        )


def test_update_status_rejects_unknown_run(tmp_path) -> None:
    repository = ResearchRunRepository(
        Database(tmp_path / "research.db")
    )

    with pytest.raises(
        KeyError,
        match="Unknown research run",
    ):
        repository.update_status(
            "missing",
            ResearchRunStatus.RUNNING,
        )
