from collections.abc import Mapping

from private_quant_terminal.strategy import (
    ConditionOperator,
    StrategyCondition,
)


def evaluate_condition(
    condition: StrategyCondition,
    indicator_values: Mapping[str, float],
) -> bool:
    """Evaluate one strategy condition against calculated indicator values."""

    if condition.indicator not in indicator_values:
        raise KeyError(
            f"Indicator value not available: {condition.indicator}"
        )

    actual_value = indicator_values[condition.indicator]
    expected_value = condition.value

    if condition.operator is ConditionOperator.GREATER_THAN:
        return actual_value > expected_value

    if condition.operator is ConditionOperator.GREATER_THAN_OR_EQUAL:
        return actual_value >= expected_value

    if condition.operator is ConditionOperator.LESS_THAN:
        return actual_value < expected_value

    if condition.operator is ConditionOperator.LESS_THAN_OR_EQUAL:
        return actual_value <= expected_value

    if condition.operator is ConditionOperator.EQUAL:
        return actual_value == expected_value

    if condition.operator is ConditionOperator.NOT_EQUAL:
        return actual_value != expected_value

    raise ValueError(
        f"Unsupported condition operator: {condition.operator}"
    )


def evaluate_conditions(
    conditions: tuple[StrategyCondition, ...],
    indicator_values: Mapping[str, float],
) -> bool:
    """Evaluate all conditions using AND semantics."""

    return all(
        evaluate_condition(condition, indicator_values)
        for condition in conditions
    )
