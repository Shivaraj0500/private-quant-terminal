from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.states import PositionState


@dataclass(frozen=True)
class PositionStateSnapshot:
    """Runtime state of a strategy position group."""

    group_id: str
    state: PositionState
    entry_count: int = 0
    exit_count: int = 0

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Position group ID must not be empty.")

        if self.entry_count < 0:
            raise ValueError("entry_count cannot be negative.")

        if self.exit_count < 0:
            raise ValueError("exit_count cannot be negative.")

        object.__setattr__(
            self,
            "group_id",
            self.group_id.strip(),
        )
