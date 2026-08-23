from datetime import datetime

import pytest

from private_quant_terminal.models.candle import Candle


class TestCandle:
    def test_creates_valid_candle(self) -> None:
        timestamp = datetime(2026, 8, 24, 9, 15)

        candle = Candle(
            timestamp=timestamp,
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
            volume=1000.0,
        )

        assert candle.timestamp == timestamp
        assert candle.open == 100.0
        assert candle.high == 110.0
        assert candle.low == 95.0
        assert candle.close == 105.0
        assert candle.volume == 1000.0

    def test_uses_default_zero_volume(self) -> None:
        candle = Candle(
            timestamp=datetime(2026, 8, 24, 9, 15),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
        )

        assert candle.volume == 0.0

    def test_allows_boundary_values(self) -> None:
        candle = Candle(
            timestamp=datetime(2026, 8, 24, 9, 15),
            open=95.0,
            high=110.0,
            low=95.0,
            close=110.0,
        )

        assert candle.open == candle.low
        assert candle.close == candle.high

    def test_rejects_high_lower_than_low(self) -> None:
        with pytest.raises(
            ValueError,
            match="high cannot be lower than low",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=100.0,
                high=90.0,
                low=95.0,
                close=98.0,
            )

    def test_rejects_open_below_low(self) -> None:
        with pytest.raises(
            ValueError,
            match="open must be between low and high",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=90.0,
                high=110.0,
                low=95.0,
                close=100.0,
            )

    def test_rejects_open_above_high(self) -> None:
        with pytest.raises(
            ValueError,
            match="open must be between low and high",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=115.0,
                high=110.0,
                low=95.0,
                close=100.0,
            )

    def test_rejects_close_below_low(self) -> None:
        with pytest.raises(
            ValueError,
            match="close must be between low and high",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=100.0,
                high=110.0,
                low=95.0,
                close=90.0,
            )

    def test_rejects_close_above_high(self) -> None:
        with pytest.raises(
            ValueError,
            match="close must be between low and high",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=100.0,
                high=110.0,
                low=95.0,
                close=115.0,
            )

    def test_rejects_negative_volume(self) -> None:
        with pytest.raises(
            ValueError,
            match="volume cannot be negative",
        ):
            Candle(
                timestamp=datetime(2026, 8, 24, 9, 15),
                open=100.0,
                high=110.0,
                low=95.0,
                close=105.0,
                volume=-1.0,
            )

    def test_candle_is_immutable(self) -> None:
        candle = Candle(
            timestamp=datetime(2026, 8, 24, 9, 15),
            open=100.0,
            high=110.0,
            low=95.0,
            close=105.0,
        )

        with pytest.raises(AttributeError):
            candle.close = 120.0