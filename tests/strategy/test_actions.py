import pytest

from private_quant_terminal.strategy.actions import (
    ActionType,
    EnterAction,
    ExitAction,
    HedgeAction,
    ModifyAction,
    RollAction,
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


def option_group(group_id: str = "entry") -> PositionGroup:
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

    return PositionGroup(
        group_id=group_id,
        name="ATM Call",
        legs=(leg,),
    )


def test_enter_action() -> None:
    action = EnterAction(position=option_group())

    assert action.action_type is ActionType.ENTER
    assert action.position.group_id == "entry"


def test_exit_action() -> None:
    action = ExitAction(group_id="entry")

    assert action.action_type is ActionType.EXIT


def test_modify_action() -> None:
    action = ModifyAction(
        group_id="entry",
        changes=(("stop_loss_percent", 25.0),),
    )

    assert action.action_type is ActionType.MODIFY


def test_roll_action() -> None:
    action = RollAction(
        group_id="entry",
        replacement=option_group("rolled"),
    )

    assert action.action_type is ActionType.ROLL
    assert action.replacement.group_id == "rolled"


def test_hedge_action() -> None:
    action = HedgeAction(
        group_id="entry",
        hedge=option_group("hedge"),
    )

    assert action.action_type is ActionType.HEDGE


def test_exit_requires_group_id() -> None:
    with pytest.raises(
        ValueError,
        match="Exit group ID must not be empty",
    ):
        ExitAction(group_id=" ")
