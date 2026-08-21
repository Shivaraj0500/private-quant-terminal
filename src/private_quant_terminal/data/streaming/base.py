from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote
from private_quant_terminal.models.tick import Tick


class LiveMarketDataProvider(ABC):
    """Abstract interface for live market data providers."""

    @abstractmethod
    def subscribe_ticks(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Tick]:
        """Subscribe to live ticks."""
        raise NotImplementedError

    @abstractmethod
    def subscribe_quotes(
        self,
        symbols: list[str],
    ) -> AsyncIterator[Quote]:
        """Subscribe to live quotes."""
        raise NotImplementedError

    @abstractmethod
    def subscribe_market_depth(
        self,
        symbols: list[str],
    ) -> AsyncIterator[MarketDepth]:
        """Subscribe to live market depth."""
        raise NotImplementedError
