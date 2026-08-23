from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from private_quant_terminal.models.quote import Quote


class TestQuote:
    def test_creates_quote_with_required_fields(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15)

        quote = Quote(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=timestamp,
            last_price=25000.0,
        )

        assert quote.symbol == "NIFTY"
        assert quote.exchange == "NSE"
        assert quote.timestamp == timestamp
        assert quote.last_price == 25000.0

    def test_optional_fields_default_to_none(self) -> None:
        quote = Quote(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15),
            last_price=25000.0,
        )

        assert quote.open is None
        assert quote.high is None
        assert quote.low is None
        assert quote.previous_close is None
        assert quote.volume is None

    def test_creates_quote_with_all_fields(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15)

        quote = Quote(
            symbol="RELIANCE",
            exchange="NSE",
            timestamp=timestamp,
            last_price=1450.0,
            open=1400.0,
            high=1475.0,
            low=1395.0,
            previous_close=1420.0,
            volume=1500000.0,
        )

        assert quote.symbol == "RELIANCE"
        assert quote.exchange == "NSE"
        assert quote.timestamp == timestamp
        assert quote.last_price == 1450.0
        assert quote.open == 1400.0
        assert quote.high == 1475.0
        assert quote.low == 1395.0
        assert quote.previous_close == 1420.0
        assert quote.volume == 1500000.0

    def test_allows_zero_optional_values(self) -> None:
        quote = Quote(
            symbol="TEST",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15),
            last_price=0.0,
            open=0.0,
            high=0.0,
            low=0.0,
            previous_close=0.0,
            volume=0.0,
        )

        assert quote.last_price == 0.0
        assert quote.open == 0.0
        assert quote.high == 0.0
        assert quote.low == 0.0
        assert quote.previous_close == 0.0
        assert quote.volume == 0.0

    def test_allows_negative_values_without_validation(self) -> None:
        quote = Quote(
            symbol="TEST",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15),
            last_price=-100.0,
            open=-90.0,
            high=-80.0,
            low=-110.0,
            previous_close=-95.0,
            volume=-1000.0,
        )

        assert quote.last_price == -100.0
        assert quote.volume == -1000.0

    def test_quote_is_immutable(self) -> None:
        quote = Quote(
            symbol="NIFTY",
            exchange="NSE",
            timestamp=datetime(2026, 8, 24, 9, 15),
            last_price=25000.0,
        )

        with pytest.raises(FrozenInstanceError):
            quote.last_price = 26000.0