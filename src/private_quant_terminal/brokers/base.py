from abc import ABC, abstractmethod

from private_quant_terminal.brokers.account import BrokerAccount
from private_quant_terminal.brokers.order import BrokerOrder
from private_quant_terminal.brokers.position import BrokerPosition
from private_quant_terminal.brokers.session import BrokerSession
from private_quant_terminal.brokers.trade import BrokerTrade


class Broker(ABC):
    @property
    @abstractmethod
    def session(self) -> BrokerSession:
        """Return the broker session."""
        raise NotImplementedError

    @property
    @abstractmethod
    def account(self) -> BrokerAccount:
        """Return the broker account."""
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> tuple[BrokerPosition, ...]:
        """Return all current broker positions."""
        raise NotImplementedError

    @abstractmethod
    def get_orders(self) -> tuple[BrokerOrder, ...]:
        """Return all broker orders."""
        raise NotImplementedError

    @abstractmethod
    def get_trades(self) -> tuple[BrokerTrade, ...]:
        """Return all executed broker trades."""
        raise NotImplementedError
