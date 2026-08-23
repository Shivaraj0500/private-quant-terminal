import pytest

from private_quant_terminal.brokers.position import BrokerPosition


def test_broker_position_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerPosition()


def test_incomplete_broker_position_is_abstract() -> None:
    class IncompletePosition(BrokerPosition):
        @property
        def symbol(self) -> str:
            return "TEST"

    with pytest.raises(TypeError):
        IncompletePosition()


def test_complete_broker_position_can_be_instantiated() -> None:
    class CompletePosition(BrokerPosition):
        @property
        def symbol(self) -> str:
            return "TEST"

        @property
        def quantity(self) -> int:
            return 100

        @property
        def average_price(self) -> float:
            return 250.50

        @property
        def unrealized_pnl(self) -> float:
            return 1250.75

    position = CompletePosition()

    assert isinstance(position, BrokerPosition)
    assert position.symbol == "TEST"
    assert position.quantity == 100
    assert position.average_price == 250.50
    assert position.unrealized_pnl == 1250.75


def test_abstract_symbol_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerPosition.symbol.fget(None)


def test_abstract_quantity_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerPosition.quantity.fget(None)


def test_abstract_average_price_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerPosition.average_price.fget(None)


def test_abstract_unrealized_pnl_body_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BrokerPosition.unrealized_pnl.fget(None)