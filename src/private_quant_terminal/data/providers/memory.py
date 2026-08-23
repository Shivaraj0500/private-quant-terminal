from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import Instrument


class InMemoryMarketDataProvider:
    def __init__(self) -> None:
        self._instruments: dict[str, Instrument] = {}
        self._candles: dict[tuple[str, str], list[Candle]] = {}

    def add_instrument(self, instrument: Instrument) -> None:
        self._instruments[instrument.symbol] = instrument

    def get_instrument(self, symbol: str) -> Instrument | None:
        return self._instruments.get(symbol)

    def add_candles(
        self,
        symbol: str,
        timeframe: str,
        candles: list[Candle],
    ) -> None:
        self._candles[(symbol, timeframe)] = candles

    def get_candles(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:
        candles = self._candles.get((symbol, timeframe), [])
        return candles[-limit:]