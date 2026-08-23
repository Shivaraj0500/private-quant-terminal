import pytest

from private_quant_terminal.brokers.order_side import OrderSide


def test_order_side_values() -> None:
    assert OrderSide.BUY == "BUY"
    assert OrderSide.SELL == "SELL"


def test_order_side_member_values() -> None:
    assert OrderSide.BUY.value == "BUY"
    assert OrderSide.SELL.value == "SELL"


def test_order_side_members_are_distinct() -> None:
    assert OrderSide.BUY != OrderSide.SELL


def test_order_side_can_be_created_from_valid_value() -> None:
    assert OrderSide("BUY") is OrderSide.BUY
    assert OrderSide("SELL") is OrderSide.SELL


def test_order_side_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        OrderSide("INVALID")