from dataclasses import dataclass

from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.risk.result import RiskResult
from private_quant_terminal.services.trading_execution_result import (
    TradingExecutionResult,
)


@dataclass(frozen=True)
class TradingWorkflowResult:
    """Final result of the application trading workflow."""

    risk_result: RiskResult
    execution_result: TradingExecutionResult | None
    position: Position | None
