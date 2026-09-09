from dataclasses import dataclass

from private_quant_terminal.research.behavior_diagnostics import (
    ResearchBehaviorDiagnostics,
)


@dataclass(frozen=True)
class ResearchBehaviorFinding:
    """A deterministic, evidence-qualified behavior finding."""

    category: str
    statement: str
    evidence: str


class ResearchBehaviorFindingsCalculator:
    """Derive deterministic findings from measured behavior diagnostics."""

    def calculate(
        self,
        diagnostics: ResearchBehaviorDiagnostics,
    ) -> tuple[ResearchBehaviorFinding, ...]:
        findings: list[ResearchBehaviorFinding] = []

        total_trades = (
            diagnostics.winning_trade_count
            + diagnostics.losing_trade_count
            + diagnostics.zero_pnl_trade_count
        )

        if total_trades == 0:
            findings.append(
                ResearchBehaviorFinding(
                    category="sample",
                    statement="No completed trades were available for behavior analysis.",
                    evidence="total_trades=0",
                )
            )
            return tuple(findings)

        if diagnostics.winning_trade_count > 0:
            findings.append(
                ResearchBehaviorFinding(
                    category="outcomes",
                    statement="The research sample contains completed winning trades.",
                    evidence=(
                        f"winning_trade_count={diagnostics.winning_trade_count}; "
                        f"winning_pnl={diagnostics.winning_pnl}"
                    ),
                )
            )

        if diagnostics.losing_trade_count > 0:
            findings.append(
                ResearchBehaviorFinding(
                    category="outcomes",
                    statement="The research sample contains completed losing trades.",
                    evidence=(
                        f"losing_trade_count={diagnostics.losing_trade_count}; "
                        f"losing_pnl={diagnostics.losing_pnl}"
                    ),
                )
            )

        if diagnostics.zero_pnl_trade_count > 0:
            findings.append(
                ResearchBehaviorFinding(
                    category="outcomes",
                    statement="The research sample contains zero-P&L completed trades.",
                    evidence=(
                        f"zero_pnl_trade_count={diagnostics.zero_pnl_trade_count}"
                    ),
                )
            )

        if diagnostics.winning_trade_count > 0 and diagnostics.losing_trade_count > 0:
            if (
                diagnostics.average_winning_trade
                > abs(diagnostics.average_losing_trade)
            ):
                statement = (
                    "Average winning trade magnitude exceeded average losing trade "
                    "magnitude in the completed-trade sample."
                )
            elif (
                diagnostics.average_winning_trade
                < abs(diagnostics.average_losing_trade)
            ):
                statement = (
                    "Average losing trade magnitude exceeded average winning trade "
                    "magnitude in the completed-trade sample."
                )
            else:
                statement = (
                    "Average winning and losing trade magnitudes were equal in the "
                    "completed-trade sample."
                )

            findings.append(
                ResearchBehaviorFinding(
                    category="payoff",
                    statement=statement,
                    evidence=(
                        f"average_winning_trade={diagnostics.average_winning_trade}; "
                        f"average_losing_trade={diagnostics.average_losing_trade}"
                    ),
                )
            )

        if diagnostics.loss_by_entry_hour:
            peak_hour, peak_loss = max(
                diagnostics.loss_by_entry_hour,
                key=lambda item: item[1],
            )

            total_loss = sum(
                loss for _, loss in diagnostics.loss_by_entry_hour
            )

            concentration = peak_loss / total_loss if total_loss else 0.0

            findings.append(
                ResearchBehaviorFinding(
                    category="loss_concentration",
                    statement=(
                        f"The largest absolute loss concentration occurred among "
                        f"trades entered at hour {peak_hour:02d}:00."
                    ),
                    evidence=(
                        f"entry_hour={peak_hour}; "
                        f"absolute_loss={peak_loss}; "
                        f"share_of_entry_hour_losses={concentration}"
                    ),
                )
            )

        return tuple(findings)
