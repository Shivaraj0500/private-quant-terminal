import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategies import (
    Signal,
    SignalType,
    Strategy,
)


class DummyStrategy(Strategy):
    @property
    def name(self) -> str:
        return "dummy"

    def generate_signal(
        self,
        symbol: str,
        candles: list[Candle],
    ) -> Signal:
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
        )


def test_strategy_can_be_implemented() -> None:
    strategy = DummyStrategy()

    assert strategy.name == "dummy"


def test_strategy_generates_signal() -> None:
    strategy = DummyStrategy()

    signal = strategy.generate_signal(
        symbol="NIFTY",
        candles=[],
    )

    assert signal.symbol == "NIFTY"
    assert signal.signal_type is SignalType.HOLD


def test_base_strategy_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Strategy()