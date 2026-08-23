import pytest

from private_quant_terminal.brokers.execution import BrokerExecution


def test_broker_execution_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BrokerExecution()


def test_place_order_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerExecution.place_order(None, None)


def test_modify_order_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerExecution.modify_order(None, "order-1", None)


def test_cancel_order_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerExecution.cancel_order(None, "order-1")


def test_get_order_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerExecution.get_order(None, "order-1")


def test_get_orders_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerExecution.get_orders(None)
