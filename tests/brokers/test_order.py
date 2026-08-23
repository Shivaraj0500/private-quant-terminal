import pytest

from private_quant_terminal.brokers.order import BrokerOrder


def test_broker_order_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerOrder()


def test_incomplete_broker_order_is_abstract() -> None:
    class IncompleteOrder(BrokerOrder):
        @property
        def order_id(self) -> str:
            return "order-001"

        @property
        def symbol(self) -> str:
            return "NIFTY"

        @property
        def quantity(self) -> int:
            return 50

    with pytest.raises(TypeError):
        IncompleteOrder()


def test_complete_broker_order_can_be_instantiated() -> None:
    class CompleteOrder(BrokerOrder):
        @property
        def order_id(self) -> str:
            return "order-001"

        @property
        def symbol(self) -> str:
            return "NIFTY"

        @property
        def quantity(self) -> int:
            return 50

        @property
        def status(self) -> str:
            return "FILLED"

    order = CompleteOrder()

    assert isinstance(order, BrokerOrder)
    assert order.order_id == "order-001"
    assert order.symbol == "NIFTY"
    assert order.quantity == 50
    assert order.status == "FILLED"


def test_broker_order_abstract_properties_raise_not_implemented() -> None:
    class ConcreteOrder(BrokerOrder):
        @property
        def order_id(self) -> str:
            return BrokerOrder.order_id.fget(self)  # type: ignore[union-attr]

        @property
        def symbol(self) -> str:
            return BrokerOrder.symbol.fget(self)  # type: ignore[union-attr]

        @property
        def quantity(self) -> int:
            return BrokerOrder.quantity.fget(self)  # type: ignore[union-attr]

        @property
        def status(self) -> str:
            return BrokerOrder.status.fget(self)  # type: ignore[union-attr]

    order = ConcreteOrder()

    with pytest.raises(NotImplementedError):
        _ = order.order_id

    with pytest.raises(NotImplementedError):
        _ = order.symbol

    with pytest.raises(NotImplementedError):
        _ = order.quantity

    with pytest.raises(NotImplementedError):
        _ = order.status