import pytest

from private_quant_terminal.brokers.in_memory_execution import (
    InMemoryBrokerExecution,
)
from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.risk.limits import RiskLimits
from private_quant_terminal.risk.manager import RiskManager
from private_quant_terminal.services.broker_execution import (
    BrokerExecutionService,
)
from private_quant_terminal.services.trading_execution import (
    TradingExecutionService,
)
from private_quant_terminal.strategies.signal import Signal, SignalType


def create_service(
    *,
    quantity: int = 10,
    max_position_quantity: int = 100,
    max_order_quantity: int = 100,
    max_open_positions: int = 10,
) -> TradingExecutionService:
    position_manager = PositionManager()

    execution_engine = ExecutionEngine(
        quantity=quantity,
    )

    risk_manager = RiskManager(
        limits=RiskLimits(
            max_position_quantity=max_position_quantity,
            max_order_quantity=max_order_quantity,
            max_open_positions=max_open_positions,
            max_daily_loss=100000.0,
        ),
        position_manager=position_manager,
    )

    broker_execution_service = BrokerExecutionService(
        InMemoryBrokerExecution()
    )

    return TradingExecutionService(
        execution_engine=execution_engine,
        risk_manager=risk_manager,
        broker_execution_service=broker_execution_service,
    )


class TestTradingExecutionService:
    def test_completes_buy_execution(self) -> None:
        service = create_service()

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
            price=22000.0,
        )

        result = service.execute(signal)

        assert result.completed is True
        assert result.reason is None

        assert result.execution_result.executed is True
        assert result.execution_result.order_request is not None
        assert result.execution_result.order_request.symbol == "NIFTY"
        assert result.execution_result.order_request.price == 22000.0

        assert result.risk_result is not None
        assert result.risk_result.approved is True

        assert result.execution_report is not None
        assert result.execution_report.order_id == "ORDER-1"
        assert result.execution_report.filled_quantity == 10
        assert result.execution_report.remaining_quantity == 0
        assert result.execution_report.average_price == 22000.0

    def test_completes_sell_execution(self) -> None:
        service = create_service()

        signal = Signal(
            symbol="RELIANCE",
            signal_type=SignalType.SELL,
            price=3000.0,
        )

        result = service.execute(signal)

        assert result.completed is True
        assert result.reason is None

        assert result.execution_result.executed is True
        assert result.execution_result.order_request is not None
        assert result.execution_result.order_request.symbol == "RELIANCE"
        assert result.execution_result.order_request.price == 3000.0

        assert result.risk_result is not None
        assert result.risk_result.approved is True

        assert result.execution_report is not None
        assert result.execution_report.average_price == 3000.0

    def test_stops_when_signal_is_hold(self) -> None:
        service = create_service()

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.HOLD,
        )

        result = service.execute(signal)

        assert result.completed is False
        assert result.risk_result is None
        assert result.execution_report is None
        assert (
            result.reason
            == "Signal type HOLD does not create an order"
        )

    def test_stops_when_risk_rejects_order(self) -> None:
        service = create_service(
            quantity=10,
            max_order_quantity=5,
        )

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
            price=22000.0,
        )

        result = service.execute(signal)

        assert result.completed is False

        assert result.execution_result.executed is True
        assert result.execution_result.order_request is not None

        assert result.risk_result is not None
        assert result.risk_result.approved is False

        assert result.execution_report is None
        assert (
            result.reason
            == "Order quantity exceeds configured maximum order quantity"
        )