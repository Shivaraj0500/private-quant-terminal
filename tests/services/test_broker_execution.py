from private_quant_terminal.brokers.execution import BrokerExecution
from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order import BrokerOrder
from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.services.broker_execution import BrokerExecutionService


class FakeBrokerExecution(BrokerExecution):
    def __init__(self) -> None:
        self.requests: list[OrderRequest] = []

    def place_order(self, request: OrderRequest) -> ExecutionReport:
        self.requests.append(request)

        return ExecutionReport(
            order_id=f"order-{len(self.requests)}",
            status=OrderStatus.FILLED,
            filled_quantity=request.quantity,
            remaining_quantity=0,
            average_price=None,
        )

    def modify_order(
        self,
        order_id: str,
        request: OrderRequest,
    ) -> ExecutionReport:
        return ExecutionReport(
            order_id=order_id,
            status=OrderStatus.OPEN,
            filled_quantity=0,
            remaining_quantity=request.quantity,
        )

    def cancel_order(self, order_id: str) -> ExecutionReport:
        return ExecutionReport(
            order_id=order_id,
            status=OrderStatus.CANCELLED,
            filled_quantity=0,
            remaining_quantity=0,
        )

    def get_order(self, order_id: str) -> BrokerOrder:
        raise KeyError(order_id)

    def get_orders(self) -> list[BrokerOrder]:
        return []


def make_order_request() -> OrderRequest:
    return OrderRequest(
        symbol="NIFTY",
        quantity=10,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )


def test_service_submits_executed_order_request() -> None:
    broker = FakeBrokerExecution()
    service = BrokerExecutionService(broker)

    request = make_order_request()

    result = ExecutionResult(
        signal_symbol="NIFTY",
        order_request=request,
        executed=True,
    )

    report = service.execute(result)

    assert report is not None
    assert report.order_id == "order-1"
    assert report.status is OrderStatus.FILLED
    assert report.filled_quantity == 10
    assert report.remaining_quantity == 0
    assert broker.requests == [request]


def test_service_does_not_submit_non_executed_result() -> None:
    broker = FakeBrokerExecution()
    service = BrokerExecutionService(broker)

    result = ExecutionResult(
        signal_symbol="NIFTY",
        order_request=None,
        executed=False,
        reason="Signal type HOLD does not create an order",
    )

    report = service.execute(result)

    assert report is None
    assert broker.requests == []


def test_service_does_not_submit_result_without_order_request() -> None:
    broker = FakeBrokerExecution()
    service = BrokerExecutionService(broker)

    result = ExecutionResult(
        signal_symbol="NIFTY",
        order_request=None,
        executed=True,
    )

    report = service.execute(result)

    assert report is None
    assert broker.requests == []
