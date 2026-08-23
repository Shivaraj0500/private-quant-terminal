from abc import ABC, abstractmethod

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order import BrokerOrder
from private_quant_terminal.brokers.order_request import OrderRequest


class BrokerExecution(ABC):
    """Abstract interface for broker order execution."""

    @abstractmethod
    def place_order(self, request: OrderRequest) -> ExecutionReport:
        """Place an order and return its execution report."""
        raise NotImplementedError

    @abstractmethod
    def modify_order(self, order_id: str, request: OrderRequest) -> ExecutionReport:
        """Modify an existing order and return its execution report."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> ExecutionReport:
        """Cancel an existing order and return its execution report."""
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> BrokerOrder:
        """Return a specific broker order."""
        raise NotImplementedError

    @abstractmethod
    def get_orders(self) -> list[BrokerOrder]:
        """Return all broker orders."""
        raise NotImplementedError
