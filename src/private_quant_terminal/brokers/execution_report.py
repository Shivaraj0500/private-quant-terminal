from dataclasses import dataclass

from private_quant_terminal.brokers.order_status import OrderStatus


@dataclass(frozen=True)
class ExecutionReport:
    """Result of broker processing for an order."""

    order_id: str
    status: OrderStatus
    filled_quantity: int
    remaining_quantity: int
    average_price: float | None = None
