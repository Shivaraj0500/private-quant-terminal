import pytest

from private_quant_terminal.strategy.action_processor import (
    ActionProcessor,
)
from private_quant_terminal.strategy.actions import (
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
from private_quant_terminal.strategy.states import PositionState


def option_group(
    group_id: str,
    option_type: OptionType = OptionType.CALL,
) -> PositionGroup:
    selector = OptionSelector(
        underlying="BANKNIFTY",
        option_type=option_type,
        strike_selection=StrikeSelection.ATM,
    )

    leg = StrategyLeg(
        action=LegAction.SELL,
        instrument_type=LegInstrumentType.OPTION,
        option=selector,
        quantity=OptionQuantity(1),
    )

    return PositionGroup(
        group_id=group_id,
        name=group_id,
        legs=(leg,),
    )


def test_enter_opens_position_group() -> None:
    processor = ActionProcessor()
    group = option_group("entry")

    result = processor.process(EnterAction(position=group))

    assert processor.get_position("entry") == group
    snapshot = processor.get_state("entry")
    assert snapshot is not None
    assert snapshot.state is PositionState.OPEN
    assert snapshot.entry_count == 1
    assert snapshot.exit_count == 0
    assert result.snapshots == (snapshot,)


def test_exit_closes_position_group() -> None:
    processor = ActionProcessor()
    processor.process(EnterAction(position=option_group("entry")))

    processor.process(ExitAction(group_id="entry"))

    assert processor.get_position("entry") is None

    snapshot = processor.get_state("entry")
    assert snapshot is not None
    assert snapshot.state is PositionState.CLOSED
    assert snapshot.entry_count == 1
    assert snapshot.exit_count == 1


def test_modify_records_changes() -> None:
    processor = ActionProcessor()
    processor.process(EnterAction(position=option_group("entry")))

    action = ModifyAction(
        group_id="entry",
        changes=(
            ("stop_loss_percent", 25.0),
            ("take_profit_percent", 50.0),
        ),
    )

    processor.process(action)

    assert processor.modifications("entry") == action.changes


def test_roll_closes_old_group_and_opens_replacement() -> None:
    processor = ActionProcessor()
    processor.process(EnterAction(position=option_group("entry")))

    replacement = option_group("rolled", OptionType.PUT)

    processor.process(
        RollAction(
            group_id="entry",
            replacement=replacement,
        )
    )

    assert processor.get_position("entry") is None
    assert processor.get_position("rolled") == replacement

    old_state = processor.get_state("entry")
    new_state = processor.get_state("rolled")

    assert old_state is not None
    assert old_state.state is PositionState.CLOSED
    assert old_state.exit_count == 1

    assert new_state is not None
    assert new_state.state is PositionState.OPEN
    assert new_state.entry_count == 1


def test_hedge_requires_parent_and_opens_hedge() -> None:
    processor = ActionProcessor()
    processor.process(EnterAction(position=option_group("entry")))

    hedge = option_group("hedge", OptionType.PUT)

    processor.process(
        HedgeAction(
            group_id="entry",
            hedge=hedge,
        )
    )

    assert processor.get_position("entry") is not None
    assert processor.get_position("hedge") == hedge

    assert processor.get_state("entry").state is PositionState.OPEN
    assert processor.get_state("hedge").state is PositionState.OPEN


def test_enter_rejects_duplicate_group() -> None:
    processor = ActionProcessor()
    group = option_group("entry")

    processor.process(EnterAction(position=group))

    with pytest.raises(
        ValueError,
        match="already open",
    ):
        processor.process(EnterAction(position=group))


def test_exit_rejects_unknown_group() -> None:
    processor = ActionProcessor()

    with pytest.raises(
        KeyError,
        match="Unknown position group",
    ):
        processor.process(ExitAction(group_id="missing"))


def test_modify_rejects_unknown_group() -> None:
    processor = ActionProcessor()

    with pytest.raises(
        KeyError,
        match="Unknown position group",
    ):
        processor.process(
            ModifyAction(
                group_id="missing",
                changes=(("stop_loss_percent", 10.0),),
            )
        )


def test_roll_rejects_unknown_group() -> None:
    processor = ActionProcessor()

    with pytest.raises(
        KeyError,
        match="Unknown position group",
    ):
        processor.process(
            RollAction(
                group_id="missing",
                replacement=option_group("replacement"),
            )
        )


def test_hedge_rejects_unknown_parent() -> None:
    processor = ActionProcessor()

    with pytest.raises(
        KeyError,
        match="Unknown position group",
    ):
        processor.process(
            HedgeAction(
                group_id="missing",
                hedge=option_group("hedge"),
            )
        )


def test_process_all_preserves_action_order() -> None:
    processor = ActionProcessor()

    actions = (
        EnterAction(position=option_group("entry")),
        ModifyAction(
            group_id="entry",
            changes=(("stop_loss_percent", 20.0),),
        ),
        ExitAction(group_id="entry"),
    )

    results = processor.process_all(actions)

    assert tuple(
        result.action for result in results
    ) == actions

    snapshot = processor.get_state("entry")
    assert snapshot is not None
    assert snapshot.state is PositionState.CLOSED
