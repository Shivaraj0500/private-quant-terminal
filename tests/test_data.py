from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from private_quant_terminal.data import (
    CandleRepository,
    MarketTick,
    validate_candles,
)
from private_quant_terminal.models import Candle


def make_candle(
    timestamp: datetime,
    open_price: int = 100,
    high: int = 110,
    low: int = 95,
    close: int = 105,
    volume: int = 1000,
) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=Decimal(str(open_price)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=volume,
    )


def test_market_tick_creation() -> None:
    tick = MarketTick(
        symbol="NIFTY",
        timestamp=datetime.now(UTC),
        price=Decimal("25000.50"),
        volume=100,
    )

    assert tick.symbol == "NIFTY"
    assert tick.price == Decimal("25000.50")


def test_market_tick_rejects_invalid_price() -> None:
    with pytest.raises(ValueError):
        MarketTick(
            symbol="NIFTY",
            timestamp=datetime.now(UTC),
            price=Decimal(0),
        )


def test_validate_candles_accepts_ordered_data() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=15)),
    ]

    validate_candles(candles)


def test_validate_candles_rejects_empty_data() -> None:
    with pytest.raises(ValueError):
        validate_candles([])


def test_validate_candles_rejects_unordered_data() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)

    candles = [
        make_candle(start + timedelta(minutes=15)),
        make_candle(start),
    ]

    with pytest.raises(ValueError):
        validate_candles(candles)


def test_repository_save_and_get_all() -> None:
    repository = CandleRepository()
    start = datetime(2026, 1, 1, tzinfo=UTC)

    candles = [
        make_candle(start),
        make_candle(start + timedelta(minutes=15)),
    ]

    repository.save("NIFTY", candles)

    assert repository.get_all("NIFTY") == candles
    assert repository.latest("NIFTY") == candles[-1]


def test_repository_clear() -> None:
    repository = CandleRepository()
    start = datetime(2026, 1, 1, tzinfo=UTC)

    repository.save("NIFTY", [make_candle(start)])
    repository.clear("NIFTY")

    assert repository.get_all("NIFTY") == []
    assert repository.latest("NIFTY") is None
