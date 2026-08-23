import pytest

from private_quant_terminal.brokers.base import Broker
from private_quant_terminal.strategies.signal import Signal


def test_broker_base_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Broker()


def test_incomplete_broker_cannot_be_instantiated() -> None:
    class IncompleteBroker(Broker):
        @property
        def name(self) -> str:
            return "incomplete"

    with pytest.raises(TypeError):
        IncompleteBroker()


def test_concrete_broker_can_be_instantiated() -> None:
    class DummyBroker(Broker):
        @property
        def name(self) -> str:
            return "dummy"

        def execute_signal(self, signal: Signal) -> None:
            return None

    broker = DummyBroker()

    assert isinstance(broker, Broker)
    assert broker.name == "dummy"


def test_broker_implements_execute_signal() -> None:
    class DummyBroker(Broker):
        def __init__(self) -> None:
            self.received_signal: Signal | None = None

        @property
        def name(self) -> str:
            return "dummy"

        def execute_signal(self, signal: Signal) -> None:
            self.received_signal = signal

    broker = DummyBroker()

    assert broker.received_signal is None


def test_broker_name_abstract_property_raises_not_implemented() -> None:
    class ConcreteBroker(Broker):
        @property
        def name(self) -> str:
            return Broker.name.fget(self)

        def execute_signal(self, signal: Signal) -> None:
            return None

    broker = ConcreteBroker()

    with pytest.raises(NotImplementedError):
        _ = broker.name


def test_broker_execute_signal_base_method_raises_not_implemented() -> None:
    class ConcreteBroker(Broker):
        @property
        def name(self) -> str:
            return "concrete"

        def execute_signal(self, signal: Signal) -> None:
            Broker.execute_signal(self, signal)

    broker = ConcreteBroker()

    with pytest.raises(NotImplementedError):
        broker.execute_signal(None)