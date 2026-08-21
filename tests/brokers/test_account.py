import pytest

from private_quant_terminal.brokers.account import BrokerAccount


def test_broker_account_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerAccount()
