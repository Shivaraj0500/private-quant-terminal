from abc import ABC, abstractmethod
from collections.abc import Sequence

from private_quant_terminal.models.candle import Candle
from private_quant_terminal.strategies.signal import Signal


class Strategy(ABC):
    """Base contract for all trading strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy name."""
        raise NotImplementedError

    @abstractmethod
    def generate_signal(
        self,
        symbol: str,
        candles: Sequence[Candle],
    ) -> Signal:
        """Generate a trading signal for a symbol."""
        raise NotImplementedError
    