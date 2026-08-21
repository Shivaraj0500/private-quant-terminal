import pytest

from private_quant_terminal.brokers.trade import BrokerTrade


def test_broker_trade_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerTrade()
