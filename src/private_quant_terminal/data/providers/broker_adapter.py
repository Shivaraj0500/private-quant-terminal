from abc import ABC, abstractmethod

from private_quant_terminal.data.providers.broker_base import BrokerMarketDataProvider
from private_quant_terminal.data.streaming.base import LiveMarketDataProvider


class BrokerAdapter(
    BrokerMarketDataProvider,
    LiveMarketDataProvider,
    ABC,
):
    """Unified interface for broker historical and live market data."""

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Return whether the broker session is authenticated."""
        raise NotImplementedError

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the broker."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the broker."""
        raise NotImplementedError
