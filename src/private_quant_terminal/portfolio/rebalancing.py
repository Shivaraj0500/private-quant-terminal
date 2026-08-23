from dataclasses import dataclass


@dataclass(frozen=True)
class Rebalancing:
    """Represents the rebalancing requirement for a portfolio position."""

    symbol: str
    current_value: float
    portfolio_value: float
    target_weight: float

    @property
    def current_weight(self) -> float:
        """Return the current portfolio weight."""
        if self.portfolio_value <= 0:
            raise ValueError(
                "portfolio_value must be greater than zero"
            )

        return self.current_value / self.portfolio_value

    @property
    def target_value(self) -> float:
        """Return the target value for the position."""
        if not 0 <= self.target_weight <= 1:
            raise ValueError(
                "target_weight must be between 0 and 1"
            )

        if self.portfolio_value <= 0:
            raise ValueError(
                "portfolio_value must be greater than zero"
            )

        return self.portfolio_value * self.target_weight

    @property
    def adjustment(self) -> float:
        """Return the value adjustment required to reach target allocation."""
        return self.target_value - self.current_value