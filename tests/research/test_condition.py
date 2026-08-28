import pytest

from private_quant_terminal.research.condition import (
    evaluate_condition,
    evaluate_conditions,
)
from private_quant_terminal.strategy import (
    ConditionOperator,
    StrategyCondition,
)


@pytest.mark.parametrize(
    ("operator", "actual", "expected"),
    [
        (ConditionOperator.GREATER_THAN, 11.0, True),
        (ConditionOperator.GREATER_THAN, 10.0, False),
        (ConditionOperator.GREATER_THAN_OR_EQUAL, 10.0, True),
        (ConditionOperator.LESS_THAN, 9.0, True),
        (ConditionOperator.LESS_THAN_OR_EQUAL, 10.0, True),
        (ConditionOperator.EQUAL, 10.0, True),
        (ConditionOperator.NOT_EQUAL, 11.0, True),
    ],
)
def test_evaluate_condition(
    operator: ConditionOperator,
    actual: float,
    expected: bool,
) -> None:
    condition = StrategyCondition(
        indicator="EMA_20",
        operator=operator,
        value=10.0,
    )

    assert evaluate_condition(
        condition,
        {"EMA_20": actual},
    ) is expected


def test_missing_indicator_raises_key_error() -> None:
    condition = StrategyCondition(
        indicator="EMA_20",
        operator=ConditionOperator.GREATER_THAN,
        value=10.0,
    )

    with pytest.raises(
        KeyError,
        match="Indicator value not available: EMA_20",
    ):
        evaluate_condition(condition, {})


def test_multiple_conditions_use_and_semantics() -> None:
    conditions = (
        StrategyCondition(
            indicator="EMA_20",
            operator=ConditionOperator.GREATER_THAN,
            value=100.0,
        ),
        StrategyCondition(
            indicator="RSI_14",
            operator=ConditionOperator.LESS_THAN,
            value=70.0,
        ),
    )

    assert evaluate_conditions(
        conditions,
        {
            "EMA_20": 105.0,
            "RSI_14": 65.0,
        },
    )

    assert not evaluate_conditions(
        conditions,
        {
            "EMA_20": 105.0,
            "RSI_14": 75.0,
        },
    )


def test_empty_conditions_are_true() -> None:
    assert evaluate_conditions((), {}) is True
