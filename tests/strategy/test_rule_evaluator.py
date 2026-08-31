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
