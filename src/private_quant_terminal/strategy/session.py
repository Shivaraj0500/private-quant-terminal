from __future__ import annotations

from dataclasses import dataclass
from datetime import time

from private_quant_terminal.strategy.states import (
    ReentryPolicy,
    SessionMode,
)


@dataclass(frozen=True)
class StrategySession:
    """Declarative trading-session constraints."""

    mode: SessionMode = SessionMode.INTRADAY

    market_start: time | None = None
    market_end: time | None = None

    entry_start: time | None = None
    entry_end: time | None = None

    force_exit_at: time | None = None

    max_entries_per_session: int | None = None
    max_trades_per_session: int | None = None

    reentry_policy: ReentryPolicy = ReentryPolicy.BLOCK
    cooldown_minutes: int | None = None

    def __post_init__(self) -> None:
        if (
            self.max_entries_per_session is not None
            and self.max_entries_per_session <= 0
        ):
                raise ValueError(
                    "max_entries_per_session must be greater than zero."
                )

        if (
            self.max_trades_per_session is not None
            and self.max_trades_per_session <= 0
        ):
                raise ValueError(
                    "max_trades_per_session must be greater than zero."
                )

        if self.reentry_policy is ReentryPolicy.AFTER_COOLDOWN:
            if self.cooldown_minutes is None:
                raise ValueError(
                    "AFTER_COOLDOWN requires cooldown_minutes."
                )

            if self.cooldown_minutes <= 0:
                raise ValueError(
                    "cooldown_minutes must be greater than zero."
                )

        elif self.cooldown_minutes is not None:
            raise ValueError(
                "cooldown_minutes is only valid with AFTER_COOLDOWN."
            )

        if self.mode is SessionMode.INTRADAY and self.force_exit_at is None:
                raise ValueError(
                    "INTRADAY sessions require force_exit_at."
                )

        if (
            self.market_start is not None
            and self.market_end is not None
            and self.market_start >= self.market_end
        ):
            raise ValueError(
                "market_start must be before market_end."
            )

        if (
            self.entry_start is not None
            and self.entry_end is not None
            and self.entry_start >= self.entry_end
        ):
            raise ValueError(
                "entry_start must be before entry_end."
            )

        if (
            self.entry_start is not None
            and self.market_start is not None
            and self.entry_start < self.market_start
        ):
            raise ValueError(
                "entry_start cannot precede market_start."
            )

        if (
            self.entry_end is not None
            and self.market_end is not None
            and self.entry_end > self.market_end
        ):
            raise ValueError(
                "entry_end cannot exceed market_end."
            )
