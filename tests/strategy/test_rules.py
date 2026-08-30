import pytest

from private_quant_terminal.strategy.actions import (
    EnterAction,
)
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import (
    constant,
    price,
)
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
from private_quant_terminal.strategy.rules import StrategyRule


def make_entry_action() -> EnterAction:
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
        group_id="entry",
        name="ATM Call",
        legs=(leg,),
    )

    return EnterAction(position=group)


def test_strategy_rule_models_when_then_behavior() -> None:
    condition = compare(
        price("close"),
        ">",
        constant(100),
    )

    rule = StrategyRule(
        rule_id="entry-rule",
        name="Momentum Entry",
        condition=condition,
        actions=(make_entry_action(),),
        priority=10,
    )

    assert rule.rule_id == "entry-rule"
    assert rule.name == "Momentum Entry"
    assert rule.priority == 10
    assert rule.enabled is True
    assert len(rule.actions) == 1


def test_rule_requires_action() -> None:
    condition = compare(
        price("close"),
        ">",
        constant(100),
    )

    with pytest.raises(
        ValueError,
        match="at least one action",
    ):
        StrategyRule(
            rule_id="empty",
            name="Empty",
            condition=condition,
            actions=(),
        )


def test_rule_priority_cannot_be_negative() -> None:
    condition = compare(
        price("close"),
        ">",
        constant(100),
    )

    with pytest.raises(
        ValueError,
        match="priority cannot be negative",
    ):
        StrategyRule(
            rule_id="negative",
            name="Negative",
            condition=condition,
            actions=(make_entry_action(),),
            priority=-1,
        )
