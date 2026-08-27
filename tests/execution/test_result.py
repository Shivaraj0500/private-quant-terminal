from dataclasses import FrozenInstanceError

import pytest

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

    def test_uses_none_as_default_reason(self) -> None:
        result = ExecutionResult(
            signal_symbol="TCS",
            order_request=None,
            executed=False,
        )

        assert result.reason is None

    def test_execution_result_is_immutable(self) -> None:
        result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
        )

        with pytest.raises(FrozenInstanceError):
            result.executed = True

    def test_equal_execution_results_are_equal(self) -> None:
        first = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="No order",
        )

        second = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="No order",
        )

        assert first == second

    def test_different_execution_results_are_not_equal(self) -> None:
        first = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="No order",
        )

        second = ExecutionResult(
            signal_symbol="BANKNIFTY",
            order_request=None,
            executed=False,
            reason="No order",
        )

        assert first != second