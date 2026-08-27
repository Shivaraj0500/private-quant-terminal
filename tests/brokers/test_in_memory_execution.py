import pytest

from private_quant_terminal.brokers.in_memory_execution import (
    InMemoryBrokerExecution,
)
from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.brokers.order_type import OrderType


class TestInMemoryBrokerExecution:
    def test_fills_priced_order_immediately(self) -> None:
        broker = InMemoryBrokerExecution()

        request = OrderRequest(
            symbol="NIFTY",
            quantity=50,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price=22000.0,
        )

        result = broker.place_order(request)

        assert result.order_id == "ORDER-1"
        assert result.status is OrderStatus.FILLED
        assert result.filled_quantity == 50
        assert result.remaining_quantity == 0
        assert result.average_price == 22000.0

    def test_generates_sequential_order_ids(self) -> None:
        broker = InMemoryBrokerExecution()

        first_request = OrderRequest(
            symbol="NIFTY",
            quantity=50,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price=22000.0,
        )

        second_request = OrderRequest(
            symbol="BANKNIFTY",
            quantity=25,
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            price=48000.0,
        )

        first_result = broker.place_order(first_request)
        second_result = broker.place_order(second_request)

        assert first_result.order_id == "ORDER-1"
        assert second_result.order_id == "ORDER-2"

    def test_rejects_order_without_price(self) -> None:
        broker = InMemoryBrokerExecution()

        request = OrderRequest(
            symbol="NIFTY",
            quantity=50,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        )

        with pytest.raises(
            ValueError,
            match="in-memory broker execution requires an order price",
        ):
            broker.place_order(request)
