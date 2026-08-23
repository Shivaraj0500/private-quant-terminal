import pytest

from private_quant_terminal.brokers.execution import BrokerExecution


def test_broker_execution_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerExecution()


def test_incomplete_broker_execution_is_abstract() -> None:
    class IncompleteExecution(BrokerExecution):
        def place_order(self) -> None:
            return None

        def modify_order(self) -> None:
            return None

        def cancel_order(self) -> None:
            return None

        def get_order(self) -> None:
            return None

    with pytest.raises(TypeError):
        IncompleteExecution()


def test_complete_broker_execution_can_be_instantiated() -> None:
    class CompleteExecution(BrokerExecution):
        def __init__(self) -> None:
            self.actions: list[str] = []

        def place_order(self) -> None:
            self.actions.append("place_order")

        def modify_order(self) -> None:
            self.actions.append("modify_order")

        def cancel_order(self) -> None:
            self.actions.append("cancel_order")

        def get_order(self) -> None:
            self.actions.append("get_order")

        def get_orders(self) -> None:
            self.actions.append("get_orders")

    execution = CompleteExecution()

    assert isinstance(execution, BrokerExecution)

    execution.place_order()
    execution.modify_order()
    execution.cancel_order()
    execution.get_order()
    execution.get_orders()

    assert execution.actions == [
        "place_order",
        "modify_order",
        "cancel_order",
        "get_order",
        "get_orders",
    ]


def test_broker_execution_abstract_methods_raise_not_implemented() -> None:
    class ConcreteExecution(BrokerExecution):
        def place_order(self) -> None:
            BrokerExecution.place_order(self)

        def modify_order(self) -> None:
            BrokerExecution.modify_order(self)

        def cancel_order(self) -> None:
            BrokerExecution.cancel_order(self)

        def get_order(self) -> None:
            BrokerExecution.get_order(self)

        def get_orders(self) -> None:
            BrokerExecution.get_orders(self)

    execution = ConcreteExecution()

    with pytest.raises(NotImplementedError):
        execution.place_order()

    with pytest.raises(NotImplementedError):
        execution.modify_order()

    with pytest.raises(NotImplementedError):
        execution.cancel_order()

    with pytest.raises(NotImplementedError):
        execution.get_order()

    with pytest.raises(NotImplementedError):
        execution.get_orders()