from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal

import pytest

from private_quant_terminal.data.schemas import MarketTick


class TestMarketTick:
    def test_creates_valid_market_tick(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15)

        tick = MarketTick(
            symbol="NIFTY",
            timestamp=timestamp,
            price=Decimal("25000.50"),
            volume=100,
        )

        assert tick.symbol == "NIFTY"
        assert tick.timestamp == timestamp
        assert tick.price == Decimal("25000.50")
        assert tick.volume == 100

    def test_volume_defaults_to_zero(self) -> None:
        tick = MarketTick(
            symbol="NIFTY",
            timestamp=datetime(2026, 8, 24, 9, 15),
            price=Decimal("25000.00"),
        )

        assert tick.volume == 0

    def test_allows_zero_volume(self) -> None:
        tick = MarketTick(
            symbol="BANKNIFTY",
            timestamp=datetime(2026, 8, 24, 9, 15),
            price=Decimal("50000.00"),
            volume=0,
        )

        assert tick.volume == 0

    def test_rejects_empty_symbol(self) -> None:
        with pytest.raises(
            ValueError,
            match="symbol cannot be empty",
        ):
            MarketTick(
                symbol="",
                timestamp=datetime(2026, 8, 24, 9, 15),
                price=Decimal("100.00"),
            )

    def test_rejects_zero_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            MarketTick(
                symbol="NIFTY",
                timestamp=datetime(2026, 8, 24, 9, 15),
                price=Decimal("0"),
            )

    def test_rejects_negative_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            MarketTick(
                symbol="NIFTY",
                timestamp=datetime(2026, 8, 24, 9, 15),
                price=Decimal("-100.00"),
            )

    def test_rejects_negative_volume(self) -> None:
        with pytest.raises(
            ValueError,
            match="volume cannot be negative",
        ):
            MarketTick(
                symbol="NIFTY",
                timestamp=datetime(2026, 8, 24, 9, 15),
                price=Decimal("100.00"),
                volume=-1,
            )

    def test_market_tick_is_immutable(self) -> None:
        tick = MarketTick(
            symbol="NIFTY",
            timestamp=datetime(2026, 8, 24, 9, 15),
            price=Decimal("25000.00"),
            volume=100,
        )

        with pytest.raises(FrozenInstanceError):
            tick.price = Decimal("26000.00")