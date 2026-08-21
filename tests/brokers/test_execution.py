import pytest

from private_quant_terminal.brokers.execution import BrokerExecution


def test_broker_execution_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerExecution()
