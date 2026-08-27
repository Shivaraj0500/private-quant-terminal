from private_quant_terminal.portfolio.closed_trade import ClosedTrade
from private_quant_terminal.portfolio.performance import (
    PerformanceSnapshot,
)


class PortfolioPerformanceCalculator:
    """Calculate trading performance from completed trades."""

    def calculate(
        self,
        closed_trades: tuple[ClosedTrade, ...],
    ) -> PerformanceSnapshot:
        """Calculate a performance summary from closed trades."""
        realized_pnl = sum(
            trade.realized_pnl
            for trade in closed_trades
        )

        winning_pnls = [
            trade.realized_pnl
            for trade in closed_trades
            if trade.realized_pnl > 0
        ]

        losing_pnls = [
            trade.realized_pnl
            for trade in closed_trades
            if trade.realized_pnl < 0
        ]

        winning_trades = len(winning_pnls)
        losing_trades = len(losing_pnls)

        total_trades = winning_trades + losing_trades

        win_rate = self._win_rate(
            winning_trades=winning_trades,
            total_trades=total_trades,
        )

        average_win = self._average(
            values=winning_pnls,
        )

        average_loss = self._average(
            values=losing_pnls,
        )

        profit_factor = self._profit_factor(
            winning_pnls=winning_pnls,
            losing_pnls=losing_pnls,
        )

        return PerformanceSnapshot(
            realized_pnl=realized_pnl,
            unrealized_pnl=0.0,
            total_pnl=realized_pnl,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            average_win=average_win,
            average_loss=average_loss,
            profit_factor=profit_factor,
        )

    @staticmethod
    def _win_rate(
        winning_trades: int,
        total_trades: int,
    ) -> float:
        """Calculate the percentage of profitable trades."""
        if total_trades == 0:
            return 0.0

        return (
            winning_trades / total_trades
        ) * 100.0

    @staticmethod
    def _average(
        values: list[float],
    ) -> float:
        """Calculate an average, returning zero for no values."""
        if not values:
            return 0.0

        return sum(values) / len(values)

    @staticmethod
    def _profit_factor(
        winning_pnls: list[float],
        losing_pnls: list[float],
    ) -> float:
        """Calculate gross profit divided by absolute gross loss."""
        gross_profit = sum(winning_pnls)
        gross_loss = abs(sum(losing_pnls))

        if gross_loss == 0.0:
            if gross_profit == 0.0:
                return 0.0

            return float("inf")

        return gross_profit / gross_loss
