from abc import ABC, abstractmethod


class BrokerAccount(ABC):
    """Base interface for broker account information."""

    @property
    @abstractmethod
    def account_id(self) -> str:
        """Return the broker account identifier."""
        raise NotImplementedError

    @abstractmethod
    def available_cash(self) -> float:
        """Return available cash in the account."""
        raise NotImplementedError

    @abstractmethod
    def used_margin(self) -> float:
        """Return currently used margin."""
        raise NotImplementedError

    @abstractmethod
    def available_margin(self) -> float:
        """Return currently available margin."""
        raise NotImplementedError
