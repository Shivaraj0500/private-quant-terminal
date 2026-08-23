from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.risk.result import RiskResult
from private_quant_terminal.services.trading_execution_result import (
    TradingExecutionResult,
)
from private_quant_terminal.services.trading_workflow import (
    TradingWorkflowService,
)
from private_quant_terminal.services.trading_workflow_result import (
    TradingWorkflowResult,
)


class StubTradingExecutionService:
    def __init__(
        self,
        result: TradingExecutionResult,
    ) -> None:
        self.result = result
        self.calls: list[object] = []

    def execute(self, signal: object) -> TradingExecutionResult:
        self.calls.append(signal)
        return self.result


class TestTradingWorkflowService:
    def test_completes_workflow_and_updates_position(
        self,
    ) -> None:
        request = OrderRequest(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=50,
            order_type=OrderType.MARKET,
        )

        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=request,
            executed=True,
        )

        risk_result = RiskResult(
            approved=True,
        )

        report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=50,
            remaining_quantity=0,
            average_price=22000.0,
        )

        trading_result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=risk_result,
            execution_report=report,
            completed=True,
        )

        execution_service = StubTradingExecutionService(
            result=trading_result,
        )

        position_manager = PositionManager()

        service = TradingWorkflowService(
            trading_execution_service=execution_service,
            position_manager=position_manager,
        )

        signal = object()

        result = service.execute(signal)

        assert isinstance(result, TradingWorkflowResult)
        assert result.risk_result is risk_result
        assert result.execution_result is trading_result
        assert result.position is not None

        assert result.position.symbol == "NIFTY"
        assert result.position.quantity == 50
        assert result.position.average_price == 22000.0

        assert position_manager.get_position("NIFTY") == result.position
        assert execution_service.calls == [signal]

    def test_returns_execution_result_without_position_when_incomplete(
        self,
    ) -> None:
        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="No executable order",
        )

        trading_result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=None,
            execution_report=None,
            completed=False,
            reason="No executable order",
        )

        execution_service = StubTradingExecutionService(
            result=trading_result,
        )

        position_manager = PositionManager()

        service = TradingWorkflowService(
            trading_execution_service=execution_service,
            position_manager=position_manager,
        )

        result = service.execute(object())

        assert result.risk_result is None
        assert result.execution_result is trading_result
        assert result.position is None
        assert position_manager.positions() == ()

    def test_returns_no_position_when_execution_is_not_filled(
        self,
    ) -> None:
        request = OrderRequest(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=50,
            order_type=OrderType.MARKET,
        )

        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=request,
            executed=True,
        )

        risk_result = RiskResult(
            approved=True,
        )

        report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.REJECTED,
            filled_quantity=0,
            remaining_quantity=50,
            average_price=None,
        )

        trading_result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=risk_result,
            execution_report=report,
            completed=False,
            reason="Broker order was not filled",
        )

        execution_service = StubTradingExecutionService(
            result=trading_result,
        )

        position_manager = PositionManager()

        service = TradingWorkflowService(
            trading_execution_service=execution_service,
            position_manager=position_manager,
        )

        result = service.execute(object())

        assert result.risk_result is risk_result
        assert result.execution_result is trading_result
        assert result.position is None
        assert position_manager.positions() == ()

    def test_returns_no_position_when_completed_result_has_no_order_request(
        self,
    ) -> None:
        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=True,
        )

        risk_result = RiskResult(
            approved=True,
        )

        report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=50,
            remaining_quantity=0,
            average_price=22000.0,
        )

        trading_result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=risk_result,
            execution_report=report,
            completed=True,
        )

        execution_service = StubTradingExecutionService(
            result=trading_result,
        )

        position_manager = PositionManager()

        service = TradingWorkflowService(
            trading_execution_service=execution_service,
            position_manager=position_manager,
        )

        result = service.execute(object())

        assert result.risk_result is risk_result
        assert result.execution_result is trading_result
        assert result.position is None
        assert position_manager.positions() == ()