from datetime import UTC, datetime

import pytest

from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
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
from private_quant_terminal.strategy.runtime_state import StrategyRuntimeState
from private_quant_terminal.strategy.variables import SessionContext


def option_group(group_id: str) -> PositionGroup:
    selector = OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.CALL,
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


def timestamp(hour: int, minute: int) -> datetime:
    return datetime(
        2026,
        8,
        30,
        hour,
        minute,
        tzinfo=UTC,
    )


def runtime() -> StrategyRuntimeState:
    return StrategyRuntimeState(
        session=SessionContext(
            current_time=timestamp(10, 0),
        )
    )


def test_enter_updates_session_state() -> None:
    state = runtime()

    result = state.apply(
        EnterAction(position=option_group("entry")),
        timestamp(10, 15),
    )

    assert result.session.current_time == timestamp(10, 15)
    assert result.session.entries_today == 1
    assert result.session.trades_today == 1
    assert result.session.bars_since_entry == 0
    assert result.session.minutes_since_entry == 0.0
    assert result.session.last_entry_time == timestamp(10, 15)


def test_exit_updates_last_exit_time_without_incrementing_entries() -> None:
    state = StrategyRuntimeState(
        session=SessionContext(
            current_time=timestamp(10, 0),
            entries_today=2,
            trades_today=2,
            bars_since_entry=5,
            minutes_since_entry=15.0,
            last_entry_time=timestamp(9, 45),
        )
    )

    result = state.apply(
        ExitAction(group_id="entry"),
        timestamp(10, 30),
    )

    assert result.session.entries_today == 2
    assert result.session.trades_today == 2
    assert result.session.bars_since_entry == 5
    assert result.session.minutes_since_entry == 15.0
    assert result.session.last_entry_time == timestamp(9, 45)
    assert result.session.last_exit_time == timestamp(10, 30)


def test_advance_bar_updates_bar_and_elapsed_time() -> None:
    state = StrategyRuntimeState(
        session=SessionContext(
            current_time=timestamp(10, 0),
            last_entry_time=timestamp(9, 45),
            minutes_since_entry=15.0,
        )
    )

    result = state.advance_bar(
        timestamp(10, 1),
        minutes=1.0,
    )

    assert result.session.current_time == timestamp(10, 1)
    assert result.session.bars_since_entry == 1
    assert result.session.minutes_since_entry == 16.0


def test_advance_bar_without_entry_keeps_elapsed_time_unset() -> None:
    state = runtime()

    result = state.advance_bar(
        timestamp(10, 1),
        minutes=1.0,
    )

    assert result.session.bars_since_entry == 1
    assert result.session.minutes_since_entry is None


def test_negative_bar_duration_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="minutes cannot be negative",
    ):
        runtime().advance_bar(
            timestamp(10, 1),
            minutes=-1.0,
        )


def test_runtime_state_is_immutable() -> None:
    state = runtime()

    with pytest.raises(AttributeError):
        state.session = SessionContext(
            current_time=timestamp(10, 1),
        )
