from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.models.instrument import Instrument


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    order_id: str
    instrument: Instrument
    side: Side
    quantity: int
    price: float | None = None
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.price is not None and self.price <= 0:
            raise ValueError("price must be greater than zero")


@dataclass
class Position:
    instrument: Instrument
    quantity: int = 0
    average_price: float = 0.0

    def __post_init__(self) -> None:
        if self.average_price < 0:
            raise ValueError("average_price cannot be negative")

    @property
    def market_value(self) -> float:
        return self.quantity * self.average_price
