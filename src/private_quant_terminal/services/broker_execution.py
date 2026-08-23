"""Broker execution application service."""

from private_quant_terminal.brokers.execution import BrokerExecution
from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.execution.result import ExecutionResult


class BrokerExecutionService:
    """Submit executable order requests through a broker."""

    def __init__(self, broker_execution: BrokerExecution) -> None:
        """Initialize the broker execution service."""
        self._broker_execution = broker_execution

    def execute(self, result: ExecutionResult) -> ExecutionReport | None:
        """Submit an execution result when it contains an order request."""
        if not result.executed or result.order_request is None:
            return None

        return self._broker_execution.place_order(result.order_request)
