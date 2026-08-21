from abc import ABC, abstractmethod


class BrokerSession(ABC):
    """Base interface for broker authentication sessions."""

    @property
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Return whether the session is authenticated."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate the broker session."""
        raise NotImplementedError

    @abstractmethod
    def logout(self) -> None:
        """Terminate the broker session."""
        raise NotImplementedError
