from abc import ABC, abstractmethod


class BrokerPosition(ABC):
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Return the trading symbol."""
        raise NotImplementedError

    @property
    @abstractmethod
    def quantity(self) -> int:
        """Return the current position quantity."""
        raise NotImplementedError

    @property
    @abstractmethod
    def average_price(self) -> float:
        """Return the average entry price."""
        raise NotImplementedError

    @property
    @abstractmethod
    def unrealized_pnl(self) -> float:
        """Return the unrealized profit or loss."""
        raise NotImplementedError
