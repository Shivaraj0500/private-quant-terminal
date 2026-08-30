from private_quant_terminal.strategy.states import (
    PositionState,
    ReentryPolicy,
    SessionMode,
    StrategyExecutionState,
)


def test_execution_states_exist() -> None:
    assert StrategyExecutionState.NOT_STARTED.value == "NOT_STARTED"
    assert StrategyExecutionState.RUNNING.value == "RUNNING"
    assert StrategyExecutionState.PAUSED.value == "PAUSED"
    assert StrategyExecutionState.STOPPED.value == "STOPPED"
    assert StrategyExecutionState.COMPLETED.value == "COMPLETED"


def test_position_states_exist() -> None:
    assert PositionState.FLAT.value == "FLAT"
    assert PositionState.OPEN.value == "OPEN"
    assert PositionState.PARTIALLY_CLOSED.value == "PARTIALLY_CLOSED"
    assert PositionState.CLOSED.value == "CLOSED"


def test_session_modes_exist() -> None:
    assert SessionMode.INTRADAY.value == "INTRADAY"
    assert SessionMode.OVERNIGHT.value == "OVERNIGHT"


def test_reentry_policies_exist() -> None:
    assert ReentryPolicy.ALLOW.value == "ALLOW"
    assert ReentryPolicy.BLOCK.value == "BLOCK"
    assert ReentryPolicy.AFTER_COOLDOWN.value == "AFTER_COOLDOWN"
