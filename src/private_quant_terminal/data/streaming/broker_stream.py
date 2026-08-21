from abc import abstractmethod
from collections.abc import AsyncIterator

from private_quant_terminal.data.streaming.base import LiveMarketDataProvider
from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote
from private_quant_terminal.models.tick import Tick


class BrokerStreamProvider(LiveMarketDataProvider):
    """Base interface for broker-backed live market data streams."""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the broker's streaming service."""
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the broker's streaming service."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return whether the streaming connection is active."""
        raise NotImplementedError

    @abstractmethod
    async def subscribe_ticks(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Tick]:
        """Subscribe to live ticks."""
        raise NotImplementedError

    @abstractmethod
    async def subscribe_quotes(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Quote]:
        """Subscribe to live quotes."""
        raise NotImplementedError

    @abstractmethod
    async def subscribe_market_depth(
        self,
        symbols: list[str],
    ) -> AsyncIterator[MarketDepth]:
        """Subscribe to live market depth."""
        raise NotImplementedError
