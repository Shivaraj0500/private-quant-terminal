from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    """Portfolio and order-level risk limits."""

    max_position_quantity: int
    max_order_quantity: int
    max_open_positions: int
    max_daily_loss: float

    def __post_init__(self) -> None:
        if self.max_position_quantity <= 0:
            raise ValueError(
                "max_position_quantity must be greater than zero"
            )

        if self.max_order_quantity <= 0:
            raise ValueError(
                "max_order_quantity must be greater than zero"
            )

        if self.max_open_positions <= 0:
            raise ValueError(
                "max_open_positions must be greater than zero"
            )

        if self.max_daily_loss <= 0:
            raise ValueError(
                "max_daily_loss must be greater than zero"
            )
