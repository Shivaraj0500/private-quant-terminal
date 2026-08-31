from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.action_processor import (
    ActionProcessingResult,
    ActionProcessor,
)
from private_quant_terminal.strategy.actions import StrategyAction
from private_quant_terminal.strategy.execution_state import ExecutionStateManager
from private_quant_terminal.strategy.states import StrategyExecutionState


@dataclass(frozen=True)
class ExecutionOrchestrationResult:
    """Deterministic result of one orchestration step."""

    action_results: tuple[ActionProcessingResult, ...]
    state: StrategyExecutionState


class ExecutionOrchestrator:
    """Coordinate execution lifecycle and deterministic action processing."""

    def __init__(
        self,
        *,
        state_manager: ExecutionStateManager | None = None,
        action_processor: ActionProcessor | None = None,
    ) -> None:
        self.state_manager = state_manager or ExecutionStateManager()
        self.action_processor = action_processor or ActionProcessor()

    @property
    def state(self) -> StrategyExecutionState:
        """Return the current execution lifecycle state."""

        return self.state_manager.state

    def start(self) -> None:
        """Start the strategy execution."""

        self.state_manager.start()

    def pause(self) -> None:
        """Pause the strategy execution."""

        self.state_manager.pause()

    def resume(self) -> None:
        """Resume the strategy execution."""

        self.state_manager.resume()

    def stop(self) -> None:
        """Stop the strategy execution."""

        self.state_manager.stop()

    def complete(self) -> None:
        """Complete the strategy execution."""

        self.state_manager.complete()

    def process(
        self,
        actions: tuple[StrategyAction, ...],
    ) -> ExecutionOrchestrationResult:
        """Process a deterministic batch of strategy actions."""

        if self.state is not StrategyExecutionState.RUNNING:
            raise ValueError(
                "Strategy execution must be RUNNING to process actions."
            )

        results = self.action_processor.process_all(actions)

        return ExecutionOrchestrationResult(
            action_results=results,
            state=self.state,
        )
