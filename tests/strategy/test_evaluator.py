from datetime import UTC, datetime, timedelta

import pytest

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.conditions import (
    all_of,
    compare,
    cross_above,
    cross_below,
)
from private_quant_terminal.strategy.evaluator import (
    ConditionEvaluator,
    ExpressionEvaluator,
)
from private_quant_terminal.strategy.expressions import (
    PositionField,
    PriceField,
    constant,
    indicator,
    position,
    price,
    variable,
)
from private_quant_terminal.strategy.variables import (
    MarketContext,
    PositionContext,
    StrategyRuntimeContext,
    StrategyVariable,
    VariableScope,
    VariableType,
)


def candles(closes: list[float]) -> list[Candle]:
    start = datetime(2026, 8, 30, 9, 15, tzinfo=UTC)

    result: list[Candle] = []

    for index, close in enumerate(closes):
        result.append(
            Candle(
                timestamp=start + timedelta(minutes=index),
                open=close,
                high=close + 1,
                low=close - 1,
                close=close,
                volume=1000,
            )
        )

    return result


def test_constant_expression() -> None:
    result = ExpressionEvaluator().evaluate(
        constant(42),
        candles([100]),
        0,
    )

    assert result == 42.0


def test_price_expression() -> None:
    data = candles([100, 105])

    result = ExpressionEvaluator().evaluate(
        price(PriceField.CLOSE),
        data,
        1,
    )

    assert result == 105.0


def test_indicator_expression() -> None:
    data = candles(list(range(100, 130)))

    result = ExpressionEvaluator().evaluate(
        indicator(
            "EMA",
            parameters={"period": 10},
        ),
        data,
        29,
    )

    assert result is not None


def test_comparison() -> None:
    data = candles([100, 105])

    condition = compare(
        price(PriceField.CLOSE),
        ">",
        constant(102),
    )

    evaluator = ConditionEvaluator()

    assert evaluator.evaluate(
        condition,
        data,
        0,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        1,
    ) is True


def test_cross_above() -> None:
    data = candles([100, 101, 103])

    condition = cross_above(
        price(PriceField.CLOSE),
        constant(102),
    )

    evaluator = ConditionEvaluator()

    assert evaluator.evaluate(
        condition,
        data,
        0,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        1,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        2,
    ) is True


def test_cross_below() -> None:
    data = candles([105, 103, 99])

    condition = cross_below(
        price(PriceField.CLOSE),
        constant(100),
    )

    evaluator = ConditionEvaluator()

    assert evaluator.evaluate(
        condition,
        data,
        1,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        2,
    ) is True


def test_cross_above_requires_previous_relationship() -> None:
    data = candles([103, 104, 105])

    condition = cross_above(
        price(PriceField.CLOSE),
        constant(100),
    )

    assert ConditionEvaluator().evaluate(
        condition,
        data,
        1,
    ) is False


def test_crossing_does_not_trigger_during_indicator_warmup() -> None:
    data = candles(list(range(100, 130)))

    condition = cross_above(
        price(PriceField.CLOSE),
        indicator(
            "SMA",
            parameters={"period": 10},
        ),
    )

    evaluator = ConditionEvaluator()

    assert evaluator.evaluate(
        condition,
        data,
        0,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        5,
    ) is False

    assert evaluator.evaluate(
        condition,
        data,
        9,
    ) is False


def test_logical_and() -> None:
    data = candles([105])

    condition = all_of(
        compare(
            price(PriceField.CLOSE),
            ">",
            constant(100),
        ),
        compare(
            price(PriceField.CLOSE),
            "<",
            constant(110),
        ),
    )

    assert ConditionEvaluator().evaluate(
        condition,
        data,
        0,
    ) is True


def test_variable_expression() -> None:
    data = candles([105])

    context = StrategyRuntimeContext(
        market=MarketContext(
            timestamp=data[0].timestamp,
            open=105,
            high=106,
            low=104,
            close=105,
        ),
        variables=(
            StrategyVariable(
                name="entry_limit",
                variable_type=VariableType.NUMBER,
                scope=VariableScope.STRATEGY,
                value=100,
            ),
        ),
    )

    condition = compare(
        price(PriceField.CLOSE),
        ">",
        variable("entry_limit"),
    )

    assert ConditionEvaluator().evaluate(
        condition,
        data,
        0,
        context,
    ) is True


def test_position_expression() -> None:
    data = candles([105])

    context = StrategyRuntimeContext(
        market=MarketContext(
            timestamp=data[0].timestamp,
            open=105,
            high=106,
            low=104,
            close=105,
        ),
        position=PositionContext(
            quantity=2,
            entry_price=100,
            current_price=105,
            average_price=100,
            realized_pnl=10,
            unrealized_pnl=10,
            entry_timestamp=data[0].timestamp,
        ),
    )

    evaluator = ExpressionEvaluator()

    assert evaluator.evaluate(
        position(PositionField.QUANTITY),
        data,
        0,
        context,
    ) == 2

    assert evaluator.evaluate(
        position(PositionField.ENTRY_PRICE),
        data,
        0,
        context,
    ) == 100

    assert evaluator.evaluate(
        position(PositionField.CURRENT_PRICE),
        data,
        0,
        context,
    ) == 105

    assert evaluator.evaluate(
        position(PositionField.AVERAGE_PRICE),
        data,
        0,
        context,
    ) == 100

    assert evaluator.evaluate(
        position(PositionField.REALIZED_PNL),
        data,
        0,
        context,
    ) == 10

    assert evaluator.evaluate(
        position(PositionField.UNREALIZED_PNL),
        data,
        0,
        context,
    ) == 10

    assert evaluator.evaluate(
        position(PositionField.UNREALIZED_PNL_PERCENT),
        data,
        0,
        context,
    ) == 5.0

    assert evaluator.evaluate(
        position(PositionField.OPEN),
        data,
        0,
        context,
    ) is True


def test_position_expression_requires_context() -> None:
    with pytest.raises(ValueError, match="Runtime context is required"):
        ExpressionEvaluator().evaluate(
            position(PositionField.QUANTITY),
            candles([100]),
            0,
        )


def test_unknown_expression_type_fails() -> None:
    evaluator = ExpressionEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            object(),  # type: ignore[arg-type]
            candles([100]),
            0,
        )
