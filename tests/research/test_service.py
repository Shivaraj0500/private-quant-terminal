from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.data.identity import (
    DatasetIdentity,
    candle_dataset_hash,
)
from private_quant_terminal.models import Candle
from private_quant_terminal.persistence import Database
from private_quant_terminal.research import (
    ResearchAnalysisResult,
    ResearchIntegrityFinding,
    ResearchIntegrityReport,
    ResearchIntegritySeverity,
    ResearchIntegrityStatus,
    ResearchParameters,
    ResearchRunService,
    ResearchRunStatus,
)
from private_quant_terminal.research.repository import ResearchRunRepository
from private_quant_terminal.strategy import (
    ConditionOperator,
    ExecutionAssumptions,
    OrderType,
    PositionSizing,
    PositionSizingMethod,
    StopLoss,
    StopLossType,
    StrategyCondition,
    StrategyDefinition,
    StrategyStatus,
    StrategyTimeframe,
    StrategyVersion,
    TakeProfit,
    TakeProfitType,
)


def make_strategy_version() -> StrategyVersion:
    strategy = StrategyDefinition(
        strategy_id="service-test",
        name="Service Test",
        description="Research service orchestration test.",
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        entry_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.GREATER_THAN,
                value=100.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="close",
                operator=ConditionOperator.LESS_THAN,
                value=95.0,
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.FIXED_QUANTITY,
            value=1.0,
        ),
        stop_loss=StopLoss(type=StopLossType.NONE),
        take_profit=TakeProfit(type=TakeProfitType.NONE),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
        ),
        status=StrategyStatus.VALIDATED,
    )

    return StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def make_candles() -> tuple[Candle, ...]:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    return (
        Candle(
            timestamp=start,
            open=101.0,
            high=102.0,
            low=100.0,
            close=101.0,
            volume=1000.0,
        ),
        Candle(
            timestamp=start + timedelta(minutes=5),
            open=94.0,
            high=95.0,
            low=93.0,
            close=94.0,
            volume=1000.0,
        ),
    )


def make_dataset(candles: tuple[Candle, ...]) -> DatasetIdentity:
    return DatasetIdentity(
        dataset_hash=candle_dataset_hash(list(candles)),
        symbol="RELIANCE",
        timeframe="5m",
        candle_count=len(candles),
        start_time=candles[0].timestamp,
        end_time=candles[-1].timestamp,
    )


def make_service(tmp_path) -> ResearchRunService:
    return ResearchRunService(
        repository=ResearchRunRepository(
            Database(tmp_path / "research.db")
        )
    )


def make_run(
    service: ResearchRunService,
    strategy_version: StrategyVersion,
    candles: tuple[Candle, ...],
):
    return service.create_run(
        strategy_version=strategy_version,
        dataset=make_dataset(candles),
        parameters=ResearchParameters(values={}),
        run_id="service-run",
    ).run


def test_execute_run_returns_complete_analysis_result(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)

    run = make_run(service, strategy_version, candles)

    result = service.execute_run(
        run=run,
        strategy_version=strategy_version,
        candles=candles,
        initial_equity=100000.0,
    )

    assert isinstance(result, ResearchAnalysisResult)
    assert result.run.run_id == run.run_id
    assert result.run.status is ResearchRunStatus.COMPLETED
    assert result.execution.run_id == run.run_id
    assert len(result.execution.trades) == 1
    assert result.performance.trading_performance.realized_pnl == -7.0


def test_execute_run_rejects_strategy_identity_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    mismatched = StrategyVersion(
        strategy_id="different-strategy",
        version=strategy_version.version,
        specification=strategy_version.specification,
        created_at=strategy_version.created_at,
    )

    with pytest.raises(
        ValueError,
        match="strategy identity does not match research run",
    ):
        service.execute_run(
            run=run,
            strategy_version=mismatched,
            candles=candles,
            initial_equity=100000.0,
        )


def test_execute_run_rejects_strategy_version_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    mismatched = StrategyVersion(
        strategy_id=strategy_version.strategy_id,
        version=2,
        specification=strategy_version.specification,
        created_at=strategy_version.created_at,
    )

    with pytest.raises(
        ValueError,
        match="strategy version does not match research run",
    ):
        service.execute_run(
            run=run,
            strategy_version=mismatched,
            candles=candles,
            initial_equity=100000.0,
        )


def test_execute_run_rejects_strategy_hash_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    altered_strategy = StrategyDefinition(
        strategy_id=strategy_version.specification.strategy_id,
        name="Altered Strategy",
        description=strategy_version.specification.description,
        instruments=strategy_version.specification.instruments,
        timeframe=strategy_version.specification.timeframe,
        entry_conditions=strategy_version.specification.entry_conditions,
        exit_conditions=strategy_version.specification.exit_conditions,
        position_sizing=strategy_version.specification.position_sizing,
        stop_loss=strategy_version.specification.stop_loss,
        take_profit=strategy_version.specification.take_profit,
        execution=strategy_version.specification.execution,
        status=strategy_version.specification.status,
    )

    altered_version = StrategyVersion(
        strategy_id=strategy_version.strategy_id,
        version=strategy_version.version,
        specification=altered_strategy,
        created_at=strategy_version.created_at,
    )

    with pytest.raises(
        ValueError,
        match="strategy hash does not match research run",
    ):
        service.execute_run(
            run=run,
            strategy_version=altered_version,
            candles=candles,
            initial_equity=100000.0,
        )


def test_execute_run_rejects_dataset_hash_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    different_candles = (
        candles[0],
        Candle(
            timestamp=candles[1].timestamp,
            open=96.0,
            high=97.0,
            low=95.0,
            close=96.0,
            volume=1000.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="dataset hash does not match research run",
    ):
        service.execute_run(
            run=run,
            strategy_version=strategy_version,
            candles=different_candles,
            initial_equity=100000.0,
        )


def test_execute_run_rejects_empty_candles(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    with pytest.raises(
        ValueError,
        match="research execution requires at least one candle",
    ):
        service.execute_run(
            run=run,
            strategy_version=strategy_version,
            candles=(),
            initial_equity=100000.0,
        )


def test_execute_run_is_deterministic(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    first = service.execute_run(
        run=run,
        strategy_version=strategy_version,
        candles=candles,
        initial_equity=100000.0,
    )
    second = service.execute_run(
        run=run,
        strategy_version=strategy_version,
        candles=candles,
        initial_equity=100000.0,
    )

    assert first == second


def test_execute_run_marks_run_completed(tmp_path) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)

    run = make_run(service, strategy_version, candles)

    service.execute_run(
        run=run,
        strategy_version=strategy_version,
        candles=candles,
        initial_equity=100000.0,
    )

    persisted = service._repository.get(run.run_id)

    assert persisted.status.value == "COMPLETED"


def test_execute_run_marks_run_failed_when_integrity_fails(
    tmp_path,
    monkeypatch,
) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    failure_report = ResearchIntegrityReport(
        status=ResearchIntegrityStatus.FAIL,
        findings=(
            ResearchIntegrityFinding(
                severity=ResearchIntegritySeverity.FAIL,
                code="TEST_INTEGRITY_FAILURE",
                message="simulated integrity failure",
            ),
        ),
    )

    monkeypatch.setattr(
        "private_quant_terminal.research.service.ResearchIntegrityAnalyzer.analyze",
        lambda self, execution: failure_report,
    )

    with pytest.raises(
        ValueError,
        match="research execution failed integrity validation",
    ):
        service.execute_run(
            run=run,
            strategy_version=strategy_version,
            candles=candles,
            initial_equity=100000.0,
        )

    persisted = service._repository.get(run.run_id)

    assert persisted.status is ResearchRunStatus.FAILED


def test_execute_run_allows_integrity_warnings(
    tmp_path,
    monkeypatch,
) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)
    run = make_run(service, strategy_version, candles)

    warning_report = ResearchIntegrityReport(
        status=ResearchIntegrityStatus.WARN,
        findings=(
            ResearchIntegrityFinding(
                severity=ResearchIntegritySeverity.WARN,
                code="TEST_INTEGRITY_WARNING",
                message="simulated integrity warning",
            ),
        ),
    )

    monkeypatch.setattr(
        "private_quant_terminal.research.service.ResearchIntegrityAnalyzer.analyze",
        lambda self, execution: warning_report,
    )

    result = service.execute_run(
        run=run,
        strategy_version=strategy_version,
        candles=candles,
        initial_equity=100000.0,
    )

    assert result.run.status is ResearchRunStatus.COMPLETED


def test_execute_run_marks_run_failed_when_execution_fails(
    tmp_path,
    monkeypatch,
) -> None:
    candles = make_candles()
    strategy_version = make_strategy_version()
    service = make_service(tmp_path)

    run = make_run(service, strategy_version, candles)

    def fail_execute(self, request):
        raise RuntimeError("simulated execution failure")

    monkeypatch.setattr(
        "private_quant_terminal.research.service.ResearchExecutor.execute",
        fail_execute,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated execution failure",
    ):
        service.execute_run(
            run=run,
            strategy_version=strategy_version,
            candles=candles,
            initial_equity=100000.0,
        )

    persisted = service._repository.get(run.run_id)

    assert persisted.status.value == "FAILED"
