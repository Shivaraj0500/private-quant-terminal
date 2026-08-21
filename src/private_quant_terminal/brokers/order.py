from abc import ABC, abstractmethod


class BrokerOrder(ABC):
    @property
    @abstractmethod
    def order_id(self) -> str:
        """Return the broker order identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def symbol(self) -> str:
        """Return the trading symbol."""
        raise NotImplementedError

    @property
    @abstractmethod
    def quantity(self) -> int:
        """Return the order quantity."""
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> str:
        """Return the current order status."""
        raise NotImplementedError
