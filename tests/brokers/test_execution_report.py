from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_status import OrderStatus


def test_execution_report_creation() -> None:
    report = ExecutionReport(
        order_id="ORDER-123",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    assert report.order_id == "ORDER-123"
    assert report.status == OrderStatus.FILLED
    assert report.filled_quantity == 10
    assert report.remaining_quantity == 0
    assert report.average_price == 250.50


def test_execution_report_without_average_price() -> None:
    report = ExecutionReport(
        order_id="ORDER-456",
        status=OrderStatus.OPEN,
        filled_quantity=0,
        remaining_quantity=10,
    )

    assert report.average_price is None
