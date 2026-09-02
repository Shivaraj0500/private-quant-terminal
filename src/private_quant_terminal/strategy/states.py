from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.strategy.actions import StrategyAction
from private_quant_terminal.strategy.conditions import Condition


class StrategyExecutionState(str, Enum):
    """Lifecycle state of a running strategy execution."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"


class PositionState(str, Enum):
    """Current state of a strategy position."""

    FLAT = "FLAT"
    OPEN = "OPEN"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"


class SessionMode(str, Enum):
    """Trading session behavior."""

    INTRADAY = "INTRADAY"
    OVERNIGHT = "OVERNIGHT"


class ReentryPolicy(str, Enum):
    """Controls whether a strategy may enter again after exiting."""

    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    AFTER_COOLDOWN = "AFTER_COOLDOWN"


@dataclass(frozen=True)
class StrategyState:
    """Declarative semantic state of a strategy."""

    state_id: str
    name: str
    initial: bool = False
    terminal: bool = False

    def __post_init__(self) -> None:
        state_id = self.state_id.strip()
        name = self.name.strip()

        if not state_id:
            raise ValueError("Strategy state ID must not be empty.")

        if not name:
            raise ValueError("Strategy state name must not be empty.")

        object.__setattr__(self, "state_id", state_id)
        object.__setattr__(self, "name", name)


@dataclass(frozen=True)
class StateTransition:
    """Declarative transition between strategy semantic states."""

    transition_id: str
    from_state: str
    to_state: str
    condition: Condition
    actions: tuple[StrategyAction, ...]
    priority: int = 0
    enabled: bool = True

    def __post_init__(self) -> None:
        transition_id = self.transition_id.strip()
        from_state = self.from_state.strip()
        to_state = self.to_state.strip()

        if not transition_id:
            raise ValueError("State transition ID must not be empty.")

        if not from_state:
            raise ValueError("State transition source must not be empty.")

        if not to_state:
            raise ValueError("State transition target must not be empty.")

        if not self.actions:
            raise ValueError(
                "State transition must contain at least one action."
            )

        if self.priority < 0:
            raise ValueError("State transition priority cannot be negative.")

        object.__setattr__(self, "transition_id", transition_id)
        object.__setattr__(self, "from_state", from_state)
        object.__setattr__(self, "to_state", to_state)
