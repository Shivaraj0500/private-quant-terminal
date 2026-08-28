from dataclasses import dataclass

from private_quant_terminal.strategy.enums import (
    PositionSizingMethod,
    StopLossType,
    TakeProfitType,
)
from private_quant_terminal.strategy.ir import StrategyDefinition


@dataclass(frozen=True)
class ValidationIssue:
    """A deterministic validation issue."""

    field: str
    message: str


@dataclass(frozen=True)
class StrategyValidationResult:
    """Result of deterministic strategy validation."""

    valid: bool
    issues: tuple[ValidationIssue, ...] = ()


def validate_strategy(
    strategy: StrategyDefinition,
) -> StrategyValidationResult:
    """Validate a strategy definition deterministically."""

    issues: list[ValidationIssue] = []

    if not strategy.strategy_id.strip():
        issues.append(
            ValidationIssue(
                field="strategy_id",
                message="Strategy ID cannot be empty.",
            )
        )

    if not strategy.name.strip():
        issues.append(
            ValidationIssue(
                field="name",
                message="Strategy name cannot be empty.",
            )
        )

    if not strategy.description.strip():
        issues.append(
            ValidationIssue(
                field="description",
                message="Strategy description cannot be empty.",
            )
        )

    if not strategy.instruments:
        issues.append(
            ValidationIssue(
                field="instruments",
                message="Strategy must define at least one instrument.",
            )
        )

    normalized_instruments = {
        instrument.strip().upper()
        for instrument in strategy.instruments
    }

    if "" in normalized_instruments:
        issues.append(
            ValidationIssue(
                field="instruments",
                message="Instrument symbols cannot be empty.",
            )
        )

    if not strategy.entry_conditions:
        issues.append(
            ValidationIssue(
                field="entry_conditions",
                message="Strategy must define at least one entry condition.",
            )
        )

    if not strategy.exit_conditions:
        issues.append(
            ValidationIssue(
                field="exit_conditions",
                message="Strategy must define at least one exit condition.",
            )
        )

    if strategy.position_sizing.value <= 0:
        issues.append(
            ValidationIssue(
                field="position_sizing.value",
                message="Position sizing value must be greater than zero.",
            )
        )

    if (
        strategy.position_sizing.method
        is PositionSizingMethod.PERCENT_OF_EQUITY
        and strategy.position_sizing.value > 100
    ):
        issues.append(
            ValidationIssue(
                field="position_sizing.value",
                message="Percent-of-equity sizing cannot exceed 100.",
            )
        )

    if strategy.stop_loss.type is StopLossType.NONE:
        if strategy.stop_loss.value is not None:
            issues.append(
                ValidationIssue(
                    field="stop_loss.value",
                    message="Stop-loss value must be omitted when stop-loss type is NONE.",
                )
            )
    elif strategy.stop_loss.value is None:
        issues.append(
            ValidationIssue(
                field="stop_loss.value",
                message="Stop-loss value is required for the selected stop-loss type.",
            )
        )
    elif strategy.stop_loss.value <= 0:
        issues.append(
            ValidationIssue(
                field="stop_loss.value",
                message="Stop-loss value must be greater than zero.",
            )
        )

    if strategy.take_profit.type is TakeProfitType.NONE:
        if strategy.take_profit.value is not None:
            issues.append(
                ValidationIssue(
                    field="take_profit.value",
                    message="Take-profit value must be omitted when take-profit type is NONE.",
                )
            )
    elif strategy.take_profit.value is None:
        issues.append(
            ValidationIssue(
                field="take_profit.value",
                message="Take-profit value is required for the selected take-profit type.",
            )
        )
    elif strategy.take_profit.value <= 0:
        issues.append(
            ValidationIssue(
                field="take_profit.value",
                message="Take-profit value must be greater than zero.",
            )
        )

    if strategy.execution.slippage_bps < 0:
        issues.append(
            ValidationIssue(
                field="execution.slippage_bps",
                message="Slippage cannot be negative.",
            )
        )

    if strategy.execution.transaction_cost_bps < 0:
        issues.append(
            ValidationIssue(
                field="execution.transaction_cost_bps",
                message="Transaction cost cannot be negative.",
            )
        )

    return StrategyValidationResult(
        valid=not issues,
        issues=tuple(issues),
    )
