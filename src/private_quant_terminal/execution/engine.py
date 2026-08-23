from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.strategies.signal import Signal, SignalType


class ExecutionEngine:
    """Convert strategy signals into broker order requests."""

    def __init__(
        self,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
    ) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        self._quantity = quantity
        self._order_type = order_type

    def execute(self, signal: Signal) -> ExecutionResult:
        """Convert a signal into an executable order request."""

        if signal.signal_type is SignalType.HOLD:
            return ExecutionResult(
                signal_symbol=signal.symbol,
                order_request=None,
                executed=False,
                reason="Signal type HOLD does not create an order",
            )

        side = self._to_order_side(signal.signal_type)

        order_request = OrderRequest(
            symbol=signal.symbol,
            quantity=self._quantity,
            side=side,
            order_type=self._order_type,
        )

        return ExecutionResult(
            signal_symbol=signal.symbol,
            order_request=order_request,
            executed=True,
        )

    @staticmethod
    def _to_order_side(signal_type: SignalType) -> OrderSide:
        if signal_type is SignalType.BUY:
            return OrderSide.BUY

        if signal_type is SignalType.SELL:
            return OrderSide.SELL

        raise ValueError(
            f"Unsupported signal type for execution: {signal_type}"
        )
