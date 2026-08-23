import pytest

from private_quant_terminal.brokers.trade import BrokerTrade


def test_broker_trade_is_abstract() -> None:
    with pytest.raises(TypeError):
        BrokerTrade()


def test_incomplete_broker_trade_is_abstract() -> None:
    class IncompleteTrade(BrokerTrade):
        @property
        def trade_id(self) -> str:
            return "trade-001"

        @property
        def order_id(self) -> str:
            return "order-001"

        @property
        def symbol(self) -> str:
            return "NIFTY"

        @property
        def quantity(self) -> int:
            return 10

    with pytest.raises(TypeError):
        IncompleteTrade()


def test_complete_broker_trade_can_be_instantiated() -> None:
    class CompleteTrade(BrokerTrade):
        @property
        def trade_id(self) -> str:
            return "trade-001"

        @property
        def order_id(self) -> str:
            return "order-001"

        @property
        def symbol(self) -> str:
            return "NIFTY"

        @property
        def quantity(self) -> int:
            return 10

        @property
        def price(self) -> float:
            return 22500.50

    trade = CompleteTrade()

    assert isinstance(trade, BrokerTrade)
    assert trade.trade_id == "trade-001"
    assert trade.order_id == "order-001"
    assert trade.symbol == "NIFTY"
    assert trade.quantity == 10
    assert trade.price == 22500.50


def test_broker_trade_abstract_properties_raise_not_implemented() -> None:
    class ConcreteTrade(BrokerTrade):
        @property
        def trade_id(self) -> str:
            return BrokerTrade.trade_id.fget(self)  # type: ignore[union-attr]

        @property
        def order_id(self) -> str:
            return BrokerTrade.order_id.fget(self)  # type: ignore[union-attr]

        @property
        def symbol(self) -> str:
            return BrokerTrade.symbol.fget(self)  # type: ignore[union-attr]

        @property
        def quantity(self) -> int:
            return BrokerTrade.quantity.fget(self)  # type: ignore[union-attr]

        @property
        def price(self) -> float:
            return BrokerTrade.price.fget(self)  # type: ignore[union-attr]

    trade = ConcreteTrade()

    with pytest.raises(NotImplementedError):
        _ = trade.trade_id

    with pytest.raises(NotImplementedError):
        _ = trade.order_id

    with pytest.raises(NotImplementedError):
        _ = trade.symbol

    with pytest.raises(NotImplementedError):
        _ = trade.quantity

    with pytest.raises(NotImplementedError):
        _ = trade.price