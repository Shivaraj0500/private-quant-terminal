from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from private_quant_terminal.data.providers.yfinance import (
    YahooFinanceMarketDataProvider,
)
from private_quant_terminal.models.instrument import InstrumentType


def test_get_instrument_returns_instrument() -> None:
    provider = YahooFinanceMarketDataProvider()

    fake_ticker = MagicMock()
    fake_ticker.info = {
        "exchange": "NSE",
        "quoteType": "EQUITY",
    }

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ) as mock_ticker:
        instrument = provider.get_instrument("RELIANCE.NS")

    mock_ticker.assert_called_once_with("RELIANCE.NS")

    assert instrument.symbol == "RELIANCE.NS"
    assert instrument.exchange == "NSE"
    assert instrument.instrument_type is InstrumentType.EQUITY


def test_get_instrument_uses_default_exchange() -> None:
    provider = YahooFinanceMarketDataProvider()

    fake_ticker = MagicMock()
    fake_ticker.info = {
        "quoteType": "INDEX",
    }

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ):
        instrument = provider.get_instrument("^NSEI")

    assert instrument.symbol == "^NSEI"
    assert instrument.exchange == "UNKNOWN"
    assert instrument.instrument_type is InstrumentType.INDEX


@pytest.mark.parametrize(
    ("quote_type", "expected_type"),
    [
        ("EQUITY", InstrumentType.EQUITY),
        ("INDEX", InstrumentType.INDEX),
        ("FUTURE", InstrumentType.FUTURE),
        ("OPTION", InstrumentType.OPTION),
        ("UNKNOWN", InstrumentType.EQUITY),
        ("", InstrumentType.EQUITY),
    ],
)
def test_instrument_type_mapping(
    quote_type: str,
    expected_type: InstrumentType,
) -> None:
    result = YahooFinanceMarketDataProvider._instrument_type(
        {"quoteType": quote_type}
    )

    assert result is expected_type


def test_instrument_type_is_case_insensitive() -> None:
    result = YahooFinanceMarketDataProvider._instrument_type(
        {"quoteType": "equity"}
    )

    assert result is InstrumentType.EQUITY


@pytest.mark.parametrize(
    ("timeframe", "expected"),
    [
        ("1m", "1m"),
        ("2m", "2m"),
        ("5m", "5m"),
        ("15m", "15m"),
        ("30m", "30m"),
        ("60m", "60m"),
        ("1h", "1h"),
        ("90m", "90m"),
        ("1d", "1d"),
        ("5d", "5d"),
        ("1wk", "1wk"),
        ("1mo", "1mo"),
        ("3mo", "3mo"),
        (" 1D ", "1d"),
        (" 15M ", "15m"),
    ],
)
def test_normalize_timeframe(
    timeframe: str,
    expected: str,
) -> None:
    assert (
        YahooFinanceMarketDataProvider._normalize_timeframe(timeframe)
        == expected
    )


def test_normalize_timeframe_rejects_unsupported_value() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported timeframe: 10m",
    ):
        YahooFinanceMarketDataProvider._normalize_timeframe("10m")


@pytest.mark.parametrize(
    ("timeframe", "limit", "expected"),
    [
        ("1m", 10, "7d"),
        ("2m", 10, "7d"),
        ("5m", 10, "7d"),
        ("15m", 10, "60d"),
        ("30m", 10, "60d"),
        ("60m", 180, "60d"),
        ("60m", 181, "730d"),
        ("1h", 100, "60d"),
        ("1h", 181, "730d"),
        ("90m", 180, "60d"),
        ("90m", 181, "730d"),
        ("1d", 60, "3mo"),
        ("1d", 61, "1y"),
        ("1d", 365, "1y"),
        ("1d", 366, "2y"),
        ("1d", 730, "2y"),
        ("1d", 731, "5y"),
        ("1d", 1825, "5y"),
        ("1d", 1826, "max"),
        ("5d", 10, "max"),
        ("1wk", 52, "1y"),
        ("1wk", 53, "5y"),
        ("1wk", 260, "5y"),
        ("1wk", 261, "max"),
        ("1mo", 10, "max"),
        ("3mo", 10, "max"),
        (" 1D ", 10, "3mo"),
    ],
)
def test_period_for_limit(
    timeframe: str,
    limit: int,
    expected: str,
) -> None:
    assert (
        YahooFinanceMarketDataProvider._period_for_limit(
            timeframe,
            limit,
        )
        == expected
    )


@pytest.mark.parametrize("limit", [0, -1, -10])
def test_period_for_limit_rejects_non_positive_limit(
    limit: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="limit must be greater than zero",
    ):
        YahooFinanceMarketDataProvider._period_for_limit(
            "1d",
            limit,
        )


def test_period_for_limit_rejects_unsupported_timeframe() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported timeframe: 10m",
    ):
        YahooFinanceMarketDataProvider._period_for_limit(
            "10m",
            10,
        )


def test_normalize_timestamp_returns_datetime() -> None:
    timestamp = datetime(
        2026,
        1,
        1,
        9,
        15,
    )

    result = YahooFinanceMarketDataProvider._normalize_timestamp(
        timestamp
    )

    assert result == timestamp


def test_normalize_timestamp_removes_timezone() -> None:
    timestamp = datetime(
        2026,
        1,
        1,
        9,
        15,
        tzinfo=timezone.utc,
    )

    result = YahooFinanceMarketDataProvider._normalize_timestamp(
        timestamp
    )

    assert result == datetime(
        2026,
        1,
        1,
        9,
        15,
    )
    assert result.tzinfo is None


def test_normalize_timestamp_converts_pandas_timestamp() -> None:
    timestamp = pd.Timestamp(
        "2026-01-01 09:15:00",
        tz="UTC",
    )

    result = YahooFinanceMarketDataProvider._normalize_timestamp(
        timestamp
    )

    assert result == datetime(
        2026,
        1,
        1,
        9,
        15,
    )
    assert result.tzinfo is None


def test_get_candles_returns_empty_list_for_empty_data() -> None:
    provider = YahooFinanceMarketDataProvider()

    fake_ticker = MagicMock()
    fake_ticker.history.return_value = pd.DataFrame()

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ):
        candles = provider.get_candles(
            symbol="RELIANCE.NS",
            timeframe="1d",
            limit=10,
        )

    assert candles == []

    fake_ticker.history.assert_called_once_with(
        period="3mo",
        interval="1d",
        auto_adjust=False,
    )


def test_get_candles_returns_candle_objects() -> None:
    provider = YahooFinanceMarketDataProvider()

    index = pd.to_datetime(
        [
            "2026-01-01 09:15:00",
            "2026-01-02 09:15:00",
        ],
        utc=True,
    )

    data = pd.DataFrame(
        {
            "Open": [100.0, 110.0],
            "High": [120.0, 130.0],
            "Low": [90.0, 100.0],
            "Close": [115.0, 125.0],
            "Volume": [1000.0, 2000.0],
        },
        index=index,
    )

    fake_ticker = MagicMock()
    fake_ticker.history.return_value = data

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ):
        candles = provider.get_candles(
            symbol="RELIANCE.NS",
            timeframe="1d",
            limit=10,
        )

    assert len(candles) == 2

    first = candles[0]

    assert first.timestamp == datetime(
        2026,
        1,
        1,
        9,
        15,
    )
    assert first.timestamp.tzinfo is None
    assert first.open == 100.0
    assert first.high == 120.0
    assert first.low == 90.0
    assert first.close == 115.0
    assert first.volume == 1000.0

    second = candles[1]

    assert second.open == 110.0
    assert second.high == 130.0
    assert second.low == 100.0
    assert second.close == 125.0
    assert second.volume == 2000.0


def test_get_candles_respects_limit() -> None:
    provider = YahooFinanceMarketDataProvider()

    index = pd.to_datetime(
        [
            "2026-01-01",
            "2026-01-02",
            "2026-01-03",
        ]
    )

    data = pd.DataFrame(
        {
            "Open": [100.0, 110.0, 120.0],
            "High": [120.0, 130.0, 140.0],
            "Low": [90.0, 100.0, 110.0],
            "Close": [115.0, 125.0, 135.0],
            "Volume": [1000.0, 2000.0, 3000.0],
        },
        index=index,
    )

    fake_ticker = MagicMock()
    fake_ticker.history.return_value = data

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ):
        candles = provider.get_candles(
            symbol="RELIANCE.NS",
            timeframe="1d",
            limit=2,
        )

    assert len(candles) == 2
    assert candles[0].open == 110.0
    assert candles[1].open == 120.0


def test_get_candles_uses_zero_volume_when_volume_column_is_missing() -> None:
    provider = YahooFinanceMarketDataProvider()

    index = pd.to_datetime(
        [
            "2026-01-01",
        ]
    )

    data = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [120.0],
            "Low": [90.0],
            "Close": [115.0],
        },
        index=index,
    )

    fake_ticker = MagicMock()
    fake_ticker.history.return_value = data

    with patch(
        "private_quant_terminal.data.providers.yfinance.yf.Ticker",
        return_value=fake_ticker,
    ):
        candles = provider.get_candles(
            symbol="RELIANCE.NS",
            timeframe="1d",
            limit=1,
        )

    assert len(candles) == 1
    assert candles[0].volume == 0.0