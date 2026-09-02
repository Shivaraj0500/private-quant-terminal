
import pytest

from private_quant_terminal.strategy.actions import EnterAction
from private_quant_terminal.strategy.conditions import compare
from private_quant_terminal.strategy.enums import StrategyStatus, StrategyTimeframe
from private_quant_terminal.strategy.expressions import constant, price
from private_quant_terminal.strategy.ir import StrategyIR
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.states import StateTransition, StrategyState


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


def make_condition():
    return compare(price("close"), ">", constant(100))


def make_transition(
    transition_id: str = "entry",
    *,
    from_state: str = "WAITING",
    to_state: str = "ACTIVE",
) -> StateTransition:
    return StateTransition(
        transition_id=transition_id,
        from_state=from_state,
        to_state=to_state,
        condition=make_condition(),
        actions=(make_action(),),
    )


def make_ir(
    *,
    states=(),
    transitions=(),
    rules=(),
) -> StrategyIR:
    return StrategyIR(
        strategy_id="state-test",
        name="State Test",
        description="Strategy state test",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("NIFTY",),
        timeframe=StrategyTimeframe.FIVE_MINUTES,
        states=states,
        transitions=transitions,
        rules=rules,
    )


def test_strategy_state_normalizes_identity_fields() -> None:
    state = StrategyState(
        state_id=" active ",
        name=" Active Position ",
        initial=True,
        terminal=False,
    )

    assert state.state_id == "active"
    assert state.name == "Active Position"
    assert state.initial is True
    assert state.terminal is False


@pytest.mark.parametrize(
    "kwargs",
    (
        {"state_id": "", "name": "Active"},
        {"state_id": "ACTIVE", "name": ""},
    ),
)
def test_strategy_state_rejects_empty_identity(kwargs) -> None:
    with pytest.raises(ValueError):
        StrategyState(**kwargs)


def test_state_transition_normalizes_state_references() -> None:
    transition = StateTransition(
        transition_id=" entry ",
        from_state=" WAITING ",
        to_state=" ACTIVE ",
        condition=make_condition(),
        actions=(make_action(),),
    )

    assert transition.transition_id == "entry"
    assert transition.from_state == "WAITING"
    assert transition.to_state == "ACTIVE"


def test_state_transition_requires_action() -> None:
    with pytest.raises(ValueError, match="at least one action"):
        StateTransition(
            transition_id="entry",
            from_state="WAITING",
            to_state="ACTIVE",
            condition=make_condition(),
            actions=(),
        )


def test_strategy_ir_accepts_valid_state_machine() -> None:
    states = (
        StrategyState("WAITING", "Waiting", initial=True),
        StrategyState("ACTIVE", "Active"),
        StrategyState("DONE", "Done", terminal=True),
    )

    transition = make_transition()

    strategy = make_ir(
        states=states,
        transitions=(transition,),
    )

    assert strategy.states == states
    assert strategy.transitions == (transition,)


def test_strategy_ir_rejects_duplicate_state_ids() -> None:
    states = (
        StrategyState("WAITING", "Waiting", initial=True),
        StrategyState("WAITING", "Duplicate"),
    )

    with pytest.raises(ValueError, match="state IDs must be unique"):
        make_ir(states=states)


def test_strategy_ir_rejects_multiple_initial_states() -> None:
    states = (
        StrategyState("WAITING", "Waiting", initial=True),
        StrategyState("ACTIVE", "Active", initial=True),
    )

    with pytest.raises(ValueError, match="at most one initial state"):
        make_ir(states=states)


def test_strategy_ir_rejects_duplicate_transition_ids() -> None:
    states = (
        StrategyState("WAITING", "Waiting", initial=True),
        StrategyState("ACTIVE", "Active"),
    )

    transitions = (
        make_transition("entry"),
        make_transition("entry"),
    )

    with pytest.raises(ValueError, match="transition IDs must be unique"):
        make_ir(states=states, transitions=transitions)


def test_strategy_ir_rejects_undeclared_transition_source() -> None:
    states = (StrategyState("ACTIVE", "Active", initial=True),)

    with pytest.raises(ValueError, match="source state must be declared"):
        make_ir(
            states=states,
            transitions=(
                make_transition(
                    from_state="WAITING",
                    to_state="ACTIVE",
                ),
            ),
        )


def test_strategy_ir_rejects_undeclared_transition_target() -> None:
    states = (StrategyState("WAITING", "Waiting", initial=True),)

    with pytest.raises(ValueError, match="target state must be declared"):
        make_ir(
            states=states,
            transitions=(
                make_transition(
                    from_state="WAITING",
                    to_state="ACTIVE",
                ),
            ),
        )


def test_strategy_ir_rejects_undeclared_rule_state() -> None:
    states = (
        StrategyState("WAITING", "Waiting", initial=True),
        StrategyState("ACTIVE", "Active"),
    )

    rule = StrategyRule(
        rule_id="post-roll",
        name="Post Roll",
        condition=make_condition(),
        actions=(make_action(),),
        states=("POST_ROLL",),
    )

    with pytest.raises(ValueError, match="rule state must be declared"):
        make_ir(states=states, rules=(rule,))
