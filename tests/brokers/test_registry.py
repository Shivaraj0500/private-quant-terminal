import pytest

from private_quant_terminal.brokers.base import Broker
from private_quant_terminal.brokers.registry import BrokerRegistry


class FakeBroker(Broker):
    @property
    def name(self) -> str:
        return "fake"

    def account(self):
        raise NotImplementedError

    def session(self):
        raise NotImplementedError

    def get_positions(self):
        raise NotImplementedError

    def get_trades(self):
        raise NotImplementedError

    def get_orders(self):
        raise NotImplementedError


def test_register_and_get_broker() -> None:
    registry = BrokerRegistry()
    broker = FakeBroker()

    registry.register(broker)

    assert registry.get("fake") is broker


def test_get_unknown_broker_raises_key_error() -> None:
    registry = BrokerRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")