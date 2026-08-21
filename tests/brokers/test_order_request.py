from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.brokers.time_in_force import TimeInForce


def test_order_request_with_time_in_force() -> None:
    request = OrderRequest(
        symbol="NIFTY",
        quantity=50,
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.IOC,
    )

    assert request.time_in_force == TimeInForce.IOC