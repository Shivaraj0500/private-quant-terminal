from __future__ import annotations

from typing import ClassVar

from private_quant_terminal.strategy.states import StrategyExecutionState


class ExecutionStateManager:
    """Manage deterministic strategy-execution lifecycle transitions."""

    _TRANSITIONS: ClassVar[
        dict[
            StrategyExecutionState,
            frozenset[StrategyExecutionState],
        ]
    ] = {
        StrategyExecutionState.NOT_STARTED: frozenset(
            {StrategyExecutionState.RUNNING}
        ),
        StrategyExecutionState.RUNNING: frozenset(
            {
                StrategyExecutionState.PAUSED,
                StrategyExecutionState.STOPPED,
                StrategyExecutionState.COMPLETED,
            }
        ),
        StrategyExecutionState.PAUSED: frozenset(
            {
                StrategyExecutionState.RUNNING,
                StrategyExecutionState.STOPPED,
            }
        ),
        StrategyExecutionState.STOPPED: frozenset(),
        StrategyExecutionState.COMPLETED: frozenset(),
    }

    def __init__(
        self,
        initial_state: StrategyExecutionState = (
            StrategyExecutionState.NOT_STARTED
        ),
    ) -> None:
        self._state = initial_state
        self._history: list[StrategyExecutionState] = [initial_state]

    @property
    def state(self) -> StrategyExecutionState:
        """Return the current execution state."""

        return self._state

    @property
    def history(self) -> tuple[StrategyExecutionState, ...]:
        """Return the immutable execution-state transition history."""

        return tuple(self._history)

    def start(self) -> None:
        """Start an execution."""

        self._transition(StrategyExecutionState.RUNNING)

    def pause(self) -> None:
        """Pause a running execution."""

        self._transition(StrategyExecutionState.PAUSED)

    def resume(self) -> None:
        """Resume a paused execution."""

        if self._state is not StrategyExecutionState.PAUSED:
            raise ValueError(
                "Invalid execution-state transition: "
                f"{self._state.value} -> {StrategyExecutionState.RUNNING.value}."
            )

        self._transition(StrategyExecutionState.RUNNING)

    def stop(self) -> None:
        """Stop an execution."""

        self._transition(StrategyExecutionState.STOPPED)

    def complete(self) -> None:
        """Complete an execution."""

        self._transition(StrategyExecutionState.COMPLETED)

    def _transition(
        self,
        target: StrategyExecutionState,
    ) -> None:
        allowed = self._TRANSITIONS[self._state]

        if target not in allowed:
            raise ValueError(
                "Invalid execution-state transition: "
                f"{self._state.value} -> {target.value}."
            )

        self._state = target
        self._history.append(target)
