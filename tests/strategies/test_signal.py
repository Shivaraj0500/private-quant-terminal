from private_quant_terminal.strategies import Signal, SignalType


def test_signal_can_be_created() -> None:
    signal = Signal(
        symbol="NIFTY",
        signal_type=SignalType.BUY,
    )

    assert signal.symbol == "NIFTY"
    assert signal.signal_type is SignalType.BUY
    assert signal.price is None
    assert signal.reason is None


def test_signal_supports_optional_metadata() -> None:
    signal = Signal(
        symbol="BANKNIFTY",
        signal_type=SignalType.SELL,
        price=52000.0,
        reason="Bearish crossover",
    )

    assert signal.price == 52000.0
    assert signal.reason == "Bearish crossover"


def test_signal_is_immutable() -> None:
    signal = Signal(
        symbol="NIFTY",
        signal_type=SignalType.HOLD,
    )

    assert signal.signal_type is SignalType.HOLD