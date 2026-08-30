from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    ExpressionType,
    IndicatorExpression,
    PriceField,
    PriceExpression,
    TimeField,
    TimeExpression,
    VariableExpression,
    constant,
    indicator,
    price,
    time_value,
    variable,
)


def test_constant_expression_is_immutable() -> None:
    expression = constant(60)

    assert expression == ConstantExpression(value=60.0)
    assert expression.expression_type is ExpressionType.CONSTANT


def test_price_expression_supports_close() -> None:
    expression = price("close")

    assert expression == PriceExpression(field=PriceField.CLOSE)
    assert expression.expression_type is ExpressionType.PRICE


def test_indicator_expression_normalizes_name_and_parameters() -> None:
    expression = indicator(
        " supertrend ",
        parameters={
            "multiplier": 2,
            "period": 10,
        },
    )

    assert expression == IndicatorExpression(
        name="SUPERTREND",
        parameters=(
            ("multiplier", 2.0),
            ("period", 10.0),
        ),
        timeframe=None,
    )


def test_indicator_parameter_order_is_deterministic() -> None:
    first = indicator(
        "EMA",
        parameters={
            "period": 50,
            "source": 1,
        },
    )
    second = indicator(
        "EMA",
        parameters={
            "source": 1,
            "period": 50,
        },
    )

    assert first == second


def test_indicator_can_have_its_own_timeframe() -> None:
    expression = indicator(
        "RSI",
        parameters={"period": 14},
        timeframe="15m",
    )

    assert expression.timeframe == "15m"


def test_time_expression_supports_time_of_day() -> None:
    expression = time_value(TimeField.TIME_OF_DAY)

    assert isinstance(expression, TimeExpression)
    assert expression.expression_type is ExpressionType.TIME


def test_variable_expression_requires_a_name() -> None:
    expression = variable("atm_strike")

    assert expression == VariableExpression(name="atm_strike")
    assert expression.expression_type is ExpressionType.VARIABLE


def test_variable_expression_rejects_empty_name() -> None:
    try:
        variable("   ")
    except ValueError as exc:
        assert str(exc) == "Variable name must not be empty."
    else:
        raise AssertionError("Expected ValueError")
