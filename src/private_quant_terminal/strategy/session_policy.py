from __future__ import annotations

from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.states import ReentryPolicy, SessionMode
from private_quant_terminal.strategy.variables import SessionContext


class SessionPolicyEvaluator:
    """Evaluate declarative session constraints without mutating state."""

    def market_open(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether the market is open at the current session time."""

        current = context.current_time.time()

        if session.market_start is not None and current < session.market_start:
            return False

        return session.market_end is None or current <= session.market_end

    def entry_limit_reached(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether the per-session entry limit has been reached."""

        return (
            session.max_entries_per_session is not None
            and context.entries_today >= session.max_entries_per_session
        )

    def trade_limit_reached(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether the per-session trade limit has been reached."""

        return (
            session.max_trades_per_session is not None
            and context.trades_today >= session.max_trades_per_session
        )

    def force_exit(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether an intraday session must force an exit."""

        if session.mode is not SessionMode.INTRADAY:
            return False

        if session.force_exit_at is None:
            return False

        return context.current_time.time() >= session.force_exit_at

    def reentry_allowed(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether a new entry is permitted after an exit."""

        if session.reentry_policy is ReentryPolicy.ALLOW:
            return True

        if session.reentry_policy is ReentryPolicy.BLOCK:
            return context.last_exit_time is None

        if session.reentry_policy is ReentryPolicy.AFTER_COOLDOWN:
            if context.last_exit_time is None:
                return False

            elapsed = (
                context.current_time - context.last_exit_time
            )

            return elapsed.total_seconds() >= (
                session.cooldown_minutes * 60
            )

        raise ValueError(
            f"Unsupported reentry policy: {session.reentry_policy}"
        )

    def entry_allowed(
        self,
        session: StrategySession,
        context: SessionContext,
    ) -> bool:
        """Return whether a new strategy entry is currently permitted."""

        if not self.market_open(session, context):
            return False

        current = context.current_time.time()

        if session.entry_start is not None and current < session.entry_start:
            return False

        if session.entry_end is not None and current > session.entry_end:
            return False

        if self.entry_limit_reached(session, context):
            return False

        if self.trade_limit_reached(session, context):
            return False

        return self.reentry_allowed(session, context)
