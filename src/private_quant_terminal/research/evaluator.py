from collections.abc import Mapping
from enum import Enum

from private_quant_terminal.research.condition import evaluate_conditions
from private_quant_terminal.strategy import StrategyDefinition


class StrategyDecision(str, Enum):
    """Deterministic decision produced by strategy evaluation."""

    ENTRY = "ENTRY"
    EXIT = "EXIT"
    HOLD = "HOLD"


def evaluate_strategy(
    strategy: StrategyDefinition,
    indicator_values: Mapping[str, float],
) -> StrategyDecision:
    """Evaluate a strategy's entry and exit conditions."""

    if evaluate_conditions(
        strategy.entry_conditions,
        indicator_values,
    ):
        return StrategyDecision.ENTRY

    if evaluate_conditions(
        strategy.exit_conditions,
        indicator_values,
    ):
        return StrategyDecision.EXIT

    return StrategyDecision.HOLD
