from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
    HedgeAction,
    ModifyAction,
    RollAction,
    StrategyAction,
)
from private_quant_terminal.strategy.positions import PositionGroup
from private_quant_terminal.strategy.positions_state import PositionStateSnapshot
from private_quant_terminal.strategy.states import PositionState


@dataclass(frozen=True)
class ActionProcessingResult:
    """Result of processing one strategy action."""

    action: StrategyAction
    snapshots: tuple[PositionStateSnapshot, ...]


class ActionProcessor:
    """Apply strategy actions to deterministic position-group state."""

    def __init__(self) -> None:
        self._groups: dict[str, PositionGroup] = {}
        self._states: dict[str, PositionStateSnapshot] = {}
        self._modifications: dict[str, tuple[tuple[str, float | str | bool], ...]] = {}

    def process(
        self,
        action: StrategyAction,
    ) -> ActionProcessingResult:
        """Process one strategy action deterministically."""

        if isinstance(action, EnterAction):
            self._enter(action.position)

        elif isinstance(action, ExitAction):
            self._exit(action.group_id)

        elif isinstance(action, ModifyAction):
            self._modify(action)

        elif isinstance(action, RollAction):
            self._roll(action)

        elif isinstance(action, HedgeAction):
            self._hedge(action)

        else:
            raise TypeError(
                f"Unsupported strategy action: {type(action).__name__}"
            )

        return ActionProcessingResult(
            action=action,
            snapshots=self.snapshots(),
        )

    def process_all(
        self,
        actions: tuple[StrategyAction, ...],
    ) -> tuple[ActionProcessingResult, ...]:
        """Process actions in their supplied deterministic order."""

        return tuple(self.process(action) for action in actions)

    def get_position(
        self,
        group_id: str,
    ) -> PositionGroup | None:
        """Return an active position group, if present."""

        return self._groups.get(group_id)

    def get_state(
        self,
        group_id: str,
    ) -> PositionStateSnapshot | None:
        """Return the current state snapshot for a group."""

        return self._states.get(group_id)

    def snapshots(self) -> tuple[PositionStateSnapshot, ...]:
        """Return current position-state snapshots in insertion order."""

        return tuple(self._states.values())

    def modifications(
        self,
        group_id: str,
    ) -> tuple[tuple[str, float | str | bool], ...]:
        """Return management modifications recorded for a group."""

        return self._modifications.get(group_id, ())

    def _enter(self, position: PositionGroup) -> None:
        """Open a new position group."""

        group_id = position.group_id

        if group_id in self._groups:
            raise ValueError(
                f"Position group {group_id!r} is already open."
            )

        self._groups[group_id] = position
        self._states[group_id] = PositionStateSnapshot(
            group_id=group_id,
            state=PositionState.OPEN,
            entry_count=1,
            exit_count=0,
        )

    def _exit(self, group_id: str) -> None:
        """Close an existing position group."""

        if group_id not in self._groups:
            raise KeyError(
                f"Unknown position group: {group_id!r}"
            )

        current = self._states[group_id]

        self._groups.pop(group_id)
        self._states[group_id] = PositionStateSnapshot(
            group_id=group_id,
            state=PositionState.CLOSED,
            entry_count=current.entry_count,
            exit_count=current.exit_count + 1,
        )

    def _modify(self, action: ModifyAction) -> None:
        """Record management changes for an existing position group."""

        if action.group_id not in self._groups:
            raise KeyError(
                f"Unknown position group: {action.group_id!r}"
            )

        existing = self._modifications.get(action.group_id, ())
        self._modifications[action.group_id] = existing + action.changes

    def _roll(self, action: RollAction) -> None:
        """Close the old group and open its replacement."""

        if action.group_id not in self._groups:
            raise KeyError(
                f"Unknown position group: {action.group_id!r}"
            )

        if action.replacement.group_id in self._groups:
            raise ValueError(
                f"Replacement position group "
                f"{action.replacement.group_id!r} is already open."
            )

        self._exit(action.group_id)
        self._enter(action.replacement)

    def _hedge(self, action: HedgeAction) -> None:
        """Open a hedge group alongside the referenced position group."""

        if action.group_id not in self._groups:
            raise KeyError(
                f"Unknown position group: {action.group_id!r}"
            )

        self._enter(action.hedge)
