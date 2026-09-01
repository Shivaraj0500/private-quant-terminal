from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from private_quant_terminal.models.tick import Tick


class TestTick:
    def test_creates_tick_with_required_fields(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15, tzinfo=UTC)

        tick = Tick(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=timestamp,
            last_price=25000.0,
        )

        assert tick.symbol == "NIFTY"
        assert tick.exchange == "NSE"
        assert tick.timestamp == timestamp
        assert tick.last_price == 25000.0

    def test_optional_fields_default_to_none(self) -> None:
        tick = Tick(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15, tzinfo=UTC),
            last_price=25000.0,
        )

        assert tick.volume is None
        assert tick.bid is None
        assert tick.ask is None

    def test_creates_tick_with_all_fields(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15, tzinfo=UTC)

        tick = Tick(
            symbol="RELIANCE",
            exchange="NSE",
            timestamp=timestamp,
            last_price=1450.0,
            volume=1500000.0,
            bid=1449.50,
            ask=1450.50,
        )

        assert tick.symbol == "RELIANCE"
        assert tick.exchange == "NSE"
        assert tick.timestamp == timestamp
        assert tick.last_price == 1450.0
        assert tick.volume == 1500000.0
        assert tick.bid == 1449.50
        assert tick.ask == 1450.50

    def test_allows_zero_values(self) -> None:
        tick = Tick(
            symbol="TEST",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15, tzinfo=UTC),
            last_price=0.0,
            volume=0.0,
            bid=0.0,
            ask=0.0,
        )

        assert tick.last_price == 0.0
        assert tick.volume == 0.0
        assert tick.bid == 0.0
        assert tick.ask == 0.0

    def test_allows_negative_values_without_validation(self) -> None:
        tick = Tick(
            symbol="TEST",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15, tzinfo=UTC),
            last_price=-100.0,
            volume=-1000.0,
            bid=-101.0,
            ask=-99.0,
        )

        assert tick.last_price == -100.0
        assert tick.volume == -1000.0
        assert tick.bid == -101.0
        assert tick.ask == -99.0

    def test_tick_is_immutable(self) -> None:
        tick = Tick(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15, tzinfo=UTC),
            last_price=25000.0,
        )

        with pytest.raises(FrozenInstanceError):
            tick.last_price = 26000.0
