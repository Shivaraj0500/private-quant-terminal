import pytest

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.risk.result import RiskResult
from private_quant_terminal.services.trading_execution_result import (
    TradingExecutionResult,
)
from private_quant_terminal.services.trading_workflow_result import (
    TradingWorkflowResult,
)


class TestTradingWorkflowResult:
    def test_creates_approved_workflow_result(self) -> None:
        order_request = OrderRequest(
            symbol="NIFTY",
            quantity=50,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        )

        risk_result = RiskResult(
            approved=True,
            reason=None,
        )

        trading_execution_result = TradingExecutionResult(
            execution_result=ExecutionResult(
                signal_symbol="NIFTY",
                order_request=order_request,
                executed=True,
                reason=None,
            ),
            risk_result=risk_result,
            execution_report=ExecutionReport(
                order_id="ORDER-1",
                status=OrderStatus.FILLED,
                filled_quantity=50,
                remaining_quantity=0,
                average_price=22000.0,
            ),
            completed=True,
            reason=None,
        )

        position = Position(
            symbol="NIFTY",
            quantity=50,
            average_price=22000.0,
        )

        result = TradingWorkflowResult(
            risk_result=risk_result,
            execution_result=trading_execution_result,
            position=position,
        )

        assert result.risk_result is risk_result
        assert result.execution_result is trading_execution_result
        assert result.position is position

    def test_creates_rejected_workflow_result(self) -> None:
        risk_result = RiskResult(
            approved=False,
            reason="Maximum order quantity exceeded",
        )

        result = TradingWorkflowResult(
            risk_result=risk_result,
            execution_result=None,
            position=None,
        )

        assert result.risk_result is risk_result
        assert result.execution_result is None
        assert result.position is None

    def test_is_immutable(self) -> None:
        result = TradingWorkflowResult(
            risk_result=RiskResult(
                approved=False,
                reason="Rejected",
            ),
            execution_result=None,
            position=None,
        )

        with pytest.raises(AttributeError):
            result.position = Position(
                symbol="NIFTY",
                quantity=50,
                average_price=22000.0,
            )