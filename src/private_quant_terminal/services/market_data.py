"""Market data application service."""

from collections.abc import Sequence

from private_quant_terminal.data.providers.broker_base import BrokerMarketDataProvider
from private_quant_terminal.data.repository import CandleRepository
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.tick import Tick


class MarketDataService:
    """Coordinates market data providers, repositories, and live updates."""

    def __init__(
        self,
        provider: BrokerMarketDataProvider,
        candle_repository: CandleRepository,
    ) -> None:
        """Initialize the market data service."""
        self._provider = provider
        self._candle_repository = candle_repository
        self._latest_ticks: dict[str, Tick] = {}

    def get_latest_tick(self, symbol: str) -> Tick:
        """Return the latest market tick from the provider."""
        return self._provider.get_quote(symbol)

    def get_candles(
        self,
        symbol: str,
        limit: int | None = None,
    ) -> Sequence[Candle]:
        """Return cached candles for a symbol."""
        candles = self._candle_repository.get_candles(symbol)

        if limit is not None:
            return tuple(candles[-limit:])

        return tuple(candles)

    def update_tick(self, tick: Tick) -> None:
        """Store the latest tick for its symbol."""
        self._latest_ticks[tick.symbol] = tick

    def latest_tick(self, symbol: str) -> Tick | None:
        """Return the cached latest tick for a symbol."""
        return self._latest_ticks.get(symbol)

    def loaded_symbols(self) -> Sequence[str]:
        """Return symbols currently holding live tick data."""
        return tuple(self._latest_ticks)

    def clear_symbol(self, symbol: str) -> None:
        """Clear cached candles and the latest tick for a symbol."""
        self._candle_repository.clear(symbol)
        self._latest_ticks.pop(symbol, None)