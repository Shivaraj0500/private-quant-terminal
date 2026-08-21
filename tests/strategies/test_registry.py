import pytest

from private_quant_terminal.strategies import (
    Signal,
    SignalType,
    Strategy,
    StrategyRegistry,
)


class DummyStrategy(Strategy):
    @property
    def name(self) -> str:
        return "dummy"

    def generate_signal(
        self,
        symbol: str,
        candles,
    ) -> Signal:
        return Signal(
            symbol=symbol,
            signal_type=SignalType.HOLD,
        )


def test_registry_registers_strategy() -> None:
    registry = StrategyRegistry()
    strategy = DummyStrategy()

    registry.register(strategy)

    assert "dummy" in registry


def test_registry_gets_strategy() -> None:
    registry = StrategyRegistry()
    strategy = DummyStrategy()

    registry.register(strategy)

    assert registry.get("dummy") is strategy


def test_registry_returns_names() -> None:
    registry = StrategyRegistry()

    registry.register(DummyStrategy())

    assert registry.names() == ["dummy"]


def test_registry_rejects_duplicate_strategy() -> None:
    registry = StrategyRegistry()

    registry.register(DummyStrategy())

    with pytest.raises(ValueError):
        registry.register(DummyStrategy())


def test_registry_rejects_unknown_strategy() -> None:
    registry = StrategyRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")