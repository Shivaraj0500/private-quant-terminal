import pytest

from private_quant_terminal.brokers.order_side import OrderSide


def test_order_side_buy_exists() -> None:
    assert OrderSide.BUY.value == "BUY"


def test_order_side_sell_exists() -> None:
    assert OrderSide.SELL.value == "SELL"


def test_order_side_members_are_distinct() -> None:
    assert OrderSide.BUY != OrderSide.SELL