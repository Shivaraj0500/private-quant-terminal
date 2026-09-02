from datetime import UTC, datetime

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.actions import EnterAction
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.expressions import constant, price
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.state_machine import StrategyStateMachine
from private_quant_terminal.strategy.states import StateTransition, StrategyState


def make_candles() -> tuple[Candle, ...]:
    return (
        Candle(
            timestamp=datetime(2026, 8, 30, 9, 15, tzinfo=UTC),
            open=110.0,
            high=112.0,
            low=108.0,
            close=111.0,
            volume=1000.0,
        ),
    )


def make_action() -> EnterAction:
    return EnterAction(
        position=PositionGroup(
            group_id="entry",
            name="Entry",
            legs=(
                StrategyLeg(
                    action=LegAction.BUY,
                    instrument_type=LegInstrumentType.EQUITY,
                    symbol="NIFTY",
                ),
            ),
        )
    )


def make_condition(threshold: float = 100.0):
    return compare(price("close"), ">", constant(threshold))


def make_state(
    state_id: str,
    *,
    initial: bool = False,
    terminal: bool = False,
) -> StrategyState:
    return StrategyState(
        state_id=state_id,
        name=state_id.title(),
        initial=initial,
        terminal=terminal,
    )


def make_transition(
    transition_id: str,
    *,
    from_state: str = "WAITING",
    to_state: str = "ACTIVE",
    priority: int = 0,
    enabled: bool = True,
    threshold: float = 100.0,
) -> StateTransition:
    return StateTransition(
        transition_id=transition_id,
        from_state=from_state,
        to_state=to_state,
        condition=make_condition(threshold),
        actions=(make_action(),),
        priority=priority,
        enabled=enabled,
    )


def make_machine(
    *,
    states=(
        make_state("WAITING", initial=True),
        make_state("ACTIVE"),
        make_state("DONE", terminal=True),
    ),
    transitions=(),
) -> StrategyStateMachine:
    return StrategyStateMachine(states, transitions)


def test_state_machine_uses_initial_state() -> None:
    machine = make_machine()

    assert machine.current_state == "WAITING"


def test_state_machine_has_no_current_state_without_initial_state() -> None:
    machine = make_machine(
        states=(
            make_state("WAITING"),
            make_state("ACTIVE"),
        ),
    )

    assert machine.current_state is None


def test_state_machine_evaluates_matching_transition() -> None:
    transition = make_transition("activate")
    machine = make_machine(transitions=(transition,))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None
    assert result.transition == transition
    assert result.from_state == "WAITING"
    assert result.to_state == "ACTIVE"


def test_state_machine_ignores_disabled_transitions() -> None:
    transition = make_transition("activate", enabled=False)
    machine = make_machine(transitions=(transition,))

    assert machine.evaluate(make_candles(), 0) is None


def test_state_machine_ignores_transitions_from_other_states() -> None:
    transition = make_transition(
        "finish",
        from_state="ACTIVE",
        to_state="DONE",
    )
    machine = make_machine(transitions=(transition,))

    assert machine.evaluate(make_candles(), 0) is None


def test_state_machine_uses_priority_order() -> None:
    low = make_transition("low", priority=10)
    high = make_transition("high", priority=20)

    machine = make_machine(transitions=(low, high))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None
    assert result.transition.transition_id == "high"


def test_state_machine_uses_transition_id_as_tie_breaker() -> None:
    first = make_transition("a-transition", priority=10)
    second = make_transition("b-transition", priority=10)

    machine = make_machine(transitions=(second, first))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None
    assert result.transition.transition_id == "a-transition"


def test_state_machine_returns_none_when_condition_is_false() -> None:
    transition = make_transition("activate", threshold=200.0)
    machine = make_machine(transitions=(transition,))

    assert machine.evaluate(make_candles(), 0) is None


def test_state_machine_does_not_change_state_until_apply() -> None:
    transition = make_transition("activate")
    machine = make_machine(transitions=(transition,))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None
    assert machine.current_state == "WAITING"

    machine.apply(result)

    assert machine.current_state == "ACTIVE"


def test_state_machine_rejects_stale_transition_result() -> None:
    transition = make_transition("activate")
    machine = make_machine(transitions=(transition,))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None

    machine.apply(result)

    with pytest.raises(
        ValueError,
        match="does not match current state",
    ):
        machine.apply(result)


def test_state_machine_supports_injected_condition_evaluator() -> None:
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
    transition = make_transition("activate")

    machine = StrategyStateMachine(
        states=(
            make_state("WAITING", initial=True),
            make_state("ACTIVE"),
        ),
        transitions=(transition,),
        condition_evaluator=condition_evaluator,
    )

    result = machine.evaluate(make_candles(), 0)

    assert result is not None
    assert condition_evaluator.calls == 1


def test_state_machine_returns_none_after_reaching_terminal_state_without_outgoing_transition() -> None:
    activate = make_transition(
        "activate",
        from_state="WAITING",
        to_state="DONE",
    )

    machine = make_machine(transitions=(activate,))

    result = machine.evaluate(make_candles(), 0)

    assert result is not None

    machine.apply(result)

    assert machine.current_state == "DONE"
    assert machine.evaluate(make_candles(), 0) is None


def test_state_machine_rejects_undeclared_transition_source() -> None:
    with pytest.raises(
        ValueError,
        match="Transition source state must be declared",
    ):
        make_machine(
            transitions=(
                make_transition(
                    "bad",
                    from_state="UNKNOWN",
                    to_state="ACTIVE",
                ),
            ),
        )


def test_state_machine_rejects_undeclared_transition_target() -> None:
    with pytest.raises(
        ValueError,
        match="Transition target state must be declared",
    ):
        make_machine(
            transitions=(
                make_transition(
                    "bad",
                    from_state="WAITING",
                    to_state="UNKNOWN",
                ),
            ),
        )


def test_state_machine_rejects_multiple_initial_states() -> None:
    with pytest.raises(
        ValueError,
        match="At most one initial strategy state",
    ):
        make_machine(
            states=(
                make_state("WAITING", initial=True),
                make_state("ACTIVE", initial=True),
            ),
        )
