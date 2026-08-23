from unittest.mock import Mock

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.risk.manager import RiskManager
from private_quant_terminal.risk.result import RiskResult
from private_quant_terminal.services.broker_execution import (
    BrokerExecutionService,
)
from private_quant_terminal.services.trading_execution import (
    TradingExecutionService,
)
from private_quant_terminal.strategies.signal import Signal, SignalType


class TestTradingExecutionService:
    def test_hold_signal_does_not_run_risk_or_broker_execution(self) -> None:
        execution_engine = Mock()
        execution_engine.execute.return_value = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="Signal type HOLD does not create an order",
        )

        risk_manager = Mock()
        broker_execution_service = Mock()

        service = TradingExecutionService(
            execution_engine=execution_engine,
            risk_manager=risk_manager,
            broker_execution_service=broker_execution_service,
        )

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.HOLD,
        )

        result = service.execute(signal)

        assert result.completed is False
        assert result.risk_result is None
        assert result.execution_report is None
        assert result.reason == "Signal type HOLD does not create an order"

        execution_engine.execute.assert_called_once_with(signal)
        risk_manager.validate.assert_not_called()
        broker_execution_service.execute.assert_not_called()

    def test_risk_rejection_does_not_run_broker_execution(self) -> None:
        execution_engine = Mock()
        engine = ExecutionEngine(quantity=10)

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
        )

        execution_result = engine.execute(signal)
        execution_engine.execute.return_value = execution_result

        risk_manager = Mock()
        risk_result = RiskResult(
            approved=False,
            reason="Order would exceed configured maximum position quantity",
        )
        risk_manager.validate.return_value = risk_result

        broker_execution_service = Mock()

        service = TradingExecutionService(
            execution_engine=execution_engine,
            risk_manager=risk_manager,
            broker_execution_service=broker_execution_service,
        )

        result = service.execute(signal)

        assert result.execution_result is execution_result
        assert result.risk_result is risk_result
        assert result.execution_report is None
        assert result.completed is False
        assert (
            result.reason
            == "Order would exceed configured maximum position quantity"
        )

        execution_engine.execute.assert_called_once_with(signal)
        risk_manager.validate.assert_called_once_with(
            execution_result.order_request
        )
        broker_execution_service.execute.assert_not_called()

    def test_approved_order_is_sent_to_broker(self) -> None:
        execution_engine = Mock()
        engine = ExecutionEngine(quantity=10)

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
        )

        execution_result = engine.execute(signal)
        execution_engine.execute.return_value = execution_result

        risk_manager = Mock()
        risk_result = RiskResult(approved=True)
        risk_manager.validate.return_value = risk_result

        broker_execution_service = Mock()
        execution_report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=22000.0,
        )
        broker_execution_service.execute.return_value = execution_report

        service = TradingExecutionService(
            execution_engine=execution_engine,
            risk_manager=risk_manager,
            broker_execution_service=broker_execution_service,
        )

        result = service.execute(signal)

        assert result.execution_result is execution_result
        assert result.risk_result is risk_result
        assert result.execution_report is execution_report
        assert result.completed is True
        assert result.reason is None

        execution_engine.execute.assert_called_once_with(signal)
        risk_manager.validate.assert_called_once_with(
            execution_result.order_request
        )
        broker_execution_service.execute.assert_called_once_with(
            execution_result
        )

    def test_approved_sell_order_is_sent_to_broker(self) -> None:
        execution_engine = Mock()
        engine = ExecutionEngine(quantity=5)

        signal = Signal(
            symbol="RELIANCE",
            signal_type=SignalType.SELL,
        )

        execution_result = engine.execute(signal)
        execution_engine.execute.return_value = execution_result

        risk_manager = Mock()
        risk_result = RiskResult(approved=True)
        risk_manager.validate.return_value = risk_result

        broker_execution_service = Mock()
        execution_report = ExecutionReport(
            order_id="ORDER-2",
            status=OrderStatus.FILLED,
            filled_quantity=5,
            remaining_quantity=0,
            average_price=3000.0,
        )
        broker_execution_service.execute.return_value = execution_report

        service = TradingExecutionService(
            execution_engine=execution_engine,
            risk_manager=risk_manager,
            broker_execution_service=broker_execution_service,
        )

        result = service.execute(signal)

        assert result.completed is True
        assert result.execution_report is execution_report
        assert result.reason is None

        risk_manager.validate.assert_called_once_with(
            execution_result.order_request
        )
        broker_execution_service.execute.assert_called_once_with(
            execution_result
        )

    def test_missing_broker_report_marks_execution_incomplete(self) -> None:
        execution_engine = Mock()
        engine = ExecutionEngine(quantity=10)

        signal = Signal(
            symbol="TCS",
            signal_type=SignalType.BUY,
        )

        execution_result = engine.execute(signal)
        execution_engine.execute.return_value = execution_result

        risk_manager = Mock()
        risk_manager.validate.return_value = RiskResult(
            approved=True
        )

        broker_execution_service = Mock()
        broker_execution_service.execute.return_value = None

        service = TradingExecutionService(
            execution_engine=execution_engine,
            risk_manager=risk_manager,
            broker_execution_service=broker_execution_service,
        )

        result = service.execute(signal)

        assert result.execution_result is execution_result
        assert result.risk_result is not None
        assert result.risk_result.approved is True
        assert result.execution_report is None
        assert result.completed is False
        assert (
            result.reason
            == "Broker execution did not return an execution report"
        )

        broker_execution_service.execute.assert_called_once_with(
            execution_result
        )
