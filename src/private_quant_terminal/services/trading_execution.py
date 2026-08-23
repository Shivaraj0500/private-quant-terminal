from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.risk.manager import RiskManager
from private_quant_terminal.services.broker_execution import (
    BrokerExecutionService,
)
from private_quant_terminal.services.trading_execution_result import (
    TradingExecutionResult,
)
from private_quant_terminal.strategies.signal import Signal


class TradingExecutionService:
    """Coordinate strategy execution, risk validation, and broker execution."""

    def __init__(
        self,
        execution_engine: ExecutionEngine,
        risk_manager: RiskManager,
        broker_execution_service: BrokerExecutionService,
    ) -> None:
        self._execution_engine = execution_engine
        self._risk_manager = risk_manager
        self._broker_execution_service = broker_execution_service

    def execute(self, signal: Signal) -> TradingExecutionResult:
        """Execute the complete trading workflow for a strategy signal."""
        execution_result = self._execution_engine.execute(signal)

        if (
            not execution_result.executed
            or execution_result.order_request is None
        ):
            return TradingExecutionResult(
                execution_result=execution_result,
                risk_result=None,
                execution_report=None,
                completed=False,
                reason=execution_result.reason,
            )

        risk_result = self._risk_manager.validate(
            execution_result.order_request
        )

        if not risk_result.approved:
            return TradingExecutionResult(
                execution_result=execution_result,
                risk_result=risk_result,
                execution_report=None,
                completed=False,
                reason=risk_result.reason,
            )

        execution_report = self._broker_execution_service.execute(
            execution_result
        )

        if execution_report is None:
            return TradingExecutionResult(
                execution_result=execution_result,
                risk_result=risk_result,
                execution_report=None,
                completed=False,
                reason="Broker execution did not return an execution report",
            )

        return TradingExecutionResult(
            execution_result=execution_result,
            risk_result=risk_result,
            execution_report=execution_report,
            completed=True,
        )
