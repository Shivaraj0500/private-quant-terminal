from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.actions import StrategyAction
from private_quant_terminal.strategy.conditions import Condition


@dataclass(frozen=True)
class StrategyRule:
    """A deterministic WHEN/THEN strategy rule."""

    rule_id: str
    name: str
    condition: Condition
    actions: tuple[StrategyAction, ...]
    priority: int = 0
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("Rule ID must not be empty.")

        if not self.name.strip():
            raise ValueError("Rule name must not be empty.")

        if not self.actions:
            raise ValueError(
                "Strategy rule must contain at least one action."
            )

        if self.priority < 0:
            raise ValueError("Rule priority cannot be negative.")

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
