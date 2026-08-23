from dataclasses import dataclass

from private_quant_terminal.portfolio.position import Position


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Immutable snapshot of current portfolio performance."""

    positions: tuple[Position, ...]
    realized_pnl: float
    unrealized_pnl: float

    @property
    def total_pnl(self) -> float:
        """Return total realized and unrealized profit and loss."""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def open_position_count(self) -> int:
        """Return the number of open positions."""
        return len(self.positions)
