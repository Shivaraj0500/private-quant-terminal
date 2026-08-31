from datetime import UTC, datetime

import pytest

from private_quant_terminal.strategy.risk import (
    StrategyRiskEvaluator,
    StrategyRiskResult,
)
from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.states import SessionMode
from private_quant_terminal.strategy.variables import (
    MarketContext,
    PositionContext,
    SessionContext,
    StrategyRuntimeContext,
)


def context(
    *,
    entries_today: int = 0,
    trades_today: int = 0,
) -> StrategyRuntimeContext:
    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    return StrategyRuntimeContext(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
        ),
        position=PositionContext(),
        session=SessionContext(
            current_time=timestamp,
            entries_today=entries_today,
            trades_today=trades_today,
        ),
    )


def test_risk_is_approved_when_no_limits_are_breached() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=2,
        max_trades_per_session=3,
    )

    result = StrategyRiskEvaluator().evaluate(
        session,
        context(entries_today=1, trades_today=2),
    )

    assert result == StrategyRiskResult(approved=True)


def test_entry_limit_rejection() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=2,
    )

    result = StrategyRiskEvaluator().evaluate(
        session,
        context(entries_today=3),
    )

    assert result.approved is False
    assert result.reasons == (
        "Strategy entry count exceeds configured session maximum.",
    )


def test_trade_limit_rejection() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_trades_per_session=2,
    )

    result = StrategyRiskEvaluator().evaluate(
        session,
        context(trades_today=3),
    )

    assert result.approved is False
    assert result.reasons == (
        "Strategy trade count exceeds configured session maximum.",
    )


def test_multiple_risk_rejections_are_deterministic() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=1,
        max_trades_per_session=1,
    )

    result = StrategyRiskEvaluator().evaluate(
        session,
        context(entries_today=2, trades_today=2),
    )

    assert result.approved is False
    assert result.reasons == (
        "Strategy entry count exceeds configured session maximum.",
        "Strategy trade count exceeds configured session maximum.",
    )


def test_missing_session_context_does_not_fail() -> None:
    timestamp = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)

    runtime = StrategyRuntimeContext(
        market=MarketContext(
            timestamp=timestamp,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
        )
    )

    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=1,
    )

    result = StrategyRiskEvaluator().evaluate(session, runtime)

    assert result == StrategyRiskResult(approved=True)


def test_risk_result_is_immutable() -> None:
    result = StrategyRiskResult(approved=True)

    with pytest.raises(AttributeError):
        result.approved = False
