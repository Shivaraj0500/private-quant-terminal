from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from private_quant_terminal.strategy.actions import (
    EnterAction,
    ExitAction,
    RollAction,
    StrategyAction,
)
from private_quant_terminal.strategy.variables import SessionContext


@dataclass(frozen=True)
class StrategyRuntimeState:
    """Mutable-in-practice, immutable-snapshot runtime strategy state."""

    session: SessionContext

    def apply(
        self,
        action: StrategyAction,
        timestamp: datetime,
    ) -> StrategyRuntimeState:
        """Return the next runtime state after a successful action."""

        context = self.session

        if isinstance(action, EnterAction):
            return StrategyRuntimeState(
                session=SessionContext(
                    current_time=timestamp,
                    entries_today=context.entries_today + 1,
                    trades_today=context.trades_today + 1,
                    bars_since_entry=0,
                    minutes_since_entry=0.0,
                    last_entry_time=timestamp,
                    last_exit_time=context.last_exit_time,
                )
            )

        if isinstance(action, ExitAction):
            return StrategyRuntimeState(
                session=SessionContext(
                    current_time=timestamp,
                    entries_today=context.entries_today,
                    trades_today=context.trades_today,
                    bars_since_entry=context.bars_since_entry,
                    minutes_since_entry=context.minutes_since_entry,
                    last_entry_time=context.last_entry_time,
                    last_exit_time=timestamp,
                )
            )

        if isinstance(action, RollAction):
            return StrategyRuntimeState(
                session=SessionContext(
                    current_time=timestamp,
                    entries_today=context.entries_today + 1,
                    trades_today=context.trades_today + 1,
                    bars_since_entry=0,
                    minutes_since_entry=0.0,
                    last_entry_time=timestamp,
                    last_exit_time=timestamp,
                )
            )

        return StrategyRuntimeState(
            session=SessionContext(
                current_time=timestamp,
                entries_today=context.entries_today,
                trades_today=context.trades_today,
                bars_since_entry=context.bars_since_entry,
                minutes_since_entry=context.minutes_since_entry,
                last_entry_time=context.last_entry_time,
                last_exit_time=context.last_exit_time,
            )
        )

    def advance_bar(
        self,
        timestamp: datetime,
        *,
        minutes: float,
    ) -> StrategyRuntimeState:
        """Advance time-based session state without executing an action."""

        if minutes < 0:
            raise ValueError("minutes cannot be negative.")

        context = self.session

        return StrategyRuntimeState(
            session=SessionContext(
                current_time=timestamp,
                entries_today=context.entries_today,
                trades_today=context.trades_today,
                bars_since_entry=context.bars_since_entry + 1,
                minutes_since_entry=(
                    None
                    if context.last_entry_time is None
                    else (
                        context.minutes_since_entry or 0.0
                    ) + minutes
                ),
                last_entry_time=context.last_entry_time,
                last_exit_time=context.last_exit_time,
            )
        )
