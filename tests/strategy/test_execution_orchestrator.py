import pytest

from private_quant_terminal.models import Candle

from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
    StrategyAction,
)
from private_quant_terminal.strategy.execution_orchestrator import (
    ExecutionOrchestrator,
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
from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    PriceExpression,
    PriceField,
    add,
    constant,
    variable,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.conditions import (
    ComparisonOperator,
    compare,
)
from private_quant_terminal.strategy.state_machine import StrategyStateMachine
from private_quant_terminal.strategy.states import (
    StateTransition,
    StrategyExecutionState,
    StrategyState,
)


def transition_candle(close: float = 102.0) -> Candle:
    from datetime import UTC, datetime

    return Candle(
        timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        open=100.0,
        high=105.0,
        low=99.0,
        close=close,
        volume=1000.0,
    )


def make_state_transition(
    *,
    actions: tuple[StrategyAction, ...],
) -> StateTransition:
    return StateTransition(
        transition_id="activate",
        from_state="WAITING",
        to_state="ACTIVE",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=actions,
        priority=1,
    )


def make_state_machine(
    *,
    actions: tuple[StrategyAction, ...],
) -> StrategyStateMachine:
    return StrategyStateMachine(
        states=(
            StrategyState(
                state_id="WAITING",
                name="Waiting",
                initial=True,
            ),
            StrategyState(
                state_id="ACTIVE",
                name="Active",
            ),
        ),
        transitions=(
            make_state_transition(actions=actions),
        ),
    )


def test_state_transition_executes_actions_before_applying_state() -> None:
    group = option_group("transition-entry")
    machine = make_state_machine(
        actions=(EnterAction(position=group),),
    )
    orchestrator = ExecutionOrchestrator()

    orchestrator.start()

    result = orchestrator.process_state_transition(
        machine,
        transition_candle(),
    )

    assert result.transition is not None
    assert result.transition.from_state == "WAITING"
    assert result.transition.to_state == "ACTIVE"
    assert result.execution_result is not None
    assert len(result.execution_result.action_results) == 1
    assert machine.current_state == "ACTIVE"
    assert orchestrator.action_processor.get_position("transition-entry") == group



def test_rejected_state_transition_does_not_apply_state() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode

    group = option_group("rejected-transition")
    machine = make_state_machine(
        actions=(EnterAction(position=group),),
    )
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
        entry_start=time(9, 30),
        entry_end=time(14, 30),
    )

    candle = transition_candle()
    candle = Candle(
        timestamp=datetime(2026, 8, 30, 15, 0, tzinfo=UTC),
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
    )

    result = orchestrator.process_state_transition(
        machine,
        candle,
        session=session,
    )

    assert result.transition is not None
    assert result.execution_result.rejection_reasons
    assert result.execution_result.action_results == ()
    assert machine.current_state == "WAITING"
    assert orchestrator.action_processor.get_position(
        "rejected-transition"
    ) is None


def test_failed_state_transition_action_does_not_apply_state() -> None:
    machine = make_state_machine(
        actions=(ExitAction(group_id="missing-transition-group"),),
    )
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    with pytest.raises(
        KeyError,
        match="Unknown position group",
    ):
        orchestrator.process_state_transition(
            machine,
            transition_candle(),
        )

    assert machine.current_state == "WAITING"
    assert orchestrator.action_processor.get_position(
        "missing-transition-group"
    ) is None


def test_state_transition_preserves_action_order() -> None:
    first = option_group("transition-first")
    second = option_group("transition-second")

    machine = make_state_machine(
        actions=(
            EnterAction(position=first),
            EnterAction(position=second),
        ),
    )
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    result = orchestrator.process_state_transition(
        machine,
        transition_candle(),
    )

    assert result.execution_result.action_results
    assert tuple(
        item.action for item in result.execution_result.action_results
    ) == (
        EnterAction(position=first),
        EnterAction(position=second),
    )
    assert machine.current_state == "ACTIVE"



def test_evaluate_and_process_filters_rules_by_current_state() -> None:
    entry_group = option_group("state-rule-entry")
    managing_group = option_group("state-rule-managing")

    entry_rule = StrategyRule(
        rule_id="entry-rule",
        name="Entry rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=entry_group),),
        priority=20,
        states=("ENTRY",),
    )

    managing_rule = StrategyRule(
        rule_id="managing-rule",
        name="Managing rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=managing_group),),
        priority=10,
        states=("MANAGING",),
    )

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, managing_rule),
        (transition_candle(),),
        0,
        current_state="ENTRY",
    )

    assert tuple(
        rule.rule_id for rule in evaluation.triggered_rules
    ) == ("entry-rule",)
    assert len(result.action_results) == 1
    assert orchestrator.action_processor.get_position(
        "state-rule-entry"
    ) == entry_group
    assert orchestrator.action_processor.get_position(
        "state-rule-managing"
    ) is None



def test_state_scoped_rule_reads_and_persists_strategy_variable() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
    )

    variable_definition = StrategyVariable(
        name="adjustment_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    group = option_group("state-variable-interaction")

    rule = StrategyRule(
        rule_id="state-variable-rule",
        name="State Variable Rule",
        condition=compare(
            variable("adjustment_count"),
            ComparisonOperator.LESS_THAN,
            ConstantExpression(value=1.0),
        ),
        actions=(EnterAction(position=group),),
        priority=10,
        states=("ACTIVE",),
        variable_assignments=(
            VariableAssignment(
                name="adjustment_count",
                value=add(variable("adjustment_count"), constant(1)),
            ),
        ),
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable_definition,),
    )
    orchestrator.start()

    candles = (transition_candle(),)

    first_evaluation, first_result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
        current_state="ACTIVE",
    )

    assert tuple(
        triggered.rule_id
        for triggered in first_evaluation.triggered_rules
    ) == ("state-variable-rule",)
    assert len(first_result.action_results) == 1
    assert orchestrator.variable_store.resolve("adjustment_count") == 1

    second_evaluation, second_result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
        current_state="ACTIVE",
    )

    assert second_evaluation.triggered_rules == ()
    assert second_result.action_results == ()
    assert orchestrator.variable_store.resolve("adjustment_count") == 1


def test_state_and_variable_compose_across_adjustment_cycle() -> None:
    from private_quant_terminal.strategy.state_machine import StrategyStateMachine
    from private_quant_terminal.strategy.states import (
        StateTransition,
        StrategyState,
    )
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
    )

    adjustment_count = StrategyVariable(
        name="adjustment_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    observed_count = StrategyVariable(
        name="observed_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    adjustment_group = option_group("adjustment-cycle")

    adjustment_rule = StrategyRule(
        rule_id="active-adjustment",
        name="Active Adjustment",
        condition=compare(
            variable("adjustment_count"),
            ComparisonOperator.LESS_THAN,
            ConstantExpression(value=1.0),
        ),
        actions=(EnterAction(position=adjustment_group),),
        priority=10,
        states=("ACTIVE",),
        variable_assignments=(
            VariableAssignment(
                name="adjustment_count",
                value=add(variable("adjustment_count"), constant(1)),
            ),
        ),
    )

    post_adjustment_rule = StrategyRule(
        rule_id="post-adjustment",
        name="Post Adjustment",
        condition=compare(
            variable("adjustment_count"),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=0.0),
        ),
        actions=(),
        priority=10,
        states=("POST_ADJUSTMENT",),
        variable_assignments=(
            VariableAssignment(
                name="observed_count",
                value=variable("adjustment_count"),
            ),
        ),
    )

    machine = StrategyStateMachine(
        states=(
            StrategyState(
                state_id="ACTIVE",
                name="Active",
                initial=True,
            ),
            StrategyState(
                state_id="POST_ADJUSTMENT",
                name="Post Adjustment",
            ),
        ),
        transitions=(
            StateTransition(
                transition_id="adjust",
                from_state="ACTIVE",
                to_state="POST_ADJUSTMENT",
                condition=compare(
                    PriceExpression(field=PriceField.CLOSE),
                    ComparisonOperator.GREATER_THAN,
                    ConstantExpression(value=100.0),
                ),
                actions=(
                    ExitAction(group_id="adjustment-cycle"),
                ),
                priority=10,
            ),
        ),
    )

    orchestrator = ExecutionOrchestrator(
        variables=(adjustment_count, observed_count),
    )
    orchestrator.start()

    candles = (transition_candle(),)

    evaluation, result = orchestrator.evaluate_and_process(
        (adjustment_rule, post_adjustment_rule),
        candles,
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("active-adjustment",)
    assert len(result.action_results) == 1
    assert orchestrator.variable_store.resolve("adjustment_count") == 1

    transition_result = orchestrator.process_state_transition(
        machine,
        candles[0],
    )

    assert transition_result.transition is not None
    assert transition_result.transition.transition.transition_id == "adjust"
    assert transition_result.transition.from_state == "ACTIVE"
    assert transition_result.transition.to_state == "POST_ADJUSTMENT"
    assert transition_result.execution_result.action_results
    assert (
        transition_result.execution_result.action_results[0].action
        == ExitAction(group_id="adjustment-cycle")
    )
    assert machine.current_state == "POST_ADJUSTMENT"

    evaluation, result = orchestrator.evaluate_and_process(
        (adjustment_rule, post_adjustment_rule),
        candles,
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("post-adjustment",)
    assert result.action_results == ()
    assert evaluation.variable_mutations
    assert orchestrator.variable_store.resolve("adjustment_count") == 1
    assert orchestrator.variable_store.resolve("observed_count") == 1


def test_stateful_modify_keeps_position_and_enters_post_modify_state() -> None:
    from private_quant_terminal.strategy.actions import ModifyAction
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
    )

    modify_count = StrategyVariable(
        name="modify_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    primary = option_group("stateful-modify-primary")

    entry_rule = StrategyRule(
        rule_id="entry",
        name="Entry",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=primary),),
        priority=20,
        states=("ACTIVE",),
    )

    post_modify_rule = StrategyRule(
        rule_id="post-modify",
        name="Post Modify",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(),
        priority=10,
        states=("POST_MODIFY",),
        variable_assignments=(
            VariableAssignment(
                name="modify_count",
                value=add(variable("modify_count"), constant(1)),
            ),
        ),
    )

    machine = StrategyStateMachine(
        states=(
            StrategyState(
                state_id="ACTIVE",
                name="Active",
                initial=True,
            ),
            StrategyState(
                state_id="POST_MODIFY",
                name="Post Modify",
            ),
        ),
        transitions=(
            StateTransition(
                transition_id="modify",
                from_state="ACTIVE",
                to_state="POST_MODIFY",
                condition=compare(
                    PriceExpression(field=PriceField.CLOSE),
                    ComparisonOperator.GREATER_THAN,
                    ConstantExpression(value=100.0),
                ),
                actions=(
                    ModifyAction(
                        group_id=primary.group_id,
                        changes=(
                            ("stop_loss_percent", 25.0),
                            ("take_profit_percent", 50.0),
                        ),
                    ),
                ),
                priority=10,
            ),
        ),
    )

    orchestrator = ExecutionOrchestrator(
        variables=(modify_count,),
    )
    orchestrator.start()

    candle = transition_candle()

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_modify_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("entry",)
    assert result.action_results
    assert result.action_results[0].action == EnterAction(position=primary)
    assert orchestrator.variable_store.resolve("modify_count") == 0

    transition_result = orchestrator.process_state_transition(
        machine,
        candle,
    )

    assert transition_result.transition is not None
    assert transition_result.transition.transition.transition_id == "modify"
    assert transition_result.transition.transition.from_state == "ACTIVE"
    assert transition_result.transition.transition.to_state == "POST_MODIFY"
    assert transition_result.execution_result.action_results

    primary_snapshot = orchestrator.action_processor.get_state(primary.group_id)

    assert primary_snapshot is not None
    assert primary_snapshot.state.name == "OPEN"
    assert (
        orchestrator.action_processor.modifications(primary.group_id)
        == (
            ("stop_loss_percent", 25.0),
            ("take_profit_percent", 50.0),
        )
    )
    assert machine.current_state == "POST_MODIFY"

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_modify_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("post-modify",)
    assert result.action_results == ()
    assert evaluation.variable_mutations
    assert orchestrator.variable_store.resolve("modify_count") == 1


def test_stateful_hedge_keeps_parent_and_enters_post_hedge_state() -> None:
    from private_quant_terminal.strategy.actions import HedgeAction
    from private_quant_terminal.strategy.state_machine import StrategyStateMachine
    from private_quant_terminal.strategy.states import (
        StateTransition,
        StrategyState,
    )
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
    )

    hedge_count = StrategyVariable(
        name="hedge_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    primary = option_group("stateful-hedge-primary")
    hedge = option_group("stateful-hedge-position")

    entry_rule = StrategyRule(
        rule_id="entry",
        name="Entry",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=primary),),
        priority=20,
        states=("ACTIVE",),
    )

    post_hedge_rule = StrategyRule(
        rule_id="post-hedge",
        name="Post Hedge",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(),
        priority=10,
        states=("POST_HEDGE",),
        variable_assignments=(
            VariableAssignment(
                name="hedge_count",
                value=add(variable("hedge_count"), constant(1)),
            ),
        ),
    )

    machine = StrategyStateMachine(
        states=(
            StrategyState(
                state_id="ACTIVE",
                name="Active",
                initial=True,
            ),
            StrategyState(
                state_id="POST_HEDGE",
                name="Post Hedge",
            ),
        ),
        transitions=(
            StateTransition(
                transition_id="hedge",
                from_state="ACTIVE",
                to_state="POST_HEDGE",
                condition=compare(
                    PriceExpression(field=PriceField.CLOSE),
                    ComparisonOperator.GREATER_THAN,
                    ConstantExpression(value=100.0),
                ),
                actions=(
                    HedgeAction(
                        group_id=primary.group_id,
                        hedge=hedge,
                    ),
                ),
                priority=10,
            ),
        ),
    )

    orchestrator = ExecutionOrchestrator(
        variables=(hedge_count,),
    )
    orchestrator.start()

    candle = transition_candle()

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_hedge_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("entry",)
    assert result.action_results
    assert result.action_results[0].action == EnterAction(position=primary)
    assert orchestrator.variable_store.resolve("hedge_count") == 0

    transition_result = orchestrator.process_state_transition(
        machine,
        candle,
    )

    assert transition_result.transition is not None
    assert transition_result.transition.transition.transition_id == "hedge"
    assert transition_result.transition.transition.from_state == "ACTIVE"
    assert transition_result.transition.transition.to_state == "POST_HEDGE"
    assert transition_result.execution_result.action_results

    primary_snapshot = orchestrator.action_processor.get_state(primary.group_id)
    hedge_snapshot = orchestrator.action_processor.get_state(hedge.group_id)

    assert primary_snapshot is not None
    assert hedge_snapshot is not None
    assert primary_snapshot.state.name == "OPEN"
    assert hedge_snapshot.state.name == "OPEN"
    assert machine.current_state == "POST_HEDGE"

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_hedge_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("post-hedge",)
    assert result.action_results == ()
    assert evaluation.variable_mutations
    assert orchestrator.variable_store.resolve("hedge_count") == 1


def test_stateful_roll_moves_position_and_enters_post_roll_state() -> None:
    from private_quant_terminal.strategy.actions import RollAction
    from private_quant_terminal.strategy.state_machine import StrategyStateMachine
    from private_quant_terminal.strategy.states import (
        StateTransition,
        StrategyState,
    )
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
    )

    roll_count = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    original = option_group("stateful-roll-original")
    replacement = option_group("stateful-roll-replacement")

    entry_rule = StrategyRule(
        rule_id="entry",
        name="Entry",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=original),),
        priority=20,
        states=("ACTIVE",),
    )

    post_roll_rule = StrategyRule(
        rule_id="post-roll",
        name="Post Roll",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(),
        priority=10,
        states=("POST_ROLL",),
        variable_assignments=(
            VariableAssignment(
                name="roll_count",
                value=add(variable("roll_count"), constant(1)),
            ),
        ),
    )

    machine = StrategyStateMachine(
        states=(
            StrategyState(
                state_id="ACTIVE",
                name="Active",
                initial=True,
            ),
            StrategyState(
                state_id="POST_ROLL",
                name="Post Roll",
            ),
        ),
        transitions=(
            StateTransition(
                transition_id="roll",
                from_state="ACTIVE",
                to_state="POST_ROLL",
                condition=compare(
                    PriceExpression(field=PriceField.CLOSE),
                    ComparisonOperator.GREATER_THAN,
                    ConstantExpression(value=100.0),
                ),
                actions=(
                    RollAction(
                        group_id=original.group_id,
                        replacement=replacement,
                    ),
                ),
                priority=10,
            ),
        ),
    )

    orchestrator = ExecutionOrchestrator(
        variables=(roll_count,),
    )
    orchestrator.start()

    candle = transition_candle()

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_roll_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("entry",)
    assert len(result.action_results) == 1
    assert orchestrator.action_processor.get_position(
        original.group_id,
    ) == original

    transition_result = orchestrator.process_state_transition(
        machine,
        candle,
    )

    assert transition_result.transition is not None
    assert transition_result.transition.from_state == "ACTIVE"
    assert transition_result.transition.to_state == "POST_ROLL"
    assert (
        transition_result.transition.transition.transition_id
        == "roll"
    )
    assert machine.current_state == "POST_ROLL"

    assert orchestrator.action_processor.get_position(
        original.group_id,
    ) is None
    assert orchestrator.action_processor.get_position(
        replacement.group_id,
    ) == replacement

    evaluation, result = orchestrator.evaluate_and_process(
        (entry_rule, post_roll_rule),
        (candle,),
        0,
        current_state=machine.current_state,
    )

    assert tuple(
        triggered.rule_id
        for triggered in evaluation.triggered_rules
    ) == ("post-roll",)
    assert result.action_results == ()
    assert orchestrator.variable_store.resolve("roll_count") == 1

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


def test_starts_not_started() -> None:
    orchestrator = ExecutionOrchestrator()

    assert orchestrator.state is StrategyExecutionState.NOT_STARTED


def test_start_moves_to_running() -> None:
    orchestrator = ExecutionOrchestrator()

    orchestrator.start()

    assert orchestrator.state is StrategyExecutionState.RUNNING


def test_running_execution_processes_actions() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("entry")

    result = orchestrator.process(
        (EnterAction(position=group),)
    )

    assert result.state is StrategyExecutionState.RUNNING
    assert len(result.action_results) == 1
    assert orchestrator.action_processor.get_position("entry") == group


def test_multiple_actions_are_processed_in_order() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("entry")

    result = orchestrator.process(
        (
            EnterAction(position=group),
            ExitAction(group_id="entry"),
        )
    )

    assert tuple(
        item.action for item in result.action_results
    ) == (
        EnterAction(position=group),
        ExitAction(group_id="entry"),
    )

    snapshot = orchestrator.action_processor.get_state("entry")

    assert snapshot is not None
    assert snapshot.state.value == "CLOSED"


@pytest.mark.parametrize(
    "method",
    ("process",),
)
def test_processing_before_start_is_rejected(method: str) -> None:
    orchestrator = ExecutionOrchestrator()

    with pytest.raises(
        ValueError,
        match="must be RUNNING",
    ):
        getattr(orchestrator, method)(())


def test_processing_while_paused_is_rejected() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()
    orchestrator.pause()

    with pytest.raises(
        ValueError,
        match="must be RUNNING",
    ):
        orchestrator.process(())


def test_state_transition_processing_while_paused_is_rejected() -> None:
    machine = make_state_machine(
        actions=(EnterAction(position=option_group("paused-transition")),),
    )
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()
    orchestrator.pause()

    with pytest.raises(
        ValueError,
        match="must be RUNNING",
    ):
        orchestrator.process_state_transition(
            machine,
            transition_candle(),
        )

    assert machine.current_state == "WAITING"
    assert orchestrator.action_processor.get_position(
        "paused-transition",
    ) is None


def test_processing_after_stop_is_rejected() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()
    orchestrator.stop()

    with pytest.raises(
        ValueError,
        match="must be RUNNING",
    ):
        orchestrator.process(())


def test_processing_after_completion_is_rejected() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()
    orchestrator.complete()

    with pytest.raises(
        ValueError,
        match="must be RUNNING",
    ):
        orchestrator.process(())


def test_pause_and_resume_allow_processing_again() -> None:
    orchestrator = ExecutionOrchestrator()
    orchestrator.start()
    orchestrator.pause()
    orchestrator.resume()

    group = option_group("entry")

    result = orchestrator.process(
        (EnterAction(position=group),)
    )

    assert result.state is StrategyExecutionState.RUNNING
    assert orchestrator.action_processor.get_position("entry") == group


def test_stop_and_complete_delegate_to_state_manager() -> None:
    orchestrator = ExecutionOrchestrator()

    orchestrator.start()
    orchestrator.stop()

    assert orchestrator.state is StrategyExecutionState.STOPPED

    with pytest.raises(
        ValueError,
        match="Invalid execution-state transition",
    ):
        orchestrator.complete()


def test_processing_with_approved_policies_processes_actions() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import (
        SessionMode,
    )
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        PositionContext,
        SessionContext,
        StrategyRuntimeContext,
    )

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("policy-entry")
    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
        entry_start=time(9, 30),
        entry_end=time(14, 30),
        max_entries_per_session=2,
    )

    context = SessionContext(
        current_time=timestamp,
        entries_today=0,
    )

    runtime = StrategyRuntimeContext(
        market=MarketContext(
            timestamp=timestamp,
            open=100,
            high=105,
            low=95,
            close=102,
        ),
        position=PositionContext(),
        session=context,
    )

    result = orchestrator.process(
        (EnterAction(position=group),),
        session=session,
        context=context,
        runtime_context=runtime,
    )

    assert result.session_allowed is True
    assert result.risk_result is not None
    assert result.risk_result.approved is True
    assert result.rejection_reasons == ()
    assert len(result.action_results) == 1


def test_processing_rejected_by_session_does_not_process_actions() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode
    from private_quant_terminal.strategy.variables import SessionContext

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("blocked-entry")
    timestamp = datetime(2026, 8, 30, 8, 0, tzinfo=UTC)

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
    )

    context = SessionContext(current_time=timestamp)

    result = orchestrator.process(
        (EnterAction(position=group),),
        session=session,
        context=context,
    )

    assert result.session_allowed is False
    assert result.action_results == ()
    assert orchestrator.action_processor.get_position(
        "blocked-entry"
    ) is None


def test_processing_rejected_by_session_and_risk_does_not_process_actions() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        PositionContext,
        SessionContext,
        StrategyRuntimeContext,
    )

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("risk-entry")
    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=1,
    )

    context = SessionContext(
        current_time=timestamp,
        entries_today=2,
    )

    runtime = StrategyRuntimeContext(
        market=MarketContext(
            timestamp=timestamp,
            open=100,
            high=105,
            low=95,
            close=102,
        ),
        position=PositionContext(),
        session=context,
    )

    result = orchestrator.process(
        (EnterAction(position=group),),
        session=session,
        context=context,
        runtime_context=runtime,
    )

    assert result.session_allowed is False
    assert result.risk_result is not None
    assert result.risk_result.approved is False
    assert result.action_results == ()
    assert result.rejection_reasons == (
        "Strategy session policy rejected execution.",
        "Strategy entry count exceeds configured session maximum.",
    )
    assert orchestrator.action_processor.get_position(
        "risk-entry"
    ) is None

def test_exit_is_allowed_after_entry_window_closes() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode
    from private_quant_terminal.strategy.variables import SessionContext

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("exit-entry-window")

    orchestrator.process(
        (EnterAction(position=group),)
    )

    timestamp = datetime(
        2026,
        8,
        30,
        15,
        0,
        tzinfo=UTC,
    )

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
        entry_start=time(9, 30),
        entry_end=time(14, 30),
    )

    context = SessionContext(
        current_time=timestamp,
        last_entry_time=datetime(
            2026,
            8,
            30,
            10,
            0,
            tzinfo=UTC,
        ),
    )

    result = orchestrator.process(
        (ExitAction(group_id="exit-entry-window"),),
        session=session,
        context=context,
    )

    assert result.session_allowed is True
    assert result.action_results
    assert result.rejection_reasons == ()


def test_successful_entry_advances_runtime_state() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import SessionContext

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("runtime-entry")

    result = orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(
            current_time=timestamp,
        ),
    )

    assert len(result.action_results) == 1
    assert orchestrator.runtime_state.session.entries_today == 1
    assert orchestrator.runtime_state.session.trades_today == 1


def test_successful_exit_updates_runtime_state() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import SessionContext

    entry_time = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 8, 30, 15, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("runtime-exit")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(
            current_time=entry_time,
        ),
    )

    result = orchestrator.process(
        (ExitAction(group_id="runtime-exit"),),
        context=SessionContext(
            current_time=exit_time,
        ),
    )

    assert len(result.action_results) == 1
    assert orchestrator.runtime_state.session.last_exit_time == exit_time


def test_advance_bar_updates_runtime_state() -> None:
    from datetime import UTC, datetime

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    next_timestamp = datetime(2026, 8, 30, 10, 5, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    orchestrator.advance_bar(
        timestamp,
        minutes=5.0,
    )

    result = orchestrator.advance_bar(
        next_timestamp,
        minutes=5.0,
    )

    assert result.session.current_time == next_timestamp
    assert result.session.bars_since_entry == 2
    assert result.session.minutes_since_entry is None


def test_advance_bar_after_entry_tracks_elapsed_time() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import SessionContext

    entry_time = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    next_timestamp = datetime(2026, 8, 30, 10, 5, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("bar-entry")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(
            current_time=entry_time,
        ),
    )

    result = orchestrator.advance_bar(
        next_timestamp,
        minutes=5.0,
    )

    assert result.session.current_time == next_timestamp
    assert result.session.bars_since_entry == 1
    assert result.session.minutes_since_entry == 5.0


def test_advance_bar_requires_running_execution() -> None:
    from datetime import UTC, datetime

    orchestrator = ExecutionOrchestrator()

    with pytest.raises(
        ValueError,
        match="must be RUNNING to advance a bar",
    ):
        orchestrator.advance_bar(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            minutes=1.0,
        )


def test_advance_bar_rejects_negative_minutes() -> None:
    from datetime import UTC, datetime

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    with pytest.raises(
        ValueError,
        match="minutes cannot be negative",
    ):
        orchestrator.advance_bar(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            minutes=-1.0,
        )


def test_build_runtime_context_uses_orchestrator_session_state() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
        MarketContext,
        PositionContext,
        SessionContext,
    )

    entry_time = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    bar_time = datetime(2026, 8, 30, 10, 5, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("context-entry")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(
            current_time=entry_time,
        ),
    )

    orchestrator.advance_bar(
        bar_time,
        minutes=5.0,
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=bar_time,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
        position=PositionContext(
            quantity=1,
            entry_price=100.0,
            current_price=103.0,
        ),
    )

    assert context.market.close == 103.0
    assert context.position.quantity == 1
    assert context.session is not None
    assert context.session.current_time == bar_time
    assert context.session.entries_today == 1
    assert context.session.trades_today == 1
    assert context.session.bars_since_entry == 1
    assert context.session.minutes_since_entry == 5.0


def test_build_runtime_context_defaults_position_to_empty() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
    MarketContext,
)

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 0.0
    assert context.position.entry_price is None
    assert context.session.current_time == timestamp
    assert context.session.entries_today == orchestrator.runtime_state.session.entries_today
    assert context.session.trades_today == orchestrator.runtime_state.session.trades_today
    assert context.session.bars_since_entry == orchestrator.runtime_state.session.bars_since_entry
    assert context.session.minutes_since_entry == orchestrator.runtime_state.session.minutes_since_entry
    assert context.session.last_entry_time == orchestrator.runtime_state.session.last_entry_time
    assert context.session.last_exit_time == orchestrator.runtime_state.session.last_exit_time


def test_build_runtime_context_preserves_custom_variables() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
        MarketContext,
        StrategyVariable,
        VariableScope,
        VariableType,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
        variables=(
            StrategyVariable(
                name="risk_per_trade",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=1.0,
            ),
        ),
    )

    assert context.resolve("risk_per_trade") == 1.0


def test_evaluate_and_process_evaluates_rule_and_processes_actions() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import (
        ComparisonOperator,
        compare,
    )
    from private_quant_terminal.strategy.expressions import (
        ConstantExpression,
        PriceExpression,
        PriceField,
    )
    from private_quant_terminal.strategy.rules import StrategyRule
    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("evaluated-entry")

    rule = StrategyRule(
        rule_id="entry-rule",
        name="Entry Rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(
            EnterAction(position=group),
        ),
        priority=1,
    )

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
        session=StrategySession(
            mode=SessionMode.OVERNIGHT,
        ),
    )

    assert len(evaluation.triggered_rules) == 1
    assert evaluation.triggered_rules[0].rule_id == "entry-rule"
    assert len(evaluation.actions) == 1
    assert len(result.action_results) == 1
    assert orchestrator.runtime_state.session.entries_today == 1
    assert orchestrator.runtime_state.session.trades_today == 1


def test_evaluate_and_process_plan_executes_compiled_rules() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.compiler import StrategyCompiler
    from private_quant_terminal.strategy.conditions import (
        ComparisonOperator,
        compare,
    )
    from private_quant_terminal.strategy.expressions import (
        ConstantExpression,
        PriceExpression,
        PriceField,
    )
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.lifecycle import StrategyStatus

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    group = option_group("compiled-entry")

    rule = StrategyRule(
        rule_id="compiled-entry-rule",
        name="Compiled Entry Rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ComparisonOperator.GREATER_THAN,
            ConstantExpression(value=100.0),
        ),
        actions=(
            EnterAction(position=group),
        ),
        priority=1,
    )

    strategy = StrategyIR(
        strategy_id="compiled-runtime-test",
        name="Compiled Runtime Test",
        description="Compiler runtime integration test",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("NIFTY",),
        timeframe="5m",
        rules=(rule,),
        position_groups=(group,),
    )

    plan = StrategyCompiler().compile(strategy)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process_plan(
        plan,
        candles,
        0,
    )

    assert len(evaluation.triggered_rules) == 1
    assert evaluation.triggered_rules[0].rule_id == "compiled-entry-rule"
    assert len(evaluation.actions) == 1
    assert len(result.action_results) == 1


def test_evaluate_and_process_plan_passes_plan_variables_to_runtime() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.compiler import StrategyCompiler
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import ConstantExpression
    from private_quant_terminal.strategy.ir import StrategyIR
    from private_quant_terminal.strategy.lifecycle import StrategyStatus
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableScope,
        VariableType,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    variable_definition = StrategyVariable(
        name="risk_per_trade",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=1.0,
    )

    rule = StrategyRule(
        rule_id="variable-rule",
        name="Variable Rule",
        condition=compare(
            variable("risk_per_trade"),
            ">",
            ConstantExpression(value=0.5),
        ),
        actions=(
            EnterAction(position=option_group("compiled-variable-entry")),
        ),
    )

    strategy = StrategyIR(
        strategy_id="compiled-variable-test",
        name="Compiled Variable Test",
        description="Compiler variable propagation test",
        version=1,
        status=StrategyStatus.DRAFT,
        instruments=("NIFTY",),
        timeframe="5m",
        variables=(variable_definition,),
        rules=(rule,),
    )

    plan = StrategyCompiler().compile(strategy)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process_plan(
        plan,
        candles,
        0,
    )

    assert result.rejection_reasons == ()
    assert len(evaluation.triggered_rules) == 1
    assert evaluation.triggered_rules[0].rule_id == "variable-rule"
    assert len(result.action_results) == 1


def test_evaluate_and_process_plan_rejects_invalid_plan_type() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle

    orchestrator = ExecutionOrchestrator()

    candles = (
        Candle(
            timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    with pytest.raises(TypeError, match="CompiledStrategyPlan"):
        orchestrator.evaluate_and_process_plan(
            object(),
            candles,
            0,
        )

def test_evaluate_and_process_persists_variable_assignment_after_acceptance() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        ConstantExpression,
        PriceExpression,
        PriceField,
    )
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableScope,
        VariableType,
        VariableAssignment,
        VariableMutation,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    variable_definition = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable_definition,),
    )
    orchestrator.start()

    rule = StrategyRule(
        rule_id="assignment-rule",
        name="Assignment Rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ">",
            ConstantExpression(value=100.0),
        ),
        variable_assignments=(
            VariableAssignment(
                name="roll_count",
                value=add(variable("roll_count"), constant(1)),
            ),
        ),
    )

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
    )

    assert result.rejection_reasons == ()
    assert evaluation.variable_mutations == (
        VariableMutation(name="roll_count", value=1),
    )
    assert orchestrator.variable_store.resolve("roll_count") == 1


def test_evaluate_and_process_does_not_persist_variable_assignment_when_rejected() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        ConstantExpression,
        PriceExpression,
        PriceField,
    )
    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableAssignment,
        VariableScope,
        VariableType,
        SessionContext,
    )

    timestamp = datetime(2026, 8, 30, 8, 0, tzinfo=UTC)

    variable_definition = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable_definition,),
    )
    orchestrator.start()

    rule = StrategyRule(
        rule_id="rejected-assignment-rule",
        name="Rejected Assignment Rule",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ">",
            ConstantExpression(value=100.0),
        ),
        actions=(EnterAction(position=option_group("rejected-assignment")),),
        variable_assignments=(
            VariableAssignment(
                name="roll_count",
                value=add(variable("roll_count"), constant(1)),
            ),
        ),
    )

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
        session=StrategySession(
            mode=SessionMode.OVERNIGHT,
            market_start=time(9, 15),
            market_end=time(15, 30),
            entry_start=time(9, 30),
            entry_end=time(14, 30),
        ),
    )

    assert len(evaluation.variable_mutations) == 1
    assert result.rejection_reasons
    assert orchestrator.variable_store.resolve("roll_count") == 0


def test_evaluate_and_process_later_evaluation_reads_persisted_variable() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import (
        ConstantExpression,
        PriceExpression,
        PriceField,
    )
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableAssignment,
        VariableMutation,
        VariableScope,
        VariableType,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    variable_definition = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    observed_definition = StrategyVariable(
        name="observed_roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(
            variable_definition,
            observed_definition,
        ),
    )
    orchestrator.start()

    increment_rule = StrategyRule(
        rule_id="increment-roll-count",
        name="Increment Roll Count",
        condition=compare(
            PriceExpression(field=PriceField.CLOSE),
            ">",
            ConstantExpression(value=100.0),
        ),
        variable_assignments=(
            VariableAssignment(
                name="roll_count",
                value=add(variable("roll_count"), constant(1)),
            ),
        ),
    )

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    orchestrator.evaluate_and_process(
        (increment_rule,),
        candles,
        0,
    )

    assert orchestrator.variable_store.resolve("roll_count") == 1

    check_rule = StrategyRule(
        rule_id="check-roll-count",
        name="Check Roll Count",
        condition=compare(
            variable("roll_count"),
            ">",
            ConstantExpression(value=0.0),
        ),
        variable_assignments=(
            VariableAssignment(
                name="observed_roll_count",
                value=variable("roll_count"),
            ),
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (check_rule,),
        candles,
        0,
    )

    assert result.rejection_reasons == ()
    assert evaluation.variable_mutations == (
        VariableMutation(name="observed_roll_count", value=1),
    )
    assert orchestrator.variable_store.resolve("observed_roll_count") == 1


def test_evaluate_and_process_uses_current_runtime_session() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.variables import SessionContext

    entry_time = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    bar_time = datetime(2026, 8, 30, 10, 5, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("runtime-context-entry")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(
            current_time=entry_time,
        ),
    )

    orchestrator.advance_bar(
        bar_time,
        minutes=5.0,
    )

    candles = (
        Candle(
            timestamp=bar_time,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (),
        candles,
        0,
    )

    assert evaluation.triggered_rules == ()
    assert evaluation.actions == ()
    assert result.action_results == ()
    assert orchestrator.runtime_state.session.entries_today == 1
    assert orchestrator.runtime_state.session.trades_today == 1
    assert orchestrator.runtime_state.session.bars_since_entry == 1
    assert orchestrator.runtime_state.session.minutes_since_entry == 5.0


def test_evaluate_and_process_with_no_rules_does_not_mutate_state() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    before = orchestrator.runtime_state

    candles = (
        Candle(
            timestamp=timestamp,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (),
        candles,
        0,
    )

    assert evaluation.triggered_rules == ()
    assert evaluation.actions == ()
    assert result.action_results == ()
    assert orchestrator.runtime_state.session == before.session


def test_build_runtime_context_derives_open_position_from_action_processor() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
    MarketContext,
    SessionContext,
)

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("derived-position")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(current_time=timestamp),
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 1.0
    assert context.position.entry_timestamp == timestamp
    assert context.is_position_open is True


def test_build_runtime_context_is_flat_after_position_exit() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
    MarketContext,
    SessionContext,
)

    entry_time = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 8, 30, 10, 30, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    group = option_group("derived-exit")

    orchestrator.process(
        (EnterAction(position=group),),
        context=SessionContext(current_time=entry_time),
    )

    orchestrator.process(
        (ExitAction(group_id="derived-exit"),),
        context=SessionContext(current_time=exit_time),
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=exit_time,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 0.0
    assert context.position.entry_timestamp is None
    assert context.is_position_open is False


def test_build_runtime_context_counts_multiple_open_position_groups() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
    MarketContext,
    SessionContext,
)

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    first = option_group("position-one")
    second = option_group("position-two")

    orchestrator.process(
        (
            EnterAction(position=first),
            EnterAction(position=second),
        ),
        context=SessionContext(current_time=timestamp),
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 2.0
    assert context.position.entry_timestamp == timestamp
    assert context.is_position_open is True


def test_build_runtime_context_derives_position_after_roll() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.actions import RollAction
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        SessionContext,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    original = option_group("roll-original")
    replacement = option_group("roll-replacement")

    orchestrator.process(
        (EnterAction(position=original),),
        context=SessionContext(current_time=timestamp),
    )

    orchestrator.process(
        (
            RollAction(
                group_id="roll-original",
                replacement=replacement,
            ),
        ),
        context=SessionContext(current_time=timestamp),
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 1.0
    assert context.position.entry_timestamp == timestamp
    assert context.is_position_open is True


def test_build_runtime_context_counts_hedge_as_open_position_group() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.actions import HedgeAction
    from private_quant_terminal.strategy.variables import (
        MarketContext,
        SessionContext,
    )

    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    orchestrator = ExecutionOrchestrator()
    orchestrator.start()

    primary = option_group("hedge-primary")
    hedge = option_group("hedge-position")

    orchestrator.process(
        (EnterAction(position=primary),),
        context=SessionContext(current_time=timestamp),
    )

    orchestrator.process(
        (
            HedgeAction(
                group_id="hedge-primary",
                hedge=hedge,
            ),
        ),
        context=SessionContext(current_time=timestamp),
    )

    context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert context.position.quantity == 2.0
    assert context.position.entry_timestamp == timestamp
    assert context.is_position_open is True


def test_orchestrator_persists_variable_values_across_runtime_contexts() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.strategy.variables import (
        MarketContext,
        StrategyVariable,
        VariableScope,
        VariableType,
    )

    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable,),
    )

    first_context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
        ),
    )

    assert first_context.resolve("roll_count") == 0

    orchestrator.variable_store.set("roll_count", 1)

    second_context = orchestrator.build_runtime_context(
        market=MarketContext(
            timestamp=datetime(2026, 8, 30, 10, 5, tzinfo=UTC),
            open=103.0,
            high=106.0,
            low=102.0,
            close=105.0,
        ),
    )

    assert second_context.resolve("roll_count") == 1


def test_orchestrator_applies_variable_mutations_to_store() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableMutation,
        VariableScope,
        VariableType,
    )

    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable,),
    )

    mutation = VariableMutation(
        name="roll_count",
        value=1,
    )

    assert orchestrator.variable_store.resolve("roll_count") == 0

    orchestrator._apply_variable_mutations((mutation,))

    assert orchestrator.variable_store.resolve("roll_count") == 1


def test_orchestrator_applies_multiple_variable_mutations_in_evaluation_order() -> None:
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableMutation,
        VariableScope,
        VariableType,
    )

    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable,),
    )

    high_priority_mutation = VariableMutation(
        name="roll_count",
        value=10,
    )
    low_priority_mutation = VariableMutation(
        name="roll_count",
        value=20,
    )

    mutations = (
        high_priority_mutation,
        low_priority_mutation,
    )

    orchestrator._apply_variable_mutations(mutations)

    assert orchestrator.variable_store.resolve("roll_count") == 20


def test_evaluate_and_process_applies_variable_mutation_after_approval() -> None:
    from datetime import UTC, datetime

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import constant, price
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableMutation,
        VariableScope,
        VariableType,
    )

    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable,),
    )
    orchestrator.start()

    rule = StrategyRule(
        rule_id="mutation-rule",
        name="Mutation Rule",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        variable_mutations=(
            VariableMutation(
                name="roll_count",
                value=1,
            ),
        ),
    )

    candles = (
        Candle(
            timestamp=datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
    )

    assert evaluation.variable_mutations == (
        VariableMutation(name="roll_count", value=1),
    )
    assert result.rejection_reasons == ()
    assert orchestrator.variable_store.resolve("roll_count") == 1


def test_evaluate_and_process_does_not_apply_mutation_when_execution_is_rejected() -> None:
    from datetime import UTC, datetime, time

    from private_quant_terminal.models import Candle
    from private_quant_terminal.strategy.conditions import compare
    from private_quant_terminal.strategy.expressions import constant, price
    from private_quant_terminal.strategy.session import StrategySession
    from private_quant_terminal.strategy.states import SessionMode
    from private_quant_terminal.strategy.variables import (
        StrategyVariable,
        VariableMutation,
        VariableScope,
        VariableType,
    )

    variable = StrategyVariable(
        name="roll_count",
        variable_type=VariableType.NUMBER,
        scope=VariableScope.STRATEGY,
        value=0,
    )

    orchestrator = ExecutionOrchestrator(
        variables=(variable,),
    )
    orchestrator.start()

    rule = StrategyRule(
        rule_id="mutation-rule",
        name="Mutation Rule",
        condition=compare(
            price("close"),
            ">",
            constant(100),
        ),
        actions=(EnterAction(position=option_group("mutation-entry")),),
        variable_mutations=(
            VariableMutation(
                name="roll_count",
                value=1,
            ),
        ),
    )

    candles = (
        Candle(
            timestamp=datetime(2026, 8, 30, 8, 0, tzinfo=UTC),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000.0,
        ),
    )

    evaluation, result = orchestrator.evaluate_and_process(
        (rule,),
        candles,
        0,
        session=StrategySession(
            mode=SessionMode.OVERNIGHT,
            market_start=time(9, 15),
            market_end=time(15, 30),
        ),
    )

    assert evaluation.variable_mutations == (
        VariableMutation(name="roll_count", value=1),
    )
    assert result.rejection_reasons
    assert orchestrator.variable_store.resolve("roll_count") == 0
