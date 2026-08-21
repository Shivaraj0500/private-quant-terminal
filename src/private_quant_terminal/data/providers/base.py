from abc import ABC, abstractmethod

from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import Instrument


class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def get_instrument(self, symbol: str) -> Instrument:
        """Return instrument metadata for a symbol."""
        raise NotImplementedError

    @abstractmethod
    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:
        """Return historical OHLCV candles."""
        raise NotImplementedError
