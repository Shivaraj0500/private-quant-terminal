from dataclasses import dataclass


@dataclass(frozen=True)
class Allocation:
    """Represents the capital allocation for a portfolio position."""

    symbol: str
    market_value: float
    portfolio_value: float

    @property
    def weight(self) -> float:
        """Return the position weight as a fraction of portfolio value."""
        if self.portfolio_value <= 0:
            raise ValueError(
                "portfolio_value must be greater than zero"
            )

        return self.market_value / self.portfolio_value