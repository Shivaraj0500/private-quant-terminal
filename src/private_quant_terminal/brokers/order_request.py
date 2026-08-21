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
    time_in_force: TimeInForce = TimeInForce.DAY
