
import pytest

from private_quant_terminal.persistence import Database
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
    StrategyLifecycleService,
    StrategyStatus,
    StrategyTimeframe,
    StrategyVersionRepository,
    TakeProfit,
    TakeProfitType,
)


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-lifecycle",
        name="Lifecycle Strategy",
        description="Strategy lifecycle test.",
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.ONE_HOUR,
        entry_conditions=(
            StrategyCondition(
                indicator="EMA_20",
                operator=ConditionOperator.GREATER_THAN,
                value=0.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="RSI_14",
                operator=ConditionOperator.GREATER_THAN,
                value=70.0,
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.PERCENT_OF_EQUITY,
            value=10.0,
        ),
        stop_loss=StopLoss(
            type=StopLossType.PERCENT,
            value=2.0,
        ),
        take_profit=TakeProfit(
            type=TakeProfitType.RISK_REWARD,
            value=2.0,
        ),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=5.0,
            transaction_cost_bps=10.0,
        ),
    )


def test_create_version_validates_and_persists(tmp_path) -> None:
    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    strategy = make_strategy()

    result = service.create_version(strategy)

    assert result.validation.valid is True
    assert result.version.version == 1
    assert (
        result.version.specification.status
        is StrategyStatus.VALIDATED
    )

    restored = repository.get(
        strategy_id="strategy-lifecycle",
        version=1,
    )

    assert restored == result.version


def test_create_version_increments_version(tmp_path) -> None:
    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    first = service.create_version(make_strategy())
    second = service.create_version(make_strategy())

    assert first.version.version == 1
    assert second.version.version == 2


def test_invalid_strategy_is_not_persisted(tmp_path) -> None:
    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    strategy = make_strategy()

    invalid = StrategyDefinition(
        strategy_id=strategy.strategy_id,
        name=strategy.name,
        description=strategy.description,
        instruments=(),
        timeframe=strategy.timeframe,
        entry_conditions=strategy.entry_conditions,
        exit_conditions=strategy.exit_conditions,
        position_sizing=strategy.position_sizing,
        stop_loss=strategy.stop_loss,
        take_profit=strategy.take_profit,
        execution=strategy.execution,
    )

    with pytest.raises(ValueError, match="Cannot create strategy version"):
        service.create_version(invalid)

    assert repository.next_version("strategy-lifecycle") == 1


def test_input_strategy_remains_draft(tmp_path) -> None:
    repository = StrategyVersionRepository(
        Database(tmp_path / "strategy.db")
    )
    service = StrategyLifecycleService(repository)

    strategy = make_strategy()

    result = service.create_version(strategy)

    assert strategy.status is StrategyStatus.DRAFT
    assert (
        result.version.specification.status
        is StrategyStatus.VALIDATED
    )
