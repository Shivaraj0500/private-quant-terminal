import pytest

from private_quant_terminal.brokers.order_status import OrderStatus


def test_order_status_values() -> None:
    assert OrderStatus.PENDING == "PENDING"
    assert OrderStatus.OPEN == "OPEN"
    assert OrderStatus.PARTIALLY_FILLED == "PARTIALLY_FILLED"
    assert OrderStatus.FILLED == "FILLED"
    assert OrderStatus.CANCELLED == "CANCELLED"
    assert OrderStatus.REJECTED == "REJECTED"
    assert OrderStatus.EXPIRED == "EXPIRED"


def test_order_status_member_values() -> None:
    assert OrderStatus.PENDING.value == "PENDING"
    assert OrderStatus.OPEN.value == "OPEN"
    assert OrderStatus.PARTIALLY_FILLED.value == "PARTIALLY_FILLED"
    assert OrderStatus.FILLED.value == "FILLED"
    assert OrderStatus.CANCELLED.value == "CANCELLED"
    assert OrderStatus.REJECTED.value == "REJECTED"
    assert OrderStatus.EXPIRED.value == "EXPIRED"


def test_order_status_can_be_created_from_valid_value() -> None:
    assert OrderStatus("PENDING") is OrderStatus.PENDING
    assert OrderStatus("OPEN") is OrderStatus.OPEN
    assert (
        OrderStatus("PARTIALLY_FILLED")
        is OrderStatus.PARTIALLY_FILLED
    )
    assert OrderStatus("FILLED") is OrderStatus.FILLED
    assert OrderStatus("CANCELLED") is OrderStatus.CANCELLED
    assert OrderStatus("REJECTED") is OrderStatus.REJECTED
    assert OrderStatus("EXPIRED") is OrderStatus.EXPIRED


def test_order_status_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        OrderStatus("INVALID")


def test_order_status_members_are_distinct() -> None:
    members = list(OrderStatus)

    assert len(members) == 7
    assert len(set(members)) == 7