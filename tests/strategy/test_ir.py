from datetime import UTC, datetime

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


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-001",
        name="EMA Momentum",
        description="Example declarative momentum strategy.",
        instruments=("RELIANCE", "TCS"),
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


def test_strategy_definition_is_immutable() -> None:
    strategy = make_strategy()

    assert strategy.status is StrategyStatus.DRAFT

    try:
        strategy.name = "Changed"
    except AttributeError:
        pass
    else:
        raise AssertionError("StrategyDefinition must be immutable.")


def test_strategy_definition_contains_canonical_fields() -> None:
    strategy = make_strategy()

    assert strategy.strategy_id == "strategy-001"
    assert strategy.instruments == ("RELIANCE", "TCS")
    assert strategy.timeframe is StrategyTimeframe.ONE_HOUR
    assert len(strategy.entry_conditions) == 1
    assert len(strategy.exit_conditions) == 1
    assert strategy.position_sizing.value == 10.0
    assert strategy.stop_loss.value == 2.0
    assert strategy.take_profit.value == 2.0


def test_strategy_version_is_immutable() -> None:
    strategy = make_strategy()

    version = StrategyVersion(
        strategy_id=strategy.strategy_id,
        version=1,
        specification=strategy,
        created_at=datetime.now(UTC),
    )

    assert version.version == 1
    assert version.specification is strategy

    try:
        version.version = 2
    except AttributeError:
        pass
    else:
        raise AssertionError("StrategyVersion must be immutable.")
