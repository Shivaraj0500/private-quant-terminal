from datetime import datetime

import pytest

from private_quant_terminal.data.providers.memory import InMemoryMarketDataProvider
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import Instrument, InstrumentType


def create_instrument(
    symbol: str,
    exchange: str = "NSE",
) -> Instrument:
    """Create a valid Instrument for tests."""
    return Instrument(
        symbol=symbol,
        exchange=exchange,
        instrument_type=InstrumentType.INDEX,
    )


def test_add_and_get_instrument() -> None:
    provider = InMemoryMarketDataProvider()

    instrument = create_instrument("NIFTY")

    provider.add_instrument(instrument)

    result = provider.get_instrument("NIFTY")

    assert result == instrument
    assert result.symbol == "NIFTY"


def test_get_missing_instrument_returns_none() -> None:
    provider = InMemoryMarketDataProvider()

    result = provider.get_instrument("UNKNOWN")

    assert result is None


def test_add_instrument_replaces_existing_symbol() -> None:
    provider = InMemoryMarketDataProvider()

    first_instrument = create_instrument(
        symbol="NIFTY",
        exchange="NSE",
    )

    replacement_instrument = create_instrument(
        symbol="NIFTY",
        exchange="BSE",
    )

    provider.add_instrument(first_instrument)
    provider.add_instrument(replacement_instrument)

    result = provider.get_instrument("NIFTY")

    assert result == replacement_instrument
    assert result.exchange == "BSE"


def test_get_candles_returns_empty_list_for_unknown_symbol() -> None:
    provider = InMemoryMarketDataProvider()

    candles = provider.get_candles(
        symbol="UNKNOWN",
        timeframe="1m",
        limit=100,
    )

    assert candles == []


def test_add_and_get_candles() -> None:
    provider = InMemoryMarketDataProvider()

    candles = [
        Candle(
            timestamp=datetime(2026, 1, 1, 9, 15),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000.0,
        ),
        Candle(
            timestamp=datetime(2026, 1, 1, 9, 16),
            open=103.0,
            high=106.0,
            low=102.0,
            close=105.0,
            volume=1200.0,
        ),
    ]

    provider.add_candles(
        symbol="NIFTY",
        timeframe="1m",
        candles=candles,
    )

    result = provider.get_candles(
        symbol="NIFTY",
        timeframe="1m",
        limit=100,
    )

    assert result == candles


def test_get_candles_respects_limit() -> None:
    provider = InMemoryMarketDataProvider()

    candles = [
        Candle(
            timestamp=datetime(2026, 1, 1, 9, 15),
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.5,
            volume=1000.0,
        ),
        Candle(
            timestamp=datetime(2026, 1, 1, 9, 16),
            open=100.5,
            high=102.0,
            low=100.0,
            close=101.5,
            volume=1100.0,
        ),
        Candle(
            timestamp=datetime(2026, 1, 1, 9, 17),
            open=101.5,
            high=103.0,
            low=101.0,
            close=102.5,
            volume=1200.0,
        ),
    ]

    provider.add_candles(
        symbol="NIFTY",
        timeframe="1m",
        candles=candles,
    )

    result = provider.get_candles(
        symbol="NIFTY",
        timeframe="1m",
        limit=2,
    )

    assert result == candles[-2:]


def test_candles_are_stored_separately_by_timeframe() -> None:
    provider = InMemoryMarketDataProvider()

    candle_1m = Candle(
        timestamp=datetime(2026, 1, 1, 9, 15),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000.0,
    )

    candle_5m = Candle(
        timestamp=datetime(2026, 1, 1, 9, 15),
        open=200.0,
        high=210.0,
        low=195.0,
        close=205.0,
        volume=2000.0,
    )

    provider.add_candles(
        symbol="NIFTY",
        timeframe="1m",
        candles=[candle_1m],
    )

    provider.add_candles(
        symbol="NIFTY",
        timeframe="5m",
        candles=[candle_5m],
    )

    result_1m = provider.get_candles(
        symbol="NIFTY",
        timeframe="1m",
        limit=100,
    )

    result_5m = provider.get_candles(
        symbol="NIFTY",
        timeframe="5m",
        limit=100,
    )

    assert result_1m == [candle_1m]
    assert result_5m == [candle_5m]


def test_candles_are_stored_separately_by_symbol() -> None:
    provider = InMemoryMarketDataProvider()

    nifty_candle = Candle(
        timestamp=datetime(2026, 1, 1, 9, 15),
        open=100.0,
        high=105.0,
        low=99.0,
        close=103.0,
        volume=1000.0,
    )

    banknifty_candle = Candle(
        timestamp=datetime(2026, 1, 1, 9, 15),
        open=200.0,
        high=210.0,
        low=195.0,
        close=205.0,
        volume=2000.0,
    )

    provider.add_candles(
        symbol="NIFTY",
        timeframe="1m",
        candles=[nifty_candle],
    )

    provider.add_candles(
        symbol="BANKNIFTY",
        timeframe="1m",
        candles=[banknifty_candle],
    )

    nifty_result = provider.get_candles(
        symbol="NIFTY",
        timeframe="1m",
        limit=100,
    )

    banknifty_result = provider.get_candles(
        symbol="BANKNIFTY",
        timeframe="1m",
        limit=100,
    )

    assert nifty_result == [nifty_candle]
    assert banknifty_result == [banknifty_candle]