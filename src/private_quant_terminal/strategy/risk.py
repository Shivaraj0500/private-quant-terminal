from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.variables import StrategyRuntimeContext


@dataclass(frozen=True)
class StrategyRiskResult:
    """Deterministic result of evaluating strategy-level risk constraints."""

    approved: bool
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.approved and self.reasons:
            raise ValueError(
                "Approved risk results cannot contain rejection reasons."
            )

        if not self.approved and not self.reasons:
            raise ValueError(
                "Rejected risk results must contain at least one reason."
            )


class StrategyRiskEvaluator:
    """Evaluate strategy-level risk constraints without mutating state."""

    def evaluate(
        self,
        session: StrategySession,
        context: StrategyRuntimeContext,
    ) -> StrategyRiskResult:
        """Evaluate all currently defined strategy risk constraints."""

        reasons: list[str] = []

        if context.session is not None:
            if (
                session.max_entries_per_session is not None
                and context.session.entries_today
                > session.max_entries_per_session
            ):
                reasons.append(
                    "Strategy entry count exceeds configured session maximum."
                )

            if (
                session.max_trades_per_session is not None
                and context.session.trades_today
                > session.max_trades_per_session
            ):
                reasons.append(
                    "Strategy trade count exceeds configured session maximum."
                )

        return StrategyRiskResult(
            approved=not reasons,
            reasons=tuple(reasons),
        )
