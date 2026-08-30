from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    ComparisonOperator,
    CrossingCondition,
    CrossingOperator,
    LogicalCondition,
    LogicalOperator,
    all_of,
    any_of,
    compare,
    cross_above,
    cross_below,
    not_,
)
from private_quant_terminal.strategy.expressions import (
    constant,
    indicator,
    price,
)


def test_comparison_condition_supports_price_against_indicator() -> None:
    condition = compare(
        price("close"),
        ">",
        indicator("EMA", parameters={"period": 50}),
    )

    assert condition == ComparisonCondition(
        left=price("close"),
        operator=ComparisonOperator.GREATER_THAN,
        right=indicator("EMA", parameters={"period": 50}),
    )


def test_cross_above_is_structured() -> None:
    condition = cross_above(
        price("close"),
        indicator(
            "SUPERTREND",
            parameters={
                "period": 10,
                "multiplier": 2,
            },
        ),
    )

    assert condition == CrossingCondition(
        left=price("close"),
        operator=CrossingOperator.CROSS_ABOVE,
        right=indicator(
            "SUPERTREND",
            parameters={
                "period": 10,
                "multiplier": 2,
            },
        ),
    )


def test_cross_below_is_structured() -> None:
    condition = cross_below(
        price("close"),
        indicator("SUPERTREND", parameters={"period": 10}),
    )

    assert condition.operator is CrossingOperator.CROSS_BELOW


def test_and_supports_nested_conditions() -> None:
    condition = all_of(
        compare(price("close"), ">", constant(100)),
        compare(
            price("close"),
            ">",
            indicator("EMA", parameters={"period": 50}),
        ),
    )

    assert condition.operator is LogicalOperator.AND
    assert len(condition.conditions) == 2


def test_or_supports_nested_conditions() -> None:
    condition = any_of(
        compare(price("close"), ">", constant(100)),
        compare(price("close"), "<", constant(90)),
    )

    assert condition.operator is LogicalOperator.OR
    assert len(condition.conditions) == 2


def test_not_contains_exactly_one_condition() -> None:
    child = compare(price("close"), ">", constant(100))
    condition = not_(child)

    assert condition.operator is LogicalOperator.NOT
    assert condition.conditions == (child,)


def test_and_requires_a_condition() -> None:
    try:
        all_of()
    except ValueError as exc:
        assert str(exc) == "AND requires at least one condition."
    else:
        raise AssertionError("Expected ValueError")


def test_or_requires_a_condition() -> None:
    try:
        any_of()
    except ValueError as exc:
        assert str(exc) == "OR requires at least one condition."
    else:
        raise AssertionError("Expected ValueError")
