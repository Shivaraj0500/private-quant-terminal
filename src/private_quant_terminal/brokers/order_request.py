from dataclasses import dataclass

from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.brokers.time_in_force import TimeInForce


@dataclass(frozen=True)
class OrderRequest:
    """Request to place a broker order."""

    symbol: str
    quantity: int
    side: OrderSide
    order_type: OrderType
    price: float | None = None
    time_in_force: TimeInForce = TimeInForce.DAY

    def __post_init__(self) -> None:
        """Validate order request values."""
        if not self.symbol:
            raise ValueError("symbol cannot be empty")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.price is not None and self.price <= 0:
            raise ValueError("price must be greater than zero")