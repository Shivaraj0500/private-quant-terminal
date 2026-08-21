from private_quant_terminal.brokers.order_status import OrderStatus


def test_order_status_values() -> None:
    assert OrderStatus.PENDING == "PENDING"
    assert OrderStatus.OPEN == "OPEN"
    assert OrderStatus.PARTIALLY_FILLED == "PARTIALLY_FILLED"
    assert OrderStatus.FILLED == "FILLED"
    assert OrderStatus.CANCELLED == "CANCELLED"
    assert OrderStatus.REJECTED == "REJECTED"
    assert OrderStatus.EXPIRED == "EXPIRED"
