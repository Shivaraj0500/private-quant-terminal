import pytest

from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.engine import ExecutionEngine
from private_quant_terminal.strategies.signal import Signal, SignalType


class TestExecutionEngine:
    def test_rejects_zero_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            ExecutionEngine(quantity=0)

    def test_rejects_negative_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            ExecutionEngine(quantity=-1)

    def test_creates_market_order_by_default(self) -> None:
        engine = ExecutionEngine(quantity=10)

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.BUY,
        )

        result = engine.execute(signal)

        assert result.executed is True
        assert result.reason is None
        assert result.order_request is not None
        assert result.order_request.symbol == "NIFTY"
        assert result.order_request.quantity == 10
        assert result.order_request.side is OrderSide.BUY
        assert result.order_request.order_type is OrderType.MARKET

    def test_converts_buy_signal_to_buy_order(self) -> None:
        engine = ExecutionEngine(quantity=25)

        signal = Signal(
            symbol="BANKNIFTY",
            signal_type=SignalType.BUY,
        )

        result = engine.execute(signal)

        assert result.signal_symbol == "BANKNIFTY"
        assert result.executed is True
        assert result.order_request is not None
        assert result.order_request.side is OrderSide.BUY

    def test_converts_sell_signal_to_sell_order(self) -> None:
        engine = ExecutionEngine(quantity=15)

        signal = Signal(
            symbol="RELIANCE",
            signal_type=SignalType.SELL,
        )

        result = engine.execute(signal)

        assert result.signal_symbol == "RELIANCE"
        assert result.executed is True
        assert result.order_request is not None
        assert result.order_request.side is OrderSide.SELL

    def test_hold_signal_does_not_create_order(self) -> None:
        engine = ExecutionEngine(quantity=10)

        signal = Signal(
            symbol="NIFTY",
            signal_type=SignalType.HOLD,
        )

        result = engine.execute(signal)

        assert result.signal_symbol == "NIFTY"
        assert result.executed is False
        assert result.order_request is None
        assert result.reason == "Signal type HOLD does not create an order"

    def test_uses_configured_order_type(self) -> None:
        engine = ExecutionEngine(
            quantity=10,
            order_type=OrderType.LIMIT,
        )

        signal = Signal(
            symbol="TCS",
            signal_type=SignalType.BUY,
        )

        result = engine.execute(signal)

        assert result.order_request is not None
        assert result.order_request.order_type is OrderType.LIMIT

    def test_preserves_signal_symbol(self) -> None:
        engine = ExecutionEngine(quantity=5)

        signal = Signal(
            symbol="INFY",
            signal_type=SignalType.SELL,
        )

        result = engine.execute(signal)

        assert result.signal_symbol == "INFY"
        assert result.order_request is not None
        assert result.order_request.symbol == "INFY"

    def test_private_conversion_rejects_hold_signal(self) -> None:
        with pytest.raises(
            ValueError,
            match="Unsupported signal type for execution",
        ):
            ExecutionEngine._to_order_side(SignalType.HOLD)
