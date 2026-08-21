from abc import ABC, abstractmethod

from private_quant_terminal.models.market_depth import MarketDepth
from private_quant_terminal.models.quote import Quote


class BrokerMarketDataProvider(ABC):
    """Base interface for broker market data providers."""

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """Return the latest quote for a symbol."""
        raise NotImplementedError

    @abstractmethod
    def get_market_depth(self, symbol: str) -> MarketDepth:
        """Return market depth for a symbol."""
        raise NotImplementedError

    @abstractmethod
    def stream_ticks(self, symbols: list[str]) -> None:
        """Stream live ticks."""
        raise NotImplementedError
