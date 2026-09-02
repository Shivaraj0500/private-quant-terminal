from private_quant_terminal.strategy.expressions import (
    ArithmeticExpression,
    ConstantExpression,
    ExpressionType,
    IndicatorExpression,
    PriceExpression,
    PriceField,
    TimeExpression,
    TimeField,
    UnaryExpression,
    VariableExpression,
    absolute,
    add,
    arithmetic,
    constant,
    indicator,
    negate,
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


def test_arithmetic_expression_supports_all_binary_operators() -> None:
    left = constant(10)
    right = constant(3)

    for operator in ("+", "-", "*", "/", "%", "**"):
        expression = arithmetic(left, operator, right)

        assert isinstance(expression, ArithmeticExpression)
        assert expression.left == left
        assert expression.right == right
        assert expression.operator == operator
        assert expression.expression_type is ExpressionType.ARITHMETIC


def test_arithmetic_helpers_create_expected_operators() -> None:
    left = constant(10)
    right = constant(3)

    assert add(left, right).operator == "+"
    assert arithmetic(left, "-", right).operator == "-"
    assert arithmetic(left, "*", right).operator == "*"
    assert arithmetic(left, "/", right).operator == "/"
    assert arithmetic(left, "%", right).operator == "%"
    assert arithmetic(left, "**", right).operator == "**"


def test_unary_expression_supports_abs_and_neg() -> None:
    operand = variable("pnl")

    absolute_expression = absolute(operand)
    negate_expression = negate(operand)

    assert isinstance(absolute_expression, UnaryExpression)
    assert absolute_expression.operator == "abs"
    assert absolute_expression.operand == operand
    assert absolute_expression.expression_type is ExpressionType.UNARY

    assert isinstance(negate_expression, UnaryExpression)
    assert negate_expression.operator == "neg"
    assert negate_expression.operand == operand
    assert negate_expression.expression_type is ExpressionType.UNARY


def test_expression_operators_are_normalized() -> None:
    expression = arithmetic(constant(10), "  +  ", constant(2))
    unary_expression = UnaryExpression(operator=" ABS ", operand=constant(-5))

    assert expression.operator == "+"
    assert unary_expression.operator == "abs"


def test_expression_operators_reject_unsupported_values() -> None:
    try:
        arithmetic(constant(1), "//", constant(2))
    except ValueError as exc:
        assert str(exc) == "Unsupported arithmetic operator: //"
    else:
        raise AssertionError("Expected ValueError")

    try:
        UnaryExpression(operator="sqrt", operand=constant(4))
    except ValueError as exc:
        assert str(exc) == "Unsupported unary operator: sqrt"
    else:
        raise AssertionError("Expected ValueError")
