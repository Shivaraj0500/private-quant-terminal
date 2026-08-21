import pytest

from private_quant_terminal.brokers.session import BrokerSession


def test_broker_session_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerSession()
