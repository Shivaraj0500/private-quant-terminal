import pytest

from private_quant_terminal.brokers.base import Broker


def test_broker_is_abstract() -> None:
    with pytest.raises(TypeError):
        Broker()
