from dataclasses import dataclass


@dataclass(frozen=True)
class Returns:
    """Represents return calculations for an investment."""

    initial_value: float
    current_value: float

    @property
    def profit_loss(self) -> float:
        """Return the absolute profit or loss."""
        return self.current_value - self.initial_value

    @property
    def return_percentage(self) -> float:
        """Return the percentage return."""
        if self.initial_value == 0:
            raise ValueError(
                "initial_value must not be zero"
            )

        return (
            self.profit_loss / self.initial_value
        ) * 100

    @property
    def is_profit(self) -> bool:
        """Return whether the investment is profitable."""
        return self.profit_loss > 0

    @property
    def is_loss(self) -> bool:
        """Return whether the investment is making a loss."""
        return self.profit_loss < 0

    @property
    def is_break_even(self) -> bool:
        """Return whether the investment is at break-even."""
        return self.profit_loss == 0