import pytest

from private_quant_terminal.data.providers.broker_adapter import BrokerAdapter


def test_broker_adapter_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerAdapter()
