from dataclasses import replace

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
    StrategyTimeframe,
    TakeProfit,
    TakeProfitType,
    validate_strategy,
)


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-001",
        name="EMA Momentum",
        description="Example strategy.",
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


def test_valid_strategy_passes() -> None:
    result = validate_strategy(make_strategy())

    assert result.valid is True
    assert result.issues == ()


def test_empty_universe_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        instruments=(),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "instruments"
        for issue in result.issues
    )


def test_missing_entry_conditions_are_rejected() -> None:
    strategy = replace(
        make_strategy(),
        entry_conditions=(),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "entry_conditions"
        for issue in result.issues
    )


def test_invalid_position_sizing_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.PERCENT_OF_EQUITY,
            value=101.0,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "position_sizing.value"
        for issue in result.issues
    )


def test_negative_execution_cost_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        execution=ExecutionAssumptions(
            order_type=OrderType.MARKET,
            slippage_bps=-1.0,
            transaction_cost_bps=10.0,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "execution.slippage_bps"
        for issue in result.issues
    )


def test_missing_stop_loss_value_is_rejected() -> None:
    strategy = replace(
        make_strategy(),
        stop_loss=StopLoss(
            type=StopLossType.PERCENT,
            value=None,
        ),
    )

    result = validate_strategy(strategy)

    assert result.valid is False
    assert any(
        issue.field == "stop_loss.value"
        for issue in result.issues
    )
