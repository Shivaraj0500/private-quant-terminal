import pytest

from private_quant_terminal.strategy.expressions import (
    IndicatorExpression,
    indicator,
)


def test_indicator_expression_defaults_to_value_output() -> None:
    expression = indicator(
        "SMA",
        parameters={"period": 20},
    )

    assert expression.output == "value"


def test_indicator_expression_can_select_named_output() -> None:
    expression = indicator(
        "BBANDS",
        parameters={"period": 20},
        output="upper",
    )

    assert expression.name == "BBANDS"
    assert expression.output == "upper"


def test_indicator_expression_preserves_output_in_identity() -> None:
    expression = indicator(
        "MACD",
        output="signal",
    )

    assert expression.output == "signal"


def test_output_name_is_normalized() -> None:
    expression = indicator(
        "BBANDS",
        output=" Upper ",
    )

    assert expression.output == "upper"


def test_empty_output_is_rejected() -> None:
    with pytest.raises(ValueError, match="output"):
        indicator(
            "BBANDS",
            output="   ",
        )


def test_existing_indicator_expression_remains_backward_compatible() -> None:
    expression = indicator("EMA")

    assert expression == IndicatorExpression(
        name="EMA",
        parameters=(),
        timeframe=None,
        output="value",
    )
