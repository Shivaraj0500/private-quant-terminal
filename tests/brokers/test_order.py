import pytest

from private_quant_terminal.brokers.order import BrokerOrder


def test_broker_order_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerOrder()
