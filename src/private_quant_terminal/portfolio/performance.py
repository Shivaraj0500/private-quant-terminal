from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceSnapshot:
    """Immutable summary of portfolio trading performance."""

    realized_pnl: float
    unrealized_pnl: float
    total_pnl: float
    winning_trades: int
    losing_trades: int
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float

    def __post_init__(self) -> None:
        if self.winning_trades < 0:
            raise ValueError(
                "winning_trades cannot be negative"
            )

        if self.losing_trades < 0:
            raise ValueError(
                "losing_trades cannot be negative"
            )

        if not 0.0 <= self.win_rate <= 100.0:
            raise ValueError(
                "win_rate must be between 0 and 100"
            )