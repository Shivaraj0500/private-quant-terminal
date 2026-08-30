from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.strategy.positions import PositionGroup


class ActionType(str, Enum):
    """Actions a strategy may request."""

    ENTER = "ENTER"
    EXIT = "EXIT"
    MODIFY = "MODIFY"
    ROLL = "ROLL"
    HEDGE = "HEDGE"


@dataclass(frozen=True)
class EnterAction:
    """Open a new position group."""

    position: PositionGroup

    @property
    def action_type(self) -> ActionType:
        return ActionType.ENTER


@dataclass(frozen=True)
class ExitAction:
    """Close an existing position group."""

    group_id: str

    @property
    def action_type(self) -> ActionType:
        return ActionType.EXIT

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Exit group ID must not be empty.")


@dataclass(frozen=True)
class ModifyAction:
    """Modify an existing position group's management parameters."""

    group_id: str
    changes: tuple[tuple[str, float | str | bool], ...]

    @property
    def action_type(self) -> ActionType:
        return ActionType.MODIFY

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Modify group ID must not be empty.")

        if not self.changes:
            raise ValueError(
                "Modify action must contain at least one change."
            )

        object.__setattr__(
            self,
            "group_id",
            self.group_id.strip(),
        )


@dataclass(frozen=True)
class RollAction:
    """Replace an existing position group with a new group."""

    group_id: str
    replacement: PositionGroup

    @property
    def action_type(self) -> ActionType:
        return ActionType.ROLL

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Roll group ID must not be empty.")

        object.__setattr__(
            self,
            "group_id",
            self.group_id.strip(),
        )


@dataclass(frozen=True)
class HedgeAction:
    """Add a hedge position to an existing position group."""

    group_id: str
    hedge: PositionGroup

    @property
    def action_type(self) -> ActionType:
        return ActionType.HEDGE

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Hedge group ID must not be empty.")

        object.__setattr__(
            self,
            "group_id",
            self.group_id.strip(),
        )


StrategyAction = (
    EnterAction
    | ExitAction
    | ModifyAction
    | RollAction
    | HedgeAction
)
