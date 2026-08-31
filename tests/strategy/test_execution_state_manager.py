import pytest

from private_quant_terminal.strategy.execution_state import ExecutionStateManager
from private_quant_terminal.strategy.states import StrategyExecutionState


def test_starts_not_started() -> None:
    manager = ExecutionStateManager()

    assert manager.state is StrategyExecutionState.NOT_STARTED


def test_start_moves_to_running() -> None:
    manager = ExecutionStateManager()

    manager.start()

    assert manager.state is StrategyExecutionState.RUNNING


def test_running_can_be_paused() -> None:
    manager = ExecutionStateManager()
    manager.start()

    manager.pause()

    assert manager.state is StrategyExecutionState.PAUSED


def test_paused_can_resume() -> None:
    manager = ExecutionStateManager()
    manager.start()
    manager.pause()

    manager.resume()

    assert manager.state is StrategyExecutionState.RUNNING


def test_running_can_stop() -> None:
    manager = ExecutionStateManager()
    manager.start()

    manager.stop()

    assert manager.state is StrategyExecutionState.STOPPED


def test_running_can_complete() -> None:
    manager = ExecutionStateManager()
    manager.start()

    manager.complete()

    assert manager.state is StrategyExecutionState.COMPLETED


def test_paused_can_stop() -> None:
    manager = ExecutionStateManager()
    manager.start()
    manager.pause()

    manager.stop()

    assert manager.state is StrategyExecutionState.STOPPED


@pytest.mark.parametrize(
    "method",
    (
        "resume",
        "pause",
        "stop",
        "complete",
    ),
)
def test_invalid_transition_from_not_started_is_rejected(
    method: str,
) -> None:
    manager = ExecutionStateManager()

    with pytest.raises(
        ValueError,
        match="Invalid execution-state transition",
    ):
        getattr(manager, method)()

    assert manager.state is StrategyExecutionState.NOT_STARTED


def test_stopped_state_is_terminal() -> None:
    manager = ExecutionStateManager()
    manager.start()
    manager.stop()

    for method in ("start", "resume", "pause", "stop", "complete"):
        with pytest.raises(
            ValueError,
            match="Invalid execution-state transition",
        ):
            getattr(manager, method)()

    assert manager.state is StrategyExecutionState.STOPPED


def test_completed_state_is_terminal() -> None:
    manager = ExecutionStateManager()
    manager.start()
    manager.complete()

    for method in ("start", "resume", "pause", "stop", "complete"):
        with pytest.raises(
            ValueError,
            match="Invalid execution-state transition",
        ):
            getattr(manager, method)()

    assert manager.state is StrategyExecutionState.COMPLETED


def test_transition_history_is_recorded() -> None:
    manager = ExecutionStateManager()

    manager.start()
    manager.pause()
    manager.resume()
    manager.stop()

    assert manager.history == (
        StrategyExecutionState.NOT_STARTED,
        StrategyExecutionState.RUNNING,
        StrategyExecutionState.PAUSED,
        StrategyExecutionState.RUNNING,
        StrategyExecutionState.STOPPED,
    )


def test_history_is_immutable() -> None:
    manager = ExecutionStateManager()

    manager.start()

    history = manager.history

    assert isinstance(history, tuple)
    assert history == (
        StrategyExecutionState.NOT_STARTED,
        StrategyExecutionState.RUNNING,
    )
