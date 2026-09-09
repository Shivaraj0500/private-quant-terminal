from collections import Counter
from dataclasses import dataclass

from private_quant_terminal.research.execution import ResearchTrade


@dataclass(frozen=True)
class ResearchBehaviorDiagnostics:
    """Immutable deterministic strategy-behavior diagnostics."""

    entry_hour_distribution: tuple[tuple[int, int], ...]
    exit_hour_distribution: tuple[tuple[int, int], ...]
    winning_trade_count: int
    losing_trade_count: int
    zero_pnl_trade_count: int
    winning_pnl: float
    losing_pnl: float
    average_winning_trade: float
    average_losing_trade: float
    loss_by_entry_hour: tuple[tuple[int, float], ...]


class ResearchBehaviorDiagnosticsCalculator:
    """Calculate deterministic behavior diagnostics from completed trades."""

    def calculate(
        self,
        trades: tuple[ResearchTrade, ...],
    ) -> ResearchBehaviorDiagnostics:
        entry_hours = Counter(trade.entry_time.hour for trade in trades)
        exit_hours = Counter(trade.exit_time.hour for trade in trades)

        winning_pnls = tuple(
            trade.net_pnl for trade in trades if trade.net_pnl > 0
        )
        losing_pnls = tuple(
            trade.net_pnl for trade in trades if trade.net_pnl < 0
        )

        zero_pnl_trade_count = sum(
            trade.net_pnl == 0 for trade in trades
        )

        loss_by_entry_hour: dict[int, float] = {}

        for trade in trades:
            if trade.net_pnl < 0:
                hour = trade.entry_time.hour
                loss_by_entry_hour[hour] = (
                    loss_by_entry_hour.get(hour, 0.0)
                    + abs(trade.net_pnl)
                )

        return ResearchBehaviorDiagnostics(
            entry_hour_distribution=tuple(sorted(entry_hours.items())),
            exit_hour_distribution=tuple(sorted(exit_hours.items())),
            winning_trade_count=len(winning_pnls),
            losing_trade_count=len(losing_pnls),
            zero_pnl_trade_count=zero_pnl_trade_count,
            winning_pnl=sum(winning_pnls),
            losing_pnl=sum(losing_pnls),
            average_winning_trade=(
                sum(winning_pnls) / len(winning_pnls)
                if winning_pnls
                else 0.0
            ),
            average_losing_trade=(
                sum(losing_pnls) / len(losing_pnls)
                if losing_pnls
                else 0.0
            ),
            loss_by_entry_hour=tuple(sorted(loss_by_entry_hour.items())),
        )
