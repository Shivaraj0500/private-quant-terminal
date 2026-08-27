from private_quant_terminal.brokers.execution import BrokerExecution
from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order import BrokerOrder
from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_status import OrderStatus


class InMemoryBrokerExecution(BrokerExecution):
    """Simple in-memory broker that fills priced orders immediately."""

    def __init__(self) -> None:
        """Initialize the in-memory broker."""
        self._next_order_number = 1

    def place_order(self, request: OrderRequest) -> ExecutionReport:
        """Fill an order immediately at its supplied price."""
        if request.price is None:
            raise ValueError(
                "in-memory broker execution requires an order price"
            )

        order_id = f"ORDER-{self._next_order_number}"
        self._next_order_number += 1

        return ExecutionReport(
            order_id=order_id,
            status=OrderStatus.FILLED,
            filled_quantity=request.quantity,
            remaining_quantity=0,
            average_price=request.price,
        )

    def modify_order(
        self,
        order_id: str,
        request: OrderRequest,
    ) -> ExecutionReport:
        """Modification is not supported by the in-memory broker."""
        raise NotImplementedError(
            "Order modification is not supported"
        )

    def cancel_order(self, order_id: str) -> ExecutionReport:
        """Cancellation is not supported by the in-memory broker."""
        raise NotImplementedError(
            "Order cancellation is not supported"
        )

    def get_order(self, order_id: str) -> BrokerOrder:
        """Order lookup is not supported by the in-memory broker."""
        raise NotImplementedError(
            "Order lookup is not supported"
        )

    def get_orders(self) -> list[BrokerOrder]:
        """Order listing is not supported by the in-memory broker."""
        raise NotImplementedError(
            "Order listing is not supported"
        )