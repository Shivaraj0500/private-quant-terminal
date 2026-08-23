from datetime import datetime, timedelta

import pytest

from private_quant_terminal.data.repository import CandleRepository
from private_quant_terminal.models import Candle


def make_candle(timestamp: datetime, close: float = 105.0) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=100.0,
        high=110.0,
        low=90.0,
        close=close,
        volume=1000.0,
    )


class TestCandleRepository:
    def test_save_and_get_all_candles(self) -> None:
        start = datetime(2026, 1, 1, 9, 15)

        candles = [
            make_candle(start),
            make_candle(start + timedelta(minutes=1)),
        ]

        repository = CandleRepository()
        repository.save("NIFTY", candles)

        result = repository.get_all("NIFTY")

        assert result == candles

    def test_get_all_returns_empty_list_for_unknown_symbol(self) -> None:
        repository = CandleRepository()

        assert repository.get_all("UNKNOWN") == []

    def test_get_all_returns_copy_of_stored_list(self) -> None:
        start = datetime(2026, 1, 1, 9, 15)

        candles = [
            make_candle(start),
            make_candle(start + timedelta(minutes=1)),
        ]

        repository = CandleRepository()
        repository.save("NIFTY", candles)

        result = repository.get_all("NIFTY")
        result.pop()

        assert len(result) == 1
        assert len(repository.get_all("NIFTY")) == 2

    def test_save_stores_copy_of_input_sequence(self) -> None:
        start = datetime(2026, 1, 1, 9, 15)

        candles = [
            make_candle(start),
            make_candle(start + timedelta(minutes=1)),
        ]

        repository = CandleRepository()
        repository.save("NIFTY", candles)

        candles.pop()

        assert len(candles) == 1
        assert len(repository.get_all("NIFTY")) == 2

    def test_latest_returns_latest_candle(self) -> None:
        start = datetime(2026, 1, 1, 9, 15)

        first = make_candle(start, close=101.0)
        latest = make_candle(
            start + timedelta(minutes=1),
            close=106.0,
        )

        repository = CandleRepository()
        repository.save("NIFTY", [first, latest])

        assert repository.latest("NIFTY") == latest

    def test_latest_returns_none_for_unknown_symbol(self) -> None:
        repository = CandleRepository()

        assert repository.latest("UNKNOWN") is None

    def test_clear_removes_saved_candles(self) -> None:
        candle = make_candle(datetime(2026, 1, 1, 9, 15))

        repository = CandleRepository()
        repository.save("NIFTY", [candle])

        repository.clear("NIFTY")

        assert repository.get_all("NIFTY") == []
        assert repository.latest("NIFTY") is None

    def test_clear_unknown_symbol_does_not_raise_error(self) -> None:
        repository = CandleRepository()

        repository.clear("UNKNOWN")

        assert repository.get_all("UNKNOWN") == []

    def test_save_rejects_empty_candle_collection(self) -> None:
        repository = CandleRepository()

        with pytest.raises(
            ValueError,
            match="candle collection cannot be empty",
        ):
            repository.save("NIFTY", [])

    def test_save_rejects_unordered_candles(self) -> None:
        start = datetime(2026, 1, 1, 9, 15)

        candles = [
            make_candle(start + timedelta(minutes=1)),
            make_candle(start),
        ]

        repository = CandleRepository()

        with pytest.raises(
            ValueError,
            match="candles must be ordered by timestamp",
        ):
            repository.save("NIFTY", candles)

    def test_save_rejects_duplicate_candle_timestamps(self) -> None:
        timestamp = datetime(2026, 1, 1, 9, 15)

        candles = [
            make_candle(timestamp),
            make_candle(timestamp),
        ]

        repository = CandleRepository()

        with pytest.raises(
            ValueError,
            match="duplicate candle timestamps are not allowed",
        ):
            repository.save("NIFTY", candles)