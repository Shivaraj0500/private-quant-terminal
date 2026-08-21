from datetime import datetime

import yfinance as yf

from private_quant_terminal.data.providers.base import MarketDataProvider
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import Instrument


class YahooFinanceMarketDataProvider(MarketDataProvider):
    """Market data provider backed by Yahoo Finance."""

    def get_instrument(self, symbol: str) -> Instrument:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return Instrument(
            symbol=symbol,
            exchange=info.get("exchange", "UNKNOWN"),
            instrument_type=self._instrument_type(info),
        )

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:
        interval = self._normalize_timeframe(timeframe)
        period = self._period_for_limit(timeframe, limit)

        ticker = yf.Ticker(symbol)

        data = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
        )

        if data.empty:
            return []

        candles = []

        for timestamp, row in data.tail(limit).iterrows():
            candles.append(
                Candle(
                    timestamp=self._normalize_timestamp(timestamp),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row.get("Volume", 0.0)),
                )
            )

        return candles

    @staticmethod
    def _normalize_timestamp(timestamp) -> datetime:
        """Convert pandas timestamps to timezone-naive Python datetimes."""
        if hasattr(timestamp, "to_pydatetime"):
            timestamp = timestamp.to_pydatetime()

        if timestamp.tzinfo is not None:
            timestamp = timestamp.replace(tzinfo=None)

        return timestamp

    @staticmethod
    def _normalize_timeframe(timeframe: str) -> str:
        """Convert application timeframes to Yahoo Finance intervals."""
        mapping = {
            "1m": "1m",
            "2m": "2m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "60m": "60m",
            "1h": "1h",
            "90m": "90m",
            "1d": "1d",
            "5d": "5d",
            "1wk": "1wk",
            "1mo": "1mo",
            "3mo": "3mo",
        }

        normalized = timeframe.lower().strip()

        if normalized not in mapping:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}. "
                f"Supported timeframes: {', '.join(mapping.keys())}"
            )

        return mapping[normalized]

    @staticmethod
    def _period_for_limit(timeframe: str, limit: int) -> str:
        """Choose a Yahoo Finance history period appropriate for the request."""
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        timeframe = timeframe.lower().strip()

        if timeframe in {"1m", "2m", "5m"}:
            return "7d"

        if timeframe in {"15m", "30m"}:
            return "60d"

        if timeframe in {"60m", "1h", "90m"}:
            if limit <= 180:
                return "60d"
            return "730d"

        if timeframe == "1d":
            if limit <= 60:
                return "3mo"
            if limit <= 365:
                return "1y"
            if limit <= 730:
                return "2y"
            if limit <= 1825:
                return "5y"
            return "max"

        if timeframe == "5d":
            return "max"

        if timeframe == "1wk":
            if limit <= 52:
                return "1y"
            if limit <= 260:
                return "5y"
            return "max"

        if timeframe in {"1mo", "3mo"}:
            return "max"

        raise ValueError(f"Unsupported timeframe: {timeframe}")

    @staticmethod
    def _instrument_type(info: dict):
        """Map Yahoo Finance quote metadata to the application's instrument type."""
        quote_type = str(info.get("quoteType", "")).upper()

        from private_quant_terminal.models.instrument import InstrumentType

        mapping = {
            "EQUITY": InstrumentType.EQUITY,
            "INDEX": InstrumentType.INDEX,
            "FUTURE": InstrumentType.FUTURE,
            "OPTION": InstrumentType.OPTION,
        }

        return mapping.get(quote_type, InstrumentType.EQUITY)
