from datetime import datetime, timedelta

from private_quant_terminal.data.repository import CandleRepository
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.tick import Tick
from private_quant_terminal.services.market_data import MarketDataService


class FakeBrokerProvider:
    def __init__(self) -> None:
        self.streamed_symbols: list[str] = []

    def stream_ticks(self, symbols: list[str]) -> None:
        self.streamed_symbols.extend(symbols)


def make_tick(
    symbol: str = "NIFTY",
    price: float = 25000.0,
) -> Tick:
    return Tick(
        symbol=symbol,
        exchange="NSE",
        timestamp=datetime.now(),
        last_price=price,
        volume=100,
    )


def make_candle(
    minutes: int,
    close: float,
) -> Candle:
    timestamp = datetime.now() + timedelta(minutes=minutes)

    return Candle(
        timestamp=timestamp,
        open=close - 10,
        high=close + 10,
        low=close - 20,
        close=close,
        volume=100,
    )


def test_loaded_symbols_is_empty_initially() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    assert service.loaded_symbols() == ()


def test_loaded_symbols_returns_symbols_with_tick_data() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    service.update_tick(make_tick(symbol="NIFTY"))
    service.update_tick(make_tick(symbol="BANKNIFTY"))

    assert service.loaded_symbols() == (
        "NIFTY",
        "BANKNIFTY",
    )


def test_clear_symbol_removes_cached_candles_and_tick() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    tick = make_tick(symbol="NIFTY")

    service.update_tick(tick)

    assert service.latest_tick("NIFTY") == tick
    assert service.loaded_symbols() == ("NIFTY",)

    service.clear_symbol("NIFTY")

    assert service.latest_tick("NIFTY") is None
    assert service.loaded_symbols() == ()


def test_clear_symbol_does_not_affect_other_symbols() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    nifty_tick = make_tick(
        symbol="NIFTY",
        price=25000.0,
    )

    banknifty_tick = make_tick(
        symbol="BANKNIFTY",
        price=55000.0,
    )

    service.update_tick(nifty_tick)
    service.update_tick(banknifty_tick)

    service.clear_symbol("NIFTY")

    assert service.latest_tick("NIFTY") is None
    assert service.latest_tick("BANKNIFTY") == banknifty_tick
    assert service.loaded_symbols() == ("BANKNIFTY",)


def test_service_can_handle_multiple_loaded_symbols() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    symbols = [
        "NIFTY",
        "BANKNIFTY",
        "RELIANCE",
        "TCS",
    ]

    for index, symbol in enumerate(symbols):
        service.update_tick(
            make_tick(
                symbol=symbol,
                price=25000.0 + index,
            )
        )

    assert service.loaded_symbols() == tuple(symbols)

    for symbol in symbols:
        assert service.latest_tick(symbol) is not None


def test_get_candles_returns_all_cached_candles() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    candles = [
        make_candle(0, 25000.0),
        make_candle(1, 25100.0),
        make_candle(2, 25200.0),
    ]

    repository.save("NIFTY", candles)

    service = MarketDataService(
        broker,
        repository,
    )

    assert service.get_candles("NIFTY") == tuple(candles)


def test_get_candles_respects_limit() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    candles = [
        make_candle(0, 25000.0),
        make_candle(1, 25100.0),
        make_candle(2, 25200.0),
    ]

    repository.save("NIFTY", candles)

    service = MarketDataService(
        broker,
        repository,
    )

    assert service.get_candles(
        "NIFTY",
        limit=2,
    ) == tuple(candles[-2:])


def test_get_candles_returns_empty_tuple_for_unknown_symbol() -> None:
    broker = FakeBrokerProvider()
    repository = CandleRepository()

    service = MarketDataService(
        broker,
        repository,
    )

    assert service.get_candles("UNKNOWN") == ()