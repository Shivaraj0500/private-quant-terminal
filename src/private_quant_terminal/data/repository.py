from collections.abc import Sequence

from private_quant_terminal.data.validators import validate_candles
from private_quant_terminal.models import Candle


class CandleRepository:
    """In-memory repository for OHLCV candle data."""

    def __init__(self) -> None:
        self._candles: dict[str, list[Candle]] = {}

    def save(self, symbol: str, candles: Sequence[Candle]) -> None:
        validate_candles(candles)
        self._candles[symbol] = list(candles)

    def get_all(self, symbol: str) -> list[Candle]:
        return list(self._candles.get(symbol, []))

    def latest(self, symbol: str) -> Candle | None:
        candles = self._candles.get(symbol, [])
        return candles[-1] if candles else None

    def clear(self, symbol: str) -> None:
        self._candles.pop(symbol, None)
