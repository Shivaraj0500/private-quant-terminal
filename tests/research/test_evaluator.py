from private_quant_terminal.research.evaluator import (
    StrategyDecision,
    evaluate_strategy,
)
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
    TakeProfit,
    TakeProfitType,
)


def make_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="evaluator-test",
        name="Evaluator Test",
        description="Strategy evaluator test.",
        instruments=("RELIANCE",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        entry_conditions=(
            StrategyCondition(
                indicator="EMA_20",
                operator=ConditionOperator.GREATER_THAN,
                value=100.0,
            ),
            StrategyCondition(
                indicator="RSI_14",
                operator=ConditionOperator.LESS_THAN,
                value=70.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="EMA_20",
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


def test_strategy_returns_entry_when_all_entry_conditions_match() -> None:
    assert (
        evaluate_strategy(
            make_strategy(),
            {
                "EMA_20": 105.0,
                "RSI_14": 60.0,
            },
        )
        is StrategyDecision.ENTRY
    )


def test_strategy_returns_exit_when_entry_does_not_match() -> None:
    assert (
        evaluate_strategy(
            make_strategy(),
            {
                "EMA_20": 90.0,
                "RSI_14": 60.0,
            },
        )
        is StrategyDecision.EXIT
    )


def test_strategy_returns_hold_when_neither_entry_nor_exit_matches() -> None:
    assert (
        evaluate_strategy(
            make_strategy(),
            {
                "EMA_20": 98.0,
                "RSI_14": 60.0,
            },
        )
        is StrategyDecision.HOLD
    )


def test_entry_has_priority_when_both_conditions_match() -> None:
    assert (
        evaluate_strategy(
            make_strategy(),
            {
                "EMA_20": 105.0,
                "RSI_14": 60.0,
            },
        )
        is StrategyDecision.ENTRY
    )


def test_missing_indicator_propagates_as_key_error() -> None:
    try:
        evaluate_strategy(
            make_strategy(),
            {"EMA_20": 105.0},
        )
    except KeyError as exc:
        assert str(exc) == "'Indicator value not available: RSI_14'"
    else:
        raise AssertionError("Expected missing indicator to raise KeyError.")
