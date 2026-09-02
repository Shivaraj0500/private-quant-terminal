from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.action_processor import (
    ActionProcessingResult,
    ActionProcessor,
)
from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
    RollAction,
    StrategyAction,
)
from private_quant_terminal.strategy.execution_state import ExecutionStateManager
from private_quant_terminal.strategy.risk import (
    StrategyRiskEvaluator,
    StrategyRiskResult,
)
from private_quant_terminal.strategy.rule_evaluator import (
    RuleEvaluationResult,
    StrategyRuleEvaluator,
)
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.runtime_state import (
    StrategyRuntimeState,
)
from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.session_policy import (
    SessionPolicyEvaluator,
)
from private_quant_terminal.strategy.states import StrategyExecutionState
from private_quant_terminal.strategy.variables import (
    MarketContext,
    PositionContext,
    SessionContext,
    StrategyRuntimeContext,
    StrategyVariable,
    StrategyVariableStore,
    VariableMutation,
)


@dataclass(frozen=True)
class ExecutionOrchestrationResult:
    """Deterministic result of one orchestration step."""

    action_results: tuple[ActionProcessingResult, ...]
    state: StrategyExecutionState
    session_allowed: bool = True
    risk_result: StrategyRiskResult | None = None
    rejection_reasons: tuple[str, ...] = ()


class ExecutionOrchestrator:
    """Coordinate lifecycle, session policy, risk, and action processing."""

    def __init__(
        self,
        *,
        state_manager: ExecutionStateManager | None = None,
        action_processor: ActionProcessor | None = None,
        session_policy: SessionPolicyEvaluator | None = None,
        risk_evaluator: StrategyRiskEvaluator | None = None,
        variables: tuple[StrategyVariable, ...] = (),
    ) -> None:
        self.state_manager = state_manager or ExecutionStateManager()
        self.action_processor = action_processor or ActionProcessor()
        self.session_policy = (
            session_policy or SessionPolicyEvaluator()
        )
        self.risk_evaluator = (
            risk_evaluator or StrategyRiskEvaluator()
        )
        self.runtime_state = StrategyRuntimeState(
            session=SessionContext(
                current_time=datetime.now(UTC),
            )
        )
        self.variable_store = StrategyVariableStore(variables)

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

    def advance_bar(
        self,
        timestamp: datetime,
        *,
        minutes: float,
    ) -> StrategyRuntimeState:
        """Advance runtime state for a new market bar."""

        if self.state is not StrategyExecutionState.RUNNING:
            raise ValueError(
                "Strategy execution must be RUNNING to advance a bar."
            )

        self.runtime_state = self.runtime_state.advance_bar(
            timestamp,
            minutes=minutes,
        )

        return self.runtime_state

    def _apply_variable_mutations(
        self,
        mutations: tuple[VariableMutation, ...],
    ) -> None:
        """Apply evaluated variable mutations in deterministic order."""

        for mutation in mutations:
            self.variable_store.apply(mutation)

    def _open_position_group_count(self) -> int:
        """Return the number of currently open position groups."""

        return sum(
            snapshot.state.value in {"OPEN", "PARTIALLY_CLOSED"}
            for snapshot in self.action_processor.snapshots()
        )

    def _position_context(self) -> PositionContext:
        """Build runtime position state from processed position groups.

        Quantity represents the number of active position groups. It is not
        broker fill quantity because fills and executable quantities are not
        part of the current position-state model.
        """

        group_count = self._open_position_group_count()

        if group_count == 0:
            return PositionContext()

        return PositionContext(
            quantity=float(group_count),
            entry_timestamp=self.runtime_state.session.last_entry_time,
        )

    def build_runtime_context(
        self,
        *,
        market: MarketContext,
        position: PositionContext | None = None,
        variables: tuple[StrategyVariable, ...] = (),
    ) -> StrategyRuntimeContext:
        """Build an evaluation context from current runtime state."""

        return StrategyRuntimeContext(
            market=market,
            position=(
                position
                if position is not None
                else self._position_context()
            ),
            session=self.runtime_state.session,
            variables=variables,
            variable_store=self.variable_store,
        )

    @staticmethod
    def _requires_entry_policy(
        actions: tuple[StrategyAction, ...],
    ) -> bool:
        """Return whether the action batch requires entry policy checks."""

        return any(
            isinstance(action, (EnterAction, RollAction))
            for action in actions
        )

    def evaluate_and_process(
        self,
        rules: Sequence[StrategyRule],
        candles: Sequence[Candle],
        index: int,
        *,
        position: PositionContext | None = None,
        variables: tuple[StrategyVariable, ...] = (),
        session: StrategySession | None = None,
    ) -> tuple[RuleEvaluationResult, ExecutionOrchestrationResult]:
        """Evaluate strategy rules and process their resulting actions."""

        runtime_context = self.build_runtime_context(
            market=MarketContext(
                timestamp=candles[index].timestamp,
                open=candles[index].open,
                high=candles[index].high,
                low=candles[index].low,
                close=candles[index].close,
                volume=candles[index].volume,
            ),
            position=position,
            variables=variables,
        )

        evaluation = StrategyRuleEvaluator().evaluate(
            rules,
            candles,
            index,
            runtime_context,
        )

        result = self.process(
            evaluation.actions,
            session=session,
            context=runtime_context.session,
            runtime_context=runtime_context,
        )

        if not result.rejection_reasons:
            self._apply_variable_mutations(
                evaluation.variable_mutations,
            )

        return evaluation, result

    def process(
        self,
        actions: tuple[StrategyAction, ...],
        *,
        session: StrategySession | None = None,
        context: SessionContext | None = None,
        runtime_context: StrategyRuntimeContext | None = None,
    ) -> ExecutionOrchestrationResult:
        """Process actions after optional policy validation."""

        if self.state is not StrategyExecutionState.RUNNING:
            raise ValueError(
                "Strategy execution must be RUNNING to process actions."
            )

        session_allowed = True
        rejection_reasons: list[str] = []
        risk_result: StrategyRiskResult | None = None

        if (
            session is not None
            and context is not None
            and self._requires_entry_policy(actions)
        ):
            session_allowed = self.session_policy.entry_allowed(
                session,
                context,
            )

            if not session_allowed:
                rejection_reasons.append(
                    "Strategy session policy rejected execution."
                )

        if session is not None and runtime_context is not None:
            risk_result = self.risk_evaluator.evaluate(
                session,
                runtime_context,
            )

            if not risk_result.approved:
                rejection_reasons.extend(risk_result.reasons)

        if not session_allowed or (
            risk_result is not None
            and not risk_result.approved
        ):
            return ExecutionOrchestrationResult(
                action_results=(),
                state=self.state,
                session_allowed=session_allowed,
                risk_result=risk_result,
                rejection_reasons=tuple(rejection_reasons),
            )

        results = self.action_processor.process_all(actions)

        timestamp = (
            context.current_time
            if context is not None
            else (
                runtime_context.market.timestamp
                if runtime_context is not None
                else datetime.now(UTC)
            )
        )

        for action in actions:
            if isinstance(action, EnterAction):
                self.position_context = PositionContext(
                    quantity=1.0,
                    entry_timestamp=timestamp,
                )
            elif isinstance(action, ExitAction):
                self.position_context = PositionContext()
            elif isinstance(action, RollAction):
                self.position_context = PositionContext(
                    quantity=1.0,
                    entry_timestamp=timestamp,
                )

        runtime_state = self.runtime_state

        for action in actions:
            runtime_state = runtime_state.apply(
                action,
                timestamp,
            )

        self.runtime_state = runtime_state

        return ExecutionOrchestrationResult(
            action_results=results,
            state=self.state,
            session_allowed=session_allowed,
            risk_result=risk_result,
            rejection_reasons=tuple(rejection_reasons),
        )
