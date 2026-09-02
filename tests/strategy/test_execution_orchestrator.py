import pytest

from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
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
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.states import StrategyExecutionState


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
    assert context.session == orchestrator.runtime_state.session


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
