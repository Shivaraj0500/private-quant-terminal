from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.brokers.time_in_force import TimeInForce


def test_order_request_stores_all_fields() -> None:
    request = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.IOC,
    )

    assert request.symbol == "NIFTY"
    assert request.quantity == 50
    assert request.side == OrderSide.SELL
    assert request.order_type == OrderType.LIMIT
    assert request.time_in_force == TimeInForce.IOC


def test_order_request_uses_day_as_default_time_in_force() -> None:
    request = OrderRequest(
        symbol="BANKNIFTY",
        quantity=25,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    assert request.time_in_force == TimeInForce.DAY


def test_order_request_is_immutable() -> None:
    request = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    with pytest.raises(FrozenInstanceError):
        request.quantity = 100


def test_equal_order_requests_are_equal() -> None:
    first = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    second = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    assert first == second


def test_different_order_requests_are_not_equal() -> None:
    first = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    second = OrderRequest(
        symbol="NIFTY",
        quantity=25,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
    )

    assert first != second