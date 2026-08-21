import pytest

from private_quant_terminal.brokers.order_status import OrderStatus


def test_order_status_pending_exists() -> None:
    assert OrderStatus.PENDING.value == "PENDING"


def test_order_status_filled_exists() -> None:
    assert OrderStatus.FILLED.value == "FILLED"


def test_order_status_cancelled_exists() -> None:
    assert OrderStatus.CANCELLED.value == "CANCELLED"


def test_order_status_members_are_distinct() -> None:
    assert OrderStatus.PENDING != OrderStatus.FILLED
    assert OrderStatus.FILLED != OrderStatus.CANCELLED
    assert OrderStatus.PENDING != OrderStatus.CANCELLED