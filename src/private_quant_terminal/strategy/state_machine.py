from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.evaluator import ConditionEvaluator
from private_quant_terminal.strategy.states import StateTransition, StrategyState
from private_quant_terminal.strategy.variables import StrategyRuntimeContext


@dataclass(frozen=True)
class StateTransitionResult:
    """Result of evaluating semantic strategy-state transitions."""

    transition: StateTransition
    from_state: str
    to_state: str


class StrategyStateMachine:
    """Evaluate deterministic transitions between semantic strategy states."""

    def __init__(
        self,
        states: Sequence[StrategyState],
        transitions: Sequence[StateTransition],
        condition_evaluator: ConditionEvaluator | None = None,
    ) -> None:
        self._states = tuple(states)
        self._transitions = tuple(transitions)
        self._conditions = condition_evaluator or ConditionEvaluator()

        state_ids = {state.state_id for state in self._states}

        if len(state_ids) != len(self._states):
            raise ValueError("Strategy state IDs must be unique.")

        for transition in self._transitions:
            if transition.from_state not in state_ids:
                raise ValueError(
                    f"Transition source state must be declared: "
                    f"{transition.from_state}."
                )
            if transition.to_state not in state_ids:
                raise ValueError(
                    f"Transition target state must be declared: "
                    f"{transition.to_state}."
                )

        initial_states = tuple(
            state for state in self._states if state.initial
        )

        if len(initial_states) > 1:
            raise ValueError("At most one initial strategy state is allowed.")

        self._current_state = (
            initial_states[0].state_id
            if initial_states
            else None
        )

    @property
    def current_state(self) -> str | None:
        """Return the current semantic strategy state."""

        return self._current_state

    @property
    def states(self) -> tuple[StrategyState, ...]:
        """Return the declared semantic strategy states."""

        return self._states

    @property
    def transitions(self) -> tuple[StateTransition, ...]:
        """Return the declared semantic state transitions."""

        return self._transitions

    def evaluate(
        self,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None = None,
    ) -> StateTransitionResult | None:
        """Evaluate applicable transitions from the current state."""

        if self._current_state is None:
            return None

        ordered = sorted(
            (
                transition
                for transition in self._transitions
                if transition.enabled
                and transition.from_state == self._current_state
            ),
            key=lambda transition: (
                -transition.priority,
                transition.transition_id,
            ),
        )

        for transition in ordered:
            if self._conditions.evaluate(
                transition.condition,
                candles,
                index,
                context,
            ):
                return StateTransitionResult(
                    transition=transition,
                    from_state=transition.from_state,
                    to_state=transition.to_state,
                )

        return None

    def apply(self, result: StateTransitionResult) -> None:
        """Apply a previously evaluated semantic state transition."""

        if result.from_state != self._current_state:
            raise ValueError(
                "State transition result does not match current state."
            )

        self._current_state = result.to_state
