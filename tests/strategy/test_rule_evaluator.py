from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.actions import EnterAction
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import constant, price
from private_quant_terminal.strategy.options import (
    OptionQuantity,
    OptionSelector,
    OptionType,
    StrikeSelection,
)
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rule_evaluator import (
    RuleEvaluationResult,
    StrategyRuleEvaluator,
    TriggeredRule,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.variables import VariableMutation


def candles(count: int = 60) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    return [
        Candle(
            timestamp=start + timedelta(minutes=index),
            open=100.0 + index,
            high=101.0 + index,
            low=99.0 + index,
            close=100.0 + index + (index % 3) * 0.25,
            volume=1000.0 + index * 25.0,
        )
        for index in range(count)
    ]


def make_entry_action(group_id: str = "entry") -> EnterAction:
    selector = OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.CALL,
        strike_selection=StrikeSelection.ATM,
    )

    leg = StrategyLeg(
        action=LegAction.BUY,
        instrument_type=LegInstrumentType.OPTION,
        option=selector,
        quantity=OptionQuantity(1),
    )

    group = PositionGroup(
        group_id=group_id,
        name="ATM Call",
        legs=(leg,),
    )

    return EnterAction(position=group)


def make_rule(
    rule_id: str,
    *,
    priority: int,
    threshold: float,
) -> StrategyRule:
    return StrategyRule(
        rule_id=rule_id,
        name=rule_id,
        condition=compare(
            price("close"),
            ">",
            constant(threshold),
        ),
        actions=(make_entry_action(rule_id),),
        priority=priority,
    )


def test_evaluator_returns_triggered_rules() -> None:
    rules = (make_rule("entry", priority=10, threshold=100),)

    result = StrategyRuleEvaluator().evaluate(
        rules,
        candles(),
        index=len(candles()) - 1,
    )

    assert isinstance(result, RuleEvaluationResult)
    assert len(result.triggered_rules) == 1
    assert result.triggered_rules[0].rule_id == "entry"
    assert len(result.actions) == 1


def test_evaluator_filters_rules_by_current_state() -> None:
    entry_rule = StrategyRule(
        rule_id="entry",
        name="entry",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("entry"),),
        priority=20,
        states=("ENTRY",),
    )

    managing_rule = StrategyRule(
        rule_id="managing",
        name="managing",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("managing"),),
        priority=10,
        states=("MANAGING",),
    )

    result = StrategyRuleEvaluator().evaluate(
        (entry_rule, managing_rule),
        candles(),
        index=len(candles()) - 1,
        current_state="ENTRY",
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == ("entry",)


def test_evaluator_keeps_unscoped_rules_active_in_every_state() -> None:
    universal_rule = make_rule(
        "universal",
        priority=20,
        threshold=100,
    )

    managing_rule = StrategyRule(
        rule_id="managing",
        name="managing",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("managing"),),
        priority=10,
        states=("MANAGING",),
    )

    result = StrategyRuleEvaluator().evaluate(
        (universal_rule, managing_rule),
        candles(),
        index=len(candles()) - 1,
        current_state="ENTRY",
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == ("universal",)


def test_evaluator_preserves_legacy_behavior_without_current_state() -> None:
    entry_rule = StrategyRule(
        rule_id="entry",
        name="entry",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("entry"),),
        priority=20,
        states=("ENTRY",),
    )

    managing_rule = StrategyRule(
        rule_id="managing",
        name="managing",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("managing"),),
        priority=10,
        states=("MANAGING",),
    )

    result = StrategyRuleEvaluator().evaluate(
        (entry_rule, managing_rule),
        candles(),
        index=len(candles()) - 1,
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == (
        "entry",
        "managing",
    )


def test_evaluator_rejects_empty_current_state() -> None:
    with pytest.raises(ValueError, match="current_state must not be empty"):
        StrategyRuleEvaluator().evaluate(
            (make_rule("entry", priority=10, threshold=100),),
            candles(),
            index=len(candles()) - 1,
            current_state="   ",
        )


def test_evaluator_does_not_evaluate_filtered_rules() -> None:
    class StubConditionEvaluator:
        def __init__(self) -> None:
            self.calls = 0

        def evaluate(
            self,
            condition,
            candles,
            index,
            context=None,
        ) -> bool:
            self.calls += 1
            return True

    filtered_rule = StrategyRule(
        rule_id="filtered",
        name="filtered",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("filtered"),),
        priority=20,
        states=("MANAGING",),
    )

    active_rule = StrategyRule(
        rule_id="active",
        name="active",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(make_entry_action("active"),),
        priority=10,
        states=("ENTRY",),
    )

    condition_evaluator = StubConditionEvaluator()

    result = StrategyRuleEvaluator(
        condition_evaluator=condition_evaluator,
    ).evaluate(
        (filtered_rule, active_rule),
        candles(),
        index=len(candles()) - 1,
        current_state="ENTRY",
    )

    assert condition_evaluator.calls == 1
    assert tuple(rule.rule_id for rule in result.triggered_rules) == ("active",)


def test_evaluator_ignores_false_rules() -> None:
    rules = (make_rule("entry", priority=10, threshold=10_000),)

    result = StrategyRuleEvaluator().evaluate(
        rules,
        candles(),
        index=len(candles()) - 1,
    )

    assert result.triggered_rules == ()
    assert result.actions == ()


def test_evaluator_ignores_disabled_rules() -> None:
    rule = make_rule(
        "disabled",
        priority=10,
        threshold=100,
    )

    rule = StrategyRule(
        rule_id=rule.rule_id,
        name=rule.name,
        condition=rule.condition,
        actions=rule.actions,
        priority=rule.priority,
        enabled=False,
    )

    result = StrategyRuleEvaluator().evaluate(
        (rule,),
        candles(),
        index=len(candles()) - 1,
    )

    assert result.triggered_rules == ()


def test_evaluator_orders_triggered_rules_by_priority() -> None:
    rules = (
        make_rule("low", priority=10, threshold=100),
        make_rule("high", priority=100, threshold=100),
        make_rule("middle", priority=50, threshold=100),
    )

    result = StrategyRuleEvaluator().evaluate(
        rules,
        candles(),
        index=len(candles()) - 1,
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == (
        "high",
        "middle",
        "low",
    )


def test_evaluator_uses_rule_id_as_deterministic_tiebreaker() -> None:
    rules = (
        make_rule("z-rule", priority=10, threshold=100),
        make_rule("a-rule", priority=10, threshold=100),
    )

    result = StrategyRuleEvaluator().evaluate(
        rules,
        candles(),
        index=len(candles()) - 1,
    )

    assert tuple(rule.rule_id for rule in result.triggered_rules) == (
        "a-rule",
        "z-rule",
    )


def test_evaluator_can_use_injected_condition_evaluator() -> None:
    class StubConditionEvaluator:
        def __init__(self) -> None:
            self.calls = 0

        def evaluate(
            self,
            condition,
            candles,
            index,
            context=None,
        ) -> bool:
            self.calls += 1
            return True

    condition_evaluator = StubConditionEvaluator()

    result = StrategyRuleEvaluator(
        condition_evaluator=condition_evaluator,
    ).evaluate(
        (
            make_rule(
                "entry",
                priority=10,
                threshold=10_000,
            ),
        ),
        candles(),
        index=len(candles()) - 1,
    )

    assert condition_evaluator.calls == 1
    assert len(result.triggered_rules) == 1


def test_triggered_rule_is_immutable() -> None:
    triggered = TriggeredRule(
        rule_id="entry",
        actions=(make_entry_action(),),
    )

    with pytest.raises(AttributeError):
        triggered.rule_id = "changed"


def test_evaluator_returns_variable_mutations_from_triggered_rules() -> None:
    mutation = VariableMutation(
        name="roll_count",
        value=1,
    )

    rule = StrategyRule(
        rule_id="roll",
        name="roll",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        variable_mutations=(mutation,),
    )

    result = StrategyRuleEvaluator().evaluate(
        (rule,),
        candles(),
        index=len(candles()) - 1,
    )

    assert len(result.triggered_rules) == 1
    assert result.triggered_rules[0].variable_mutations == (mutation,)
    assert result.variable_mutations == (mutation,)


def test_evaluator_aggregates_variable_mutations_in_priority_order() -> None:
    low_mutation = VariableMutation(
        name="low_marker",
        value=1,
    )
    high_mutation = VariableMutation(
        name="high_marker",
        value=2,
    )

    low_rule = StrategyRule(
        rule_id="low",
        name="low",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        variable_mutations=(low_mutation,),
        priority=10,
    )

    high_rule = StrategyRule(
        rule_id="high",
        name="high",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        variable_mutations=(high_mutation,),
        priority=100,
    )

    result = StrategyRuleEvaluator().evaluate(
        (low_rule, high_rule),
        candles(),
        index=len(candles()) - 1,
    )

    assert result.variable_mutations == (
        high_mutation,
        low_mutation,
    )


def test_evaluator_returns_no_variable_mutations_for_false_rules() -> None:
    rule = StrategyRule(
        rule_id="roll",
        name="roll",
        condition=compare(
            price("close"),
            ">",
            constant(10_000),
        ),
        variable_mutations=(
            VariableMutation(
                name="roll_count",
                value=1,
            ),
        ),
    )

    result = StrategyRuleEvaluator().evaluate(
        (rule,),
        candles(),
        index=len(candles()) - 1,
    )

    assert result.triggered_rules == ()
    assert result.variable_mutations == ()
