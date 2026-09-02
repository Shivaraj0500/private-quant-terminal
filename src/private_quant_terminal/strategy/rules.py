from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.actions import StrategyAction
from private_quant_terminal.strategy.conditions import Condition
from private_quant_terminal.strategy.variables import (
    VariableAssignment,
    VariableMutation,
)


@dataclass(frozen=True)
class StrategyRule:
    """A deterministic WHEN/THEN strategy rule."""

    rule_id: str
    name: str
    condition: Condition
    actions: tuple[StrategyAction, ...] = ()
    variable_mutations: tuple[VariableMutation, ...] = ()
    variable_assignments: tuple[VariableAssignment, ...] = ()
    priority: int = 0
    enabled: bool = True
    states: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("Rule ID must not be empty.")

        if not self.name.strip():
            raise ValueError("Rule name must not be empty.")

        if (
            not self.actions
            and not self.variable_mutations
            and not self.variable_assignments
        ):
            raise ValueError(
                "Strategy rule must contain at least one action, variable mutation, or variable assignment."
            )

        mutation_names = tuple(
            mutation.name.lower()
            for mutation in self.variable_mutations
        )

        if len(set(mutation_names)) != len(mutation_names):
            raise ValueError(
                "Strategy rule variable mutations must target unique variables."
            )

        assignment_names = tuple(
            assignment.name.lower()
            for assignment in self.variable_assignments
        )

        if len(set(assignment_names)) != len(assignment_names):
            raise ValueError(
                "Strategy rule variable assignments must target unique variables."
            )

        if self.priority < 0:
            raise ValueError("Rule priority cannot be negative.")

        normalized_states = tuple(
            state.strip()
            for state in self.states
        )

        if any(not state for state in normalized_states):
            raise ValueError("Strategy rule states must not be empty.")

        if len(set(normalized_states)) != len(normalized_states):
            raise ValueError("Strategy rule states must be unique.")

        object.__setattr__(
            self,
            "rule_id",
            self.rule_id.strip(),
        )
        object.__setattr__(
            self,
            "name",
            self.name.strip(),
        )
        object.__setattr__(
            self,
            "states",
            normalized_states,
        )
