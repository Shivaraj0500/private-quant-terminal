from __future__ import annotations

from collections.abc import Sequence

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.canonical_indicator_engine import (
    CanonicalIndicatorEngine,
)
from private_quant_terminal.strategy.conditions import (
    ComparisonCondition,
    ComparisonOperator,
    Condition,
    CrossingCondition,
    CrossingOperator,
    LogicalCondition,
    LogicalOperator,
)
from private_quant_terminal.strategy.expressions import (
    ConstantExpression,
    Expression,
    IndicatorExpression,
    PriceExpression,
    TimeExpression,
    TimeField,
    VariableExpression,
)
from private_quant_terminal.strategy.indicator_registry import (
    IndicatorRegistry,
)
from private_quant_terminal.strategy.indicators import (
    price_series,
)
from private_quant_terminal.strategy.variables import (
    StrategyRuntimeContext,
)


class ExpressionEvaluator:
    """Resolve strategy expressions against deterministic market data."""

    def __init__(
        self,
        indicator_engine: CanonicalIndicatorEngine | None = None,
    ) -> None:
        self._indicator_engine = (
            indicator_engine if indicator_engine is not None else self._default_indicator_engine()
        )

    @staticmethod
    def _default_indicator_engine() -> CanonicalIndicatorEngine:
        return CanonicalIndicatorEngine(IndicatorRegistry.with_builtin_provider())

    def evaluate(
        self,
        expression: Expression,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None = None,
    ) -> object:
        """Evaluate an expression at a specific candle index."""

        if index < 0 or index >= len(candles):
            raise IndexError(f"candle index out of range: {index}")

        if isinstance(expression, ConstantExpression):
            return expression.value

        if isinstance(expression, PriceExpression):
            return self._price(
                expression,
                candles,
                index,
            )

        if isinstance(expression, IndicatorExpression):
            result = self._indicator_engine.calculate(
                expression,
                candles,
            )

            return result.output(expression.output).value_at(index)

        if isinstance(expression, TimeExpression):
            return self._time(
                expression,
                candles[index],
            )

        if isinstance(expression, VariableExpression):
            if context is None:
                raise ValueError("Runtime context is required for variable expressions.")

            return context.resolve(expression.name)

        raise TypeError(f"Unsupported expression: {type(expression).__name__}")

    @staticmethod
    def _price(
        expression: PriceExpression,
        candles: Sequence[Candle],
        index: int,
    ) -> float:
        return float(
            price_series(
                candles,
                expression.field,
            ).value_at(index)
        )

    @staticmethod
    def _time(
        expression: TimeExpression,
        candle: Candle,
    ) -> object:
        timestamp = candle.timestamp

        if expression.field is TimeField.TIMESTAMP:
            return timestamp

        if expression.field is TimeField.TIME_OF_DAY:
            return timestamp.time()

        if expression.field is TimeField.DAY_OF_WEEK:
            return timestamp.weekday()

        raise TypeError(f"Unsupported time field: {expression.field}")


class ConditionEvaluator:
    """Evaluate deterministic strategy conditions."""

    def __init__(
        self,
        expression_evaluator: ExpressionEvaluator | None = None,
    ) -> None:
        self._expressions = (
            expression_evaluator if expression_evaluator is not None else ExpressionEvaluator()
        )

    def evaluate(
        self,
        condition: Condition,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None = None,
    ) -> bool:
        if isinstance(condition, ComparisonCondition):
            return self._comparison(
                condition,
                candles,
                index,
                context,
            )

        if isinstance(condition, CrossingCondition):
            return self._crossing(
                condition,
                candles,
                index,
                context,
            )

        if isinstance(condition, LogicalCondition):
            return self._logical(
                condition,
                candles,
                index,
                context,
            )

        raise TypeError(f"Unsupported condition: {type(condition).__name__}")

    def _comparison(
        self,
        condition: ComparisonCondition,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None,
    ) -> bool:
        left = self._expressions.evaluate(
            condition.left,
            candles,
            index,
            context,
        )

        right = self._expressions.evaluate(
            condition.right,
            candles,
            index,
            context,
        )

        if left is None or right is None:
            return False

        try:
            if condition.operator is ComparisonOperator.GREATER_THAN:
                return bool(left > right)

            if condition.operator is ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return bool(left >= right)

            if condition.operator is ComparisonOperator.LESS_THAN:
                return bool(left < right)

            if condition.operator is ComparisonOperator.LESS_THAN_OR_EQUAL:
                return bool(left <= right)

            if condition.operator is ComparisonOperator.EQUAL:
                return bool(left == right)

            if condition.operator is ComparisonOperator.NOT_EQUAL:
                return bool(left != right)

        except TypeError:
            return False

        raise TypeError(f"Unsupported comparison operator: {condition.operator}")

    def _crossing(
        self,
        condition: CrossingCondition,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None,
    ) -> bool:
        # A crossing needs both a previous and current candle.
        if index == 0:
            return False

        current_left = self._expressions.evaluate(
            condition.left,
            candles,
            index,
            context,
        )

        current_right = self._expressions.evaluate(
            condition.right,
            candles,
            index,
            context,
        )

        previous_left = self._expressions.evaluate(
            condition.left,
            candles,
            index - 1,
            context,
        )

        previous_right = self._expressions.evaluate(
            condition.right,
            candles,
            index - 1,
            context,
        )

        # Indicator warm-up or unavailable data means no signal.
        if (
            current_left is None
            or current_right is None
            or previous_left is None
            or previous_right is None
        ):
            return False

        if condition.operator is CrossingOperator.CROSS_ABOVE:
            return previous_left <= previous_right and current_left > current_right

        if condition.operator is CrossingOperator.CROSS_BELOW:
            return previous_left >= previous_right and current_left < current_right

        raise TypeError(f"Unsupported crossing operator: {condition.operator}")

    def _logical(
        self,
        condition: LogicalCondition,
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None,
    ) -> bool:
        if condition.operator is LogicalOperator.AND:
            return all(
                self.evaluate(
                    child,
                    candles,
                    index,
                    context,
                )
                for child in condition.conditions
            )

        if condition.operator is LogicalOperator.OR:
            return any(
                self.evaluate(
                    child,
                    candles,
                    index,
                    context,
                )
                for child in condition.conditions
            )

        if condition.operator is LogicalOperator.NOT:
            if len(condition.conditions) != 1:
                raise ValueError("NOT must contain exactly one condition.")

            return not self.evaluate(
                condition.conditions[0],
                candles,
                index,
                context,
            )

        raise TypeError(f"Unsupported logical operator: {condition.operator}")
