from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.services.trading_execution import (
    TradingExecutionService,
)
from private_quant_terminal.services.trading_workflow_result import (
    TradingWorkflowResult,
)
from private_quant_terminal.strategies.signal import Signal


class TradingWorkflowService:
    """Coordinate trading execution and portfolio position updates."""

    def __init__(
        self,
        trading_execution_service: TradingExecutionService,
        position_manager: PositionManager,
    ) -> None:
        """Initialize the trading workflow service."""
        self._trading_execution_service = trading_execution_service
        self._position_manager = position_manager

    def execute(
        self,
        signal: Signal,
    ) -> TradingWorkflowResult:
        """Execute the complete trading workflow for a signal."""
        trading_execution_result = (
            self._trading_execution_service.execute(signal)
        )

        risk_result = trading_execution_result.risk_result

        if not trading_execution_result.completed:
            return TradingWorkflowResult(
                risk_result=risk_result,
                execution_result=trading_execution_result,
                position=None,
            )

        execution_result = (
            trading_execution_result.execution_result
        )
        execution_report = (
            trading_execution_result.execution_report
        )

        if (
            execution_result.order_request is None
            or execution_report is None
            or execution_report.average_price is None
        ):
            return TradingWorkflowResult(
                risk_result=risk_result,
                execution_result=trading_execution_result,
                position=None,
            )

        order_request = execution_result.order_request

        position = self._position_manager.apply_execution(
            symbol=order_request.symbol,
            side=order_request.side,
            quantity=execution_report.filled_quantity,
            price=execution_report.average_price,
            report=execution_report,
        )

        return TradingWorkflowResult(
            risk_result=risk_result,
            execution_result=trading_execution_result,
            position=position,
        )