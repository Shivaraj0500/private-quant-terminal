import pytest

from private_quant_terminal.brokers.base import Broker
from private_quant_terminal.strategies.signal import Signal


class DummyBroker(Broker):
    @property
    def name(self) -> str:
        return "dummy"

    def execute_signal(self, signal: Signal) -> None:
        pass


def test_broker_base_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Broker()


def test_concrete_broker_can_be_instantiated() -> None:
    broker = DummyBroker()

    assert broker.name == "dummy"


def test_broker_implements_execute_signal() -> None:
    broker = DummyBroker()

    assert callable(broker.execute_signal)