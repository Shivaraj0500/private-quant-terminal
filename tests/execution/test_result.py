from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.execution.result import ExecutionResult


class TestExecutionResult:
    def test_creates_executed_result_with_order_request(self) -> None:
        order_request = OrderRequest(
            symbol="NIFTY",
            quantity=10,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
        )

        result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=order_request,
            executed=True,
        )

        assert result.signal_symbol == "NIFTY"
        assert result.order_request is order_request
        assert result.executed is True
        assert result.reason is None

    def test_creates_non_executed_result_without_order_request(self) -> None:
        result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="Signal type HOLD does not create an order",
        )

        assert result.signal_symbol == "NIFTY"
        assert result.order_request is None
        assert result.executed is False
        assert result.reason == "Signal type HOLD does not create an order"

    def test_execution_result_is_immutable(self) -> None:
        result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
        )

        try:
            result.executed = True
        except Exception as error:
            assert type(error).__name__ == "FrozenInstanceError"
        else:
            raise AssertionError("ExecutionResult should be immutable")
