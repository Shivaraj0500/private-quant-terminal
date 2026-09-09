from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.data.identity import DatasetIdentity, candle_dataset_hash
from private_quant_terminal.models import Candle
from private_quant_terminal.persistence import Database
from private_quant_terminal.research import (
    ResearchAnalysisResult,
    ResearchParameters,
    ResearchRunService,
    ResearchRunStatus,
)
from private_quant_terminal.research.repository import ResearchRunRepository
from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    ComparisonOperator,
)
from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    PriceExpression,
    PriceField,
)
from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
)
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy import (
    ExecutionAssumptions,
    PositionSizingMethod,
    PositionSizing,
    StopLoss,
    StopLossType,
    StrategyIR,
    StrategyStatus,
    StrategyTimeframe,
    TakeProfit,
    TakeProfitType,
)


def make_candles() -> tuple[Candle, ...]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return (
        Candle(
            timestamp=start,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000.0,
        ),
        Candle(
            timestamp=start + timedelta(minutes=5),
            open=110.0,
            high=111.0,
            low=109.0,
            close=110.0,
            volume=1000.0,
        ),
    )


def make_strategy() -> StrategyIR:
    group = PositionGroup(
        group_id="group-1",
        name="Test Position",
        legs=(
            StrategyLeg(
                instrument_type=LegInstrumentType.EQUITY,
                symbol="TEST",
                action=LegAction.BUY,
                quantity=1.0,
            ),
        ),
    )

    return StrategyIR(
        strategy_id="service-v2-test",
        name="Service V2 Test",
        description="Canonical V2 research service integration test.",
        version=1,
        status=StrategyStatus.VALIDATED,
        instruments=("TEST",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        position_groups=(group,),
        rules=(
            StrategyRule(
                rule_id="enter",
                name="Enter",
                condition=ComparisonCondition(
                    left=PriceExpression(field=PriceField.CLOSE),
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    right=ConstantExpression(100.0),
                ),
                actions=(
                    EnterAction(position=group),
                ),
            ),
            StrategyRule(
                rule_id="exit",
                name="Exit",
                condition=ComparisonCondition(
                    left=PriceExpression(field=PriceField.CLOSE),
                    operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
                    right=ConstantExpression(105.0),
                ),
                actions=(
                    ExitAction(group_id="group-1"),
                ),
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.FIXED_QUANTITY,
            value=1.0,
        ),
        stop_loss=StopLoss(type=StopLossType.NONE),
        take_profit=TakeProfit(type=TakeProfitType.NONE),
        execution=ExecutionAssumptions(),
    )


def make_dataset(candles: tuple[Candle, ...]) -> DatasetIdentity:
    return DatasetIdentity(
        dataset_hash=candle_dataset_hash(list(candles)),
        symbol="TEST",
        timeframe="5m",
        candle_count=len(candles),
        start_time=candles[0].timestamp,
        end_time=candles[-1].timestamp,
    )


def make_service(tmp_path) -> ResearchRunService:
    return ResearchRunService(
        repository=ResearchRunRepository(
            Database(tmp_path / "research-v2.db")
        )
    )


def make_run(service: ResearchRunService, strategy: StrategyIR, candles):
    return service.create_run_v2(
        strategy=strategy,
        dataset=make_dataset(candles),
        parameters=ResearchParameters(values={}),
        run_id="service-v2-run",
    ).run


def test_create_run_v2_persists_canonical_strategy_identity(tmp_path) -> None:
    candles = make_candles()
    strategy = make_strategy()
    service = make_service(tmp_path)

    run = make_run(service, strategy, candles)

    assert run.strategy_id == strategy.strategy_id
    assert run.strategy_version == strategy.version
    assert run.strategy_hash
    assert run.dataset_hash == candle_dataset_hash(list(candles))
    assert run.status is ResearchRunStatus.CREATED


def test_execute_run_v2_returns_complete_analysis_result(tmp_path) -> None:
    candles = make_candles()
    strategy = make_strategy()
    service = make_service(tmp_path)
    run = make_run(service, strategy, candles)

    result = service.execute_run_v2(
        run=run,
        strategy=strategy,
        candles=candles,
        initial_equity=1000.0,
    )

    assert isinstance(result, ResearchAnalysisResult)
    assert result.run.run_id == run.run_id
    assert result.run.status is ResearchRunStatus.COMPLETED
    assert result.execution.run_id == run.run_id
    assert len(result.execution.trades) == 1
    assert result.execution.trades[0].gross_pnl == 10.0
    assert result.execution.final_equity == 1010.0
    assert result.integrity.status.value == "PASS"
    assert result.performance.trading_performance.realized_pnl == 10.0


def test_execute_run_v2_persists_result(tmp_path) -> None:
    candles = make_candles()
    strategy = make_strategy()
    service = make_service(tmp_path)
    run = make_run(service, strategy, candles)

    result = service.execute_run_v2(
        run=run,
        strategy=strategy,
        candles=candles,
        initial_equity=1000.0,
    )

    persisted_execution, persisted_integrity, persisted_performance, persisted_intelligence = (
        service._repository.get_result(run.run_id)
    )

    assert persisted_execution.final_equity == result.execution.final_equity
    assert persisted_execution.trades == result.execution.trades
    assert persisted_integrity.status == result.integrity.status


def test_execute_run_v2_rejects_strategy_hash_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy = make_strategy()
    service = make_service(tmp_path)
    run = make_run(service, strategy, candles)

    altered = StrategyIR(
        strategy_id=strategy.strategy_id,
        name="Altered V2 Strategy",
        description=strategy.description,
        version=strategy.version,
        status=strategy.status,
        instruments=strategy.instruments,
        timeframe=strategy.timeframe,
        variables=strategy.variables,
        rules=strategy.rules,
        states=strategy.states,
        transitions=strategy.transitions,
        data_requirements=strategy.data_requirements,
        position_groups=strategy.position_groups,
        session=strategy.session,
        position_sizing=strategy.position_sizing,
        stop_loss=strategy.stop_loss,
        take_profit=strategy.take_profit,
        execution=strategy.execution,
    )

    with pytest.raises(
        ValueError,
        match="strategy hash does not match research run",
    ):
        service.execute_run_v2(
            run=run,
            strategy=altered,
            candles=candles,
            initial_equity=1000.0,
        )


def test_execute_run_v2_rejects_dataset_hash_mismatch(tmp_path) -> None:
    candles = make_candles()
    strategy = make_strategy()
    service = make_service(tmp_path)
    run = make_run(service, strategy, candles)

    different = (
        candles[0],
        Candle(
            timestamp=candles[1].timestamp,
            open=120.0,
            high=121.0,
            low=119.0,
            close=120.0,
            volume=1000.0,
        ),
    )

    with pytest.raises(
        ValueError,
        match="dataset hash does not match research run",
    ):
        service.execute_run_v2(
            run=run,
            strategy=strategy,
            candles=different,
            initial_equity=1000.0,
        )
