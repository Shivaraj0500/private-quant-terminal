import pytest

from private_quant_terminal.models import Candle
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
    strategy_definition_to_ir,
)
from private_quant_terminal.strategy.actions import EnterAction, ExitAction
from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    LogicalCondition,
    LogicalOperator,
)
from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    IndicatorExpression,
)
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
)


def make_legacy_strategy() -> StrategyDefinition:
    return StrategyDefinition(
        strategy_id="strategy-legacy",
        name="Legacy Momentum",
        description="Legacy strategy for compatibility testing.",
        instruments=("RELIANCE", "TCS"),
        timeframe=StrategyTimeframe.ONE_HOUR,
        entry_conditions=(
            StrategyCondition(
                indicator="EMA_20",
                operator=ConditionOperator.GREATER_THAN,
                value=0.0,
            ),
            StrategyCondition(
                indicator="RSI_14",
                operator=ConditionOperator.LESS_THAN,
                value=70.0,
            ),
        ),
        exit_conditions=(
            StrategyCondition(
                indicator="RSI_14",
                operator=ConditionOperator.GREATER_THAN,
                value=80.0,
            ),
        ),
        position_sizing=PositionSizing(
            method=PositionSizingMethod.FIXED_QUANTITY,
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
        status=StrategyStatus.VALIDATED,
    )


def test_strategy_definition_to_ir_preserves_identity_and_metadata() -> None:
    legacy = make_legacy_strategy()

    converted = strategy_definition_to_ir(legacy, version=7)

    assert converted.strategy_id == legacy.strategy_id
    assert converted.name == legacy.name
    assert converted.description == legacy.description
    assert converted.version == 7
    assert converted.status is legacy.status
    assert converted.instruments == legacy.instruments
    assert converted.timeframe is legacy.timeframe


def test_strategy_definition_to_ir_combines_entry_conditions_with_and() -> None:
    converted = strategy_definition_to_ir(
        make_legacy_strategy(),
        version=1,
    )

    entry_rule = converted.rules[0]

    assert entry_rule.rule_id == "legacy-entry"
    assert isinstance(entry_rule.condition, LogicalCondition)
    assert entry_rule.condition.operator is LogicalOperator.AND
    assert len(entry_rule.condition.conditions) == 2
    assert isinstance(entry_rule.actions[0], EnterAction)

    first = entry_rule.condition.conditions[0]
    assert isinstance(first, ComparisonCondition)
    assert isinstance(first.left, IndicatorExpression)
    assert first.left.name == "EMA_20"
    assert isinstance(first.right, ConstantExpression)
    assert first.right.value == 0.0


def test_strategy_definition_to_ir_combines_exit_conditions_with_and() -> None:
    converted = strategy_definition_to_ir(
        make_legacy_strategy(),
        version=1,
    )

    exit_rule = converted.rules[1]

    assert exit_rule.rule_id == "legacy-exit"
    assert isinstance(exit_rule.condition, LogicalCondition)
    assert exit_rule.condition.operator is LogicalOperator.AND
    assert len(exit_rule.condition.conditions) == 1
    assert isinstance(exit_rule.actions[0], ExitAction)
    assert exit_rule.actions[0].group_id == "legacy-position"


def test_strategy_definition_to_ir_creates_position_legs_for_all_instruments() -> None:
    converted = strategy_definition_to_ir(
        make_legacy_strategy(),
        version=1,
    )

    group = converted.position_groups[0]

    assert group.group_id == "legacy-position"
    assert len(group.legs) == 2

    assert group.legs[0].action is LegAction.BUY
    assert group.legs[0].instrument_type is LegInstrumentType.EQUITY
    assert group.legs[0].symbol == "RELIANCE"

    assert group.legs[1].symbol == "TCS"


def test_strategy_definition_to_ir_preserves_management_and_execution() -> None:
    legacy = make_legacy_strategy()

    converted = strategy_definition_to_ir(legacy, version=1)

    assert converted.position_sizing == legacy.position_sizing
    assert converted.stop_loss == legacy.stop_loss
    assert converted.take_profit == legacy.take_profit
    assert converted.execution == legacy.execution


def test_strategy_definition_to_ir_rejects_invalid_version() -> None:
    with pytest.raises(
        ValueError,
        match="Strategy version must be greater than zero.",
    ):
        strategy_definition_to_ir(make_legacy_strategy(), version=0)


def make_candles(
    closes: list[float],
) -> list[Candle]:
    from datetime import UTC, datetime, timedelta

    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=close,
            high=close + 1.0,
            low=close - 1.0,
            close=close,
            volume=1000.0,
        )
        for index, close in enumerate(closes)
    ]


def test_legacy_entry_and_exit_rules_preserve_v1_decision_priority() -> None:
    from private_quant_terminal.research.evaluator import (
        StrategyDecision,
        evaluate_strategy,
    )
    from private_quant_terminal.strategy.rule_evaluator import (
        StrategyRuleEvaluator,
    )

    legacy = make_legacy_strategy()
    converted = strategy_definition_to_ir(legacy, version=1)

    data = make_candles([100.0])

    # The V2 expression engine does not use the legacy indicator mapping
    # directly, so verify the structural rule semantics through the
    # converted conditions with a controlled condition evaluator.
    class StubConditionEvaluator:
        def __init__(self, values: tuple[bool, bool]) -> None:
            self.values = iter(values)

        def evaluate(
            self,
            condition,
            candles,
            index,
            context=None,
        ) -> bool:
            return next(self.values)

    assert evaluate_strategy(
        legacy,
        {
            "EMA_20": 1.0,
            "RSI_14": 60.0,
        },
    ) is StrategyDecision.ENTRY

    result = StrategyRuleEvaluator(
        condition_evaluator=StubConditionEvaluator((True, True)),
    ).evaluate(
        converted.rules,
        data,
        0,
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == (
        "legacy-entry",
        "legacy-exit",
    )
    assert isinstance(result.actions[0], EnterAction)
    assert isinstance(result.actions[1], ExitAction)
