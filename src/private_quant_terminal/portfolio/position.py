from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Represents a portfolio position managed by the application."""

    symbol: str
    quantity: int
    average_price: float

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

        if self.average_price <= 0:
            raise ValueError("average_price must be greater than zero")

    @property
    def cost_basis(self) -> float:
        """Return the total acquisition value of the position."""
        return self.quantity * self.average_price

    def market_value(self, current_price: float) -> float:
        """Return the current market value of the position."""
        self._validate_current_price(current_price)
        return self.quantity * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        """Return the unrealized profit or loss."""
        return self.market_value(current_price) - self.cost_basis

    def unrealized_pnl_percentage(self, current_price: float) -> float:
        """Return the unrealized profit or loss as a percentage."""
        if self.cost_basis == 0:
            return 0.0

        return self.unrealized_pnl(current_price) / abs(self.cost_basis)

    @staticmethod
    def _validate_current_price(current_price: float) -> None:
        if current_price <= 0:
            raise ValueError("current_price must be greater than zero")