from __future__ import annotations

from enum import Enum


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
