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
from private_quant_terminal.services.trading_workflow import (
    TradingWorkflowService,
)
from private_quant_terminal.strategies.signal import Signal, SignalType


def create_workflow(
    *,
    quantity: int = 10,
    max_position_quantity: int = 100,
    max_order_quantity: int = 100,
    max_open_positions: int = 10,
) -> tuple[TradingWorkflowService, PositionManager]:
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

    trading_execution_service = TradingExecutionService(
        execution_engine=execution_engine,
        risk_manager=risk_manager,
        broker_execution_service=broker_execution_service,
    )

    workflow = TradingWorkflowService(
        trading_execution_service=trading_execution_service,
        position_manager=position_manager,
    )

    return workflow, position_manager


class TestTradingWorkflowIntegration:
    def test_buy_signal_executes_and_creates_position(self) -> None:
        workflow, position_manager = create_workflow(
            quantity=50,
        )

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
            price=22000.0,
        )

        result = workflow.execute(signal)

        assert result.execution_result is not None
        assert result.execution_result.completed is True
        assert result.execution_result.reason is None

        assert result.risk_result is not None
        assert result.risk_result.approved is True

        assert result.position is not None
        assert result.position.symbol == "NIFTY"
        assert result.position.quantity == 50
        assert result.position.average_price == 22000.0

        stored_position = position_manager.get_position("NIFTY")

        assert stored_position == result.position

    def test_sell_signal_executes_and_creates_short_position(self) -> None:
        workflow, position_manager = create_workflow(
            quantity=25,
        )

        signal = Signal(
            symbol="RELIANCE",
            signal_type=SignalType.SELL,
            price=3000.0,
        )

        result = workflow.execute(signal)

        assert result.execution_result is not None
        assert result.execution_result.completed is True

        assert result.risk_result is not None
        assert result.risk_result.approved is True

        assert result.position is not None
        assert result.position.symbol == "RELIANCE"
        assert result.position.quantity == -25
        assert result.position.average_price == 3000.0

        stored_position = position_manager.get_position("RELIANCE")

        assert stored_position == result.position

    def test_hold_signal_does_not_create_position(self) -> None:
        workflow, position_manager = create_workflow()

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.HOLD,
        )

        result = workflow.execute(signal)

        assert result.execution_result is not None
        assert result.execution_result.completed is False

        assert result.risk_result is None
        assert result.position is None

        assert (
            result.execution_result.reason
            == "Signal type HOLD does not create an order"
        )

        assert position_manager.positions() == ()

    def test_risk_rejection_does_not_create_position(self) -> None:
        workflow, position_manager = create_workflow(
            quantity=50,
            max_order_quantity=10,
        )

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
            price=22000.0,
        )

        result = workflow.execute(signal)

        assert result.execution_result is not None
        assert result.execution_result.completed is False

        assert result.risk_result is not None
        assert result.risk_result.approved is False

        assert result.position is None

        assert (
            result.execution_result.reason
            == "Order quantity exceeds configured maximum order quantity"
        )

        assert position_manager.positions() == ()
