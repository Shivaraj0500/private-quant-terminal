import pytest

from private_quant_terminal.brokers.order_type import OrderType


def test_order_type_values() -> None:
    assert OrderType.MARKET == "MARKET"
    assert OrderType.LIMIT == "LIMIT"


def test_order_type_member_values() -> None:
    assert OrderType.MARKET.value == "MARKET"
    assert OrderType.LIMIT.value == "LIMIT"


def test_order_type_members_are_distinct() -> None:
    assert OrderType.MARKET != OrderType.LIMIT


def test_order_type_can_be_created_from_valid_value() -> None:
    assert OrderType("MARKET") is OrderType.MARKET
    assert OrderType("LIMIT") is OrderType.LIMIT


def test_order_type_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        OrderType("INVALID")