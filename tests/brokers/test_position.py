import pytest

from private_quant_terminal.brokers.position import BrokerPosition


def test_broker_position_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerPosition()
