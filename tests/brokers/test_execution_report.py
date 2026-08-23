from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_status import OrderStatus


def test_execution_report_stores_all_fields() -> None:
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


def test_execution_report_uses_none_as_default_average_price() -> None:
    report = ExecutionReport(
        order_id="ORDER-456",
        status=OrderStatus.OPEN,
        filled_quantity=0,
        remaining_quantity=10,
    )

    assert report.average_price is None


def test_execution_report_is_immutable() -> None:
    report = ExecutionReport(
        order_id="ORDER-123",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    with pytest.raises(FrozenInstanceError):
        report.filled_quantity = 20


def test_equal_execution_reports_are_equal() -> None:
    first = ExecutionReport(
        order_id="ORDER-123",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    second = ExecutionReport(
        order_id="ORDER-123",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    assert first == second


def test_different_execution_reports_are_not_equal() -> None:
    first = ExecutionReport(
        order_id="ORDER-123",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    second = ExecutionReport(
        order_id="ORDER-124",
        status=OrderStatus.FILLED,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=250.50,
    )

    assert first != second