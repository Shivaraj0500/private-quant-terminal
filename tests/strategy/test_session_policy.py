from datetime import UTC, datetime, time

from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.session_policy import SessionPolicyEvaluator
from private_quant_terminal.strategy.states import ReentryPolicy, SessionMode
from private_quant_terminal.strategy.variables import SessionContext


def session_context(
    current_time: datetime,
    *,
    entries_today: int = 0,
    trades_today: int = 0,
    last_exit_time: datetime | None = None,
) -> SessionContext:
    return SessionContext(
        current_time=current_time,
        entries_today=entries_today,
        trades_today=trades_today,
        last_exit_time=last_exit_time,
    )


def test_market_open_inside_window() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
    )

    context = session_context(datetime(2026, 8, 30, 10, 0, tzinfo=UTC))

    assert SessionPolicyEvaluator().market_open(session, context) is True


def test_market_open_outside_window() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
    )

    evaluator = SessionPolicyEvaluator()

    assert evaluator.market_open(
        session,
        session_context(datetime(2026, 8, 30, 9, 0, tzinfo=UTC)),
    ) is False

    assert evaluator.market_open(
        session,
        session_context(datetime(2026, 8, 30, 16, 0, tzinfo=UTC)),
    ) is False


def test_entry_window() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        market_start=time(9, 15),
        market_end=time(15, 30),
        entry_start=time(9, 30),
        entry_end=time(14, 30),
    )

    evaluator = SessionPolicyEvaluator()

    assert evaluator.entry_allowed(
        session,
        session_context(datetime(2026, 8, 30, 10, 0, tzinfo=UTC)),
    ) is True

    assert evaluator.entry_allowed(
        session,
        session_context(datetime(2026, 8, 30, 9, 20, tzinfo=UTC)),
    ) is False

    assert evaluator.entry_allowed(
        session,
        session_context(datetime(2026, 8, 30, 14, 45, tzinfo=UTC)),
    ) is False


def test_entry_limit() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_entries_per_session=2,
    )

    evaluator = SessionPolicyEvaluator()

    assert evaluator.entry_limit_reached(
        session,
        session_context(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            entries_today=1,
        ),
    ) is False

    assert evaluator.entry_limit_reached(
        session,
        session_context(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            entries_today=2,
        ),
    ) is True


def test_trade_limit() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        max_trades_per_session=2,
    )

    evaluator = SessionPolicyEvaluator()

    assert evaluator.trade_limit_reached(
        session,
        session_context(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            trades_today=1,
        ),
    ) is False

    assert evaluator.trade_limit_reached(
        session,
        session_context(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            trades_today=2,
        ),
    ) is True


def test_force_exit_for_intraday() -> None:
    session = StrategySession(
        mode=SessionMode.INTRADAY,
        force_exit_at=time(15, 10),
    )

    evaluator = SessionPolicyEvaluator()

    assert evaluator.force_exit(
        session,
        session_context(datetime(2026, 8, 30, 15, 9, tzinfo=UTC)),
    ) is False

    assert evaluator.force_exit(
        session,
        session_context(datetime(2026, 8, 30, 15, 10, tzinfo=UTC)),
    ) is True


def test_force_exit_not_required_for_overnight() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
    )

    assert SessionPolicyEvaluator().force_exit(
        session,
        session_context(datetime(2026, 8, 30, 15, 10, tzinfo=UTC)),
    ) is False


def test_block_policy_allows_first_entry() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.BLOCK,
    )

    assert SessionPolicyEvaluator().reentry_allowed(
        session,
        session_context(datetime(2026, 8, 30, 10, 0, tzinfo=UTC)),
    ) is True


def test_block_policy_rejects_reentry() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.BLOCK,
    )

    context = session_context(
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        last_exit_time=datetime(2026, 8, 30, 9, 45, tzinfo=UTC),
    )

    assert SessionPolicyEvaluator().reentry_allowed(
        session,
        context,
    ) is False


def test_allow_policy_allows_reentry() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.ALLOW,
    )

    context = session_context(
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        last_exit_time=datetime(2026, 8, 30, 9, 45, tzinfo=UTC),
    )

    assert SessionPolicyEvaluator().reentry_allowed(
        session,
        context,
    ) is True


def test_cooldown_policy_rejects_before_cooldown() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.AFTER_COOLDOWN,
        cooldown_minutes=15,
    )

    context = session_context(
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        last_exit_time=datetime(2026, 8, 30, 9, 50, tzinfo=UTC),
    )

    assert SessionPolicyEvaluator().reentry_allowed(
        session,
        context,
    ) is False


def test_cooldown_policy_allows_after_cooldown() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.AFTER_COOLDOWN,
        cooldown_minutes=15,
    )

    context = session_context(
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        last_exit_time=datetime(2026, 8, 30, 9, 45, tzinfo=UTC),
    )

    assert SessionPolicyEvaluator().reentry_allowed(
        session,
        context,
    ) is True


def test_entry_allowed_respects_all_limits() -> None:
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

    evaluator = SessionPolicyEvaluator()

    assert evaluator.entry_allowed(
        session,
        session_context(datetime(2026, 8, 30, 10, 0, tzinfo=UTC)),
    ) is True

    assert evaluator.entry_allowed(
        session,
        session_context(
            datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
            entries_today=1,
        ),
    ) is False


def test_entry_allowed_rejects_after_exit_with_block_policy() -> None:
    session = StrategySession(
        mode=SessionMode.OVERNIGHT,
        reentry_policy=ReentryPolicy.BLOCK,
    )

    context = session_context(
        datetime(2026, 8, 30, 10, 0, tzinfo=UTC),
        last_exit_time=datetime(2026, 8, 30, 9, 45, tzinfo=UTC),
    )

    assert SessionPolicyEvaluator().entry_allowed(
        session,
        context,
    ) is False
