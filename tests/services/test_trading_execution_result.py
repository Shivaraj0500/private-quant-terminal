from dataclasses import FrozenInstanceError

import pytest

from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.risk.result import RiskResult
from private_quant_terminal.services.trading_execution_result import (
    TradingExecutionResult,
)


class TestTradingExecutionResult:
    def test_creates_non_completed_result(self) -> None:
        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
            reason="Signal type HOLD does not create an order",
        )

        result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=None,
            execution_report=None,
            completed=False,
            reason="Signal type HOLD does not create an order",
        )

        assert result.execution_result is execution_result
        assert result.risk_result is None
        assert result.execution_report is None
        assert result.completed is False
        assert result.reason == "Signal type HOLD does not create an order"

    def test_creates_completed_result(self) -> None:
        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=True,
        )
        risk_result = RiskResult(approved=True)

        result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=risk_result,
            execution_report=None,
            completed=True,
        )

        assert result.execution_result is execution_result
        assert result.risk_result is risk_result
        assert result.completed is True
        assert result.reason is None

    def test_result_is_immutable(self) -> None:
        execution_result = ExecutionResult(
            signal_symbol="NIFTY",
            order_request=None,
            executed=False,
        )

        result = TradingExecutionResult(
            execution_result=execution_result,
            risk_result=None,
            execution_report=None,
            completed=False,
        )

        with pytest.raises(FrozenInstanceError):
            result.completed = True
