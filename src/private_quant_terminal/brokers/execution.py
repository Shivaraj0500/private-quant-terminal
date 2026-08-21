from abc import ABC, abstractmethod


class BrokerExecution(ABC):
    """Abstract interface for broker order execution."""

    @abstractmethod
    def place_order(self) -> None:
        """Place an order."""
        raise NotImplementedError

    @abstractmethod
    def modify_order(self) -> None:
        """Modify an existing order."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self) -> None:
        """Cancel an existing order."""
        raise NotImplementedError

    @abstractmethod
    def get_order(self) -> None:
        """Return a specific order."""
        raise NotImplementedError

    @abstractmethod
    def get_orders(self) -> None:
        """Return broker orders."""
        raise NotImplementedError
