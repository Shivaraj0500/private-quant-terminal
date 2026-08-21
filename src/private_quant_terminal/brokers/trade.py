from abc import ABC, abstractmethod


class BrokerTrade(ABC):
    @property
    @abstractmethod
    def trade_id(self) -> str:
        """Return the broker trade identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def order_id(self) -> str:
        """Return the related broker order identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def symbol(self) -> str:
        """Return the trading symbol."""
        raise NotImplementedError

    @property
    @abstractmethod
    def quantity(self) -> int:
        """Return the executed quantity."""
        raise NotImplementedError

    @property
    @abstractmethod
    def price(self) -> float:
        """Return the execution price."""
        raise NotImplementedError
