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
