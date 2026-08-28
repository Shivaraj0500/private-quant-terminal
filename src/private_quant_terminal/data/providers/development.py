from datetime import datetime, timezone

from private_quant_terminal.data.providers.broker_base import (
    BrokerMarketDataProvider,
)
from private_quant_terminal.models.market_depth import (
    MarketDepth,
    MarketDepthLevel,
)
from private_quant_terminal.models.quote import Quote


class DevelopmentMarketDataProvider(BrokerMarketDataProvider):
    """Development provider with deterministic sample market data."""

    def __init__(self) -> None:
        self._quotes: dict[str, dict[str, float | str]] = {
            "RELIANCE": {
                "exchange": "NSE",
                "last_price": 2985.40,
                "open": 2962.00,
                "high": 3004.80,
                "low": 2954.15,
                "previous_close": 2958.30,
                "volume": 2456789.0,
            },
            "TCS": {
                "exchange": "NSE",
                "last_price": 4128.75,
                "open": 4105.00,
                "high": 4142.90,
                "low": 4098.40,
                "previous_close": 4092.20,
                "volume": 1234567.0,
            },
            "HDFCBANK": {
                "exchange": "NSE",
                "last_price": 1687.90,
                "open": 1702.40,
                "high": 1708.10,
                "low": 1682.30,
                "previous_close": 1700.35,
                "volume": 6912345.0,
            },
            "INFY": {
                "exchange": "NSE",
                "last_price": 1874.60,
                "open": 1859.50,
                "high": 1882.40,
                "low": 1854.10,
                "previous_close": 1857.80,
                "volume": 3567890.0,
            },
            "ICICIBANK": {
                "exchange": "NSE",
                "last_price": 1234.80,
                "open": 1225.50,
                "high": 1238.40,
                "low": 1222.10,
                "previous_close": 1225.20,
                "volume": 7854321.0,
            },
            "SBIN": {
                "exchange": "NSE",
                "last_price": 812.65,
                "open": 820.10,
                "high": 823.50,
                "low": 808.30,
                "previous_close": 819.45,
                "volume": 8445678.0,
            },
            "ITC": {
                "exchange": "NSE",
                "last_price": 468.20,
                "open": 465.50,
                "high": 470.20,
                "low": 463.85,
                "previous_close": 465.05,
                "volume": 6234567.0,
            },
            "LT": {
                "exchange": "NSE",
                "last_price": 3520.40,
                "open": 3482.00,
                "high": 3534.90,
                "low": 3476.60,
                "previous_close": 3478.60,
                "volume": 2165432.0,
            },
            "NIFTY": {
                "exchange": "NSE",
                "last_price": 22458.30,
                "open": 22385.20,
                "high": 22510.75,
                "low": 22342.60,
                "previous_close": 22396.10,
                "volume": 0.0,
            },
        }

    def get_quote(self, symbol: str) -> Quote:
        """Return a development quote for a supported symbol."""
        normalized_symbol = symbol.upper()
        data = self._quotes.get(normalized_symbol)

        if data is None:
            raise ValueError(
                f"No development market data configured for {normalized_symbol}"
            )

        return Quote(
            symbol=normalized_symbol,
            exchange=str(data["exchange"]),
            timestamp=datetime.now(timezone.utc),
            last_price=float(data["last_price"]),
            open=float(data["open"]),
            high=float(data["high"]),
            low=float(data["low"]),
            previous_close=float(data["previous_close"]),
            volume=float(data["volume"]),
        )

    def get_market_depth(self, symbol: str) -> MarketDepth:
        """Return synthetic market depth around the latest price."""
        quote = self.get_quote(symbol)
        tick_size = 0.05

        bids = tuple(
            MarketDepthLevel(
                price=round(quote.last_price - tick_size * level, 2),
                quantity=float(100 * level),
                orders=level,
            )
            for level in range(1, 6)
        )

        asks = tuple(
            MarketDepthLevel(
                price=round(quote.last_price + tick_size * level, 2),
                quantity=float(100 * level),
                orders=level,
            )
            for level in range(1, 6)
        )

        return MarketDepth(
            symbol=quote.symbol,
            exchange=quote.exchange,
            bids=bids,
            asks=asks,
        )

    def stream_ticks(self, symbols: list[str]) -> None:
        """Placeholder for the development provider."""
        return None
