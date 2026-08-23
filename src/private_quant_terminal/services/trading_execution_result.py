from dataclasses import dataclass

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.execution.result import ExecutionResult
from private_quant_terminal.risk.result import RiskResult


@dataclass(frozen=True)
class TradingExecutionResult:
    """Result of the complete trading execution workflow."""

    execution_result: ExecutionResult
    risk_result: RiskResult | None
    execution_report: ExecutionReport | None
    completed: bool
    reason: str | None = None
