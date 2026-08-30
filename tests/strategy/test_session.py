from datetime import time

import pytest

from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.states import (
    ReentryPolicy,
    SessionMode,
)


def test_intraday_session() -> None:
    session = StrategySession(
        mode=SessionMode.INTRADAY,
        market_start=time(9, 15),
        market_end=time(15, 30),
        entry_start=time(9, 30),
        entry_end=time(14, 30),
        force_exit_at=time(15, 10),
        max_entries_per_session=1,
        max_trades_per_session=1,
        reentry_policy=ReentryPolicy.BLOCK,
    )

    assert session.mode is SessionMode.INTRADAY
    assert session.force_exit_at == time(15, 10)
    assert session.max_entries_per_session == 1


def test_overnight_session_does_not_require_force_exit() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
    )

    assert session.mode is SessionMode.OVERNIGHT


def test_intraday_requires_force_exit() -> None:
    with pytest.raises(
        ValueError,
        match="require force_exit_at",
    ):
        StrategySession(
            mode=SessionMode.INTRADAY,
        )


def test_cooldown_requires_duration() -> None:
    with pytest.raises(
        ValueError,
        match="requires cooldown_minutes",
    ):
        StrategySession(
            mode=SessionMode.OVERNIGHT,
            reentry_policy=ReentryPolicy.AFTER_COOLDOWN,
        )


def test_cooldown_cannot_be_used_with_block() -> None:
    with pytest.raises(
        ValueError,
        match="only valid with AFTER_COOLDOWN",
    ):
        StrategySession(
            mode=SessionMode.OVERNIGHT,
            reentry_policy=ReentryPolicy.BLOCK,
            cooldown_minutes=15,
        )


def test_invalid_market_window() -> None:
    with pytest.raises(
        ValueError,
        match="market_start must be before market_end",
    ):
        StrategySession(
            mode=SessionMode.OVERNIGHT,
            market_start=time(15, 30),
            market_end=time(9, 15),
        )
