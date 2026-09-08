from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from private_quant_terminal.strategy.canonical import strategy_hash
from private_quant_terminal.strategy.data_requirements import DataRequirement
from private_quant_terminal.strategy.positions import PositionGroup
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.states import StateTransition, StrategyState
from private_quant_terminal.strategy.ir import StrategyIR


@dataclass(frozen=True)
class CompiledStrategyPlan:
    strategy_id: str
    version: int
    strategy_hash: str

    rules: tuple[StrategyRule, ...]
    states: tuple[StrategyState, ...]
    transitions: Mapping[str, tuple[StateTransition, ...]]

    variables: tuple
    position_groups: tuple[PositionGroup, ...]
    data_requirements: tuple[DataRequirement, ...]

    session: object
    position_sizing: object
    stop_loss: object
    take_profit: object
    execution: object


class StrategyCompiler:
    """Compile validated StrategyIR into a deterministic immutable plan.

    The compiler is intentionally side-effect-free. It does not evaluate
    market conditions, mutate runtime state, perform risk checks, access
    market data, or submit orders.
    """

    def compile(self, strategy: StrategyIR) -> CompiledStrategyPlan:
        if not isinstance(strategy, StrategyIR):
            raise TypeError("StrategyCompiler.compile() requires a StrategyIR.")

        enabled_rules = tuple(
            sorted(
                (rule for rule in strategy.rules if rule.enabled),
                key=lambda rule: (-rule.priority, rule.rule_id),
            )
        )

        transitions_by_state: dict[str, tuple[StateTransition, ...]] = {}

        for state in strategy.states:
            enabled_transitions = tuple(
                sorted(
                    (
                        transition
                        for transition in strategy.transitions
                        if transition.enabled
                        and transition.from_state == state.state_id
                    ),
                    key=lambda transition: (
                        -transition.priority,
                        transition.transition_id,
                    ),
                )
            )
            transitions_by_state[state.state_id] = enabled_transitions

        return CompiledStrategyPlan(
            strategy_id=strategy.strategy_id,
            version=strategy.version,
            strategy_hash=strategy_hash(strategy),
            rules=enabled_rules,
            states=strategy.states,
            transitions=MappingProxyType(transitions_by_state),
            variables=strategy.variables,
            position_groups=strategy.position_groups,
            data_requirements=strategy.data_requirements,
            session=strategy.session,
            position_sizing=strategy.position_sizing,
            stop_loss=strategy.stop_loss,
            take_profit=strategy.take_profit,
            execution=strategy.execution,
        )
