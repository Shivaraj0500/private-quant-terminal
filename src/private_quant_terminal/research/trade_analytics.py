from dataclasses import dataclass
from datetime import timedelta

from private_quant_terminal.research.execution import ResearchTrade


@dataclass(frozen=True)
class ResearchTradeAnalytics:
    """Immutable trade-level analytics for a research execution."""

    total_trades: int
    average_trade: float
    best_trade: float
    worst_trade: float
    average_holding_time: timedelta
    shortest_holding_time: timedelta
    longest_holding_time: timedelta
    max_consecutive_wins: int
    max_consecutive_losses: int


class ResearchTradeAnalyticsCalculator:
    """Calculate deterministic analytics from completed research trades."""

    def calculate(
        self,
        trades: tuple[ResearchTrade, ...],
    ) -> ResearchTradeAnalytics:
        if not trades:
            return ResearchTradeAnalytics(
                total_trades=0,
                average_trade=0.0,
                best_trade=0.0,
                worst_trade=0.0,
                average_holding_time=timedelta(0),
                shortest_holding_time=timedelta(0),
                longest_holding_time=timedelta(0),
                max_consecutive_wins=0,
                max_consecutive_losses=0,
            )

        pnls = tuple(trade.net_pnl for trade in trades)
        holding_times = tuple(trade.exit_time - trade.entry_time for trade in trades)

        return ResearchTradeAnalytics(
            total_trades=len(trades),
            average_trade=sum(pnls) / len(pnls),
            best_trade=max(pnls),
            worst_trade=min(pnls),
            average_holding_time=(sum(holding_times, timedelta(0)) / len(holding_times)),
            shortest_holding_time=min(holding_times),
            longest_holding_time=max(holding_times),
            max_consecutive_wins=self._max_consecutive(
                pnls,
                positive=True,
            ),
            max_consecutive_losses=self._max_consecutive(
                pnls,
                positive=False,
            ),
        )

    @staticmethod
    def _max_consecutive(
        pnls: tuple[float, ...],
        *,
        positive: bool,
    ) -> int:
        maximum = 0
        current = 0

        for pnl in pnls:
            is_match = pnl > 0 if positive else pnl < 0

            if is_match:
                current += 1
                maximum = max(maximum, current)
            else:
                current = 0

        return maximum
