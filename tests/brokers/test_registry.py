import pytest

from private_quant_terminal.brokers.registry import BrokerRegistry


class DummyBroker:
    pass


def test_broker_registry_registers_broker() -> None:
    registry = BrokerRegistry()
    broker = DummyBroker()

    registry.register("zerodha", broker)

    assert registry.get("zerodha") is broker


def test_broker_registry_rejects_duplicate_name() -> None:
    registry = BrokerRegistry()

    registry.register("zerodha", DummyBroker())

    with pytest.raises(ValueError):
        registry.register("zerodha", DummyBroker())


def test_broker_registry_returns_registered_names() -> None:
    registry = BrokerRegistry()

    registry.register("zerodha", DummyBroker())
    registry.register("angelone", DummyBroker())

    assert registry.names() == ["zerodha", "angelone"]


def test_broker_registry_rejects_unknown_broker() -> None:
    registry = BrokerRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_broker_registry_contains_registered_broker() -> None:
    registry = BrokerRegistry()

    registry.register("zerodha", DummyBroker())

    assert "zerodha" in registry


def test_broker_registry_does_not_contain_unknown_broker() -> None:
    registry = BrokerRegistry()

    assert "unknown" not in registry