from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExpressionType(str, Enum):
    """Kinds of values that can participate in strategy expressions."""

    CONSTANT = "CONSTANT"
    PRICE = "PRICE"
    INDICATOR = "INDICATOR"
    TIME = "TIME"
    VARIABLE = "VARIABLE"


class PriceField(str, Enum):
    """OHLCV fields available from a market candle."""

    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"


class TimeField(str, Enum):
    """Time values exposed to strategy expressions."""

    TIMESTAMP = "timestamp"
    TIME_OF_DAY = "time_of_day"
    DAY_OF_WEEK = "day_of_week"


@dataclass(frozen=True)
class ConstantExpression:
    """A literal numeric value."""

    value: float

    @property
    def expression_type(self) -> ExpressionType:
        return ExpressionType.CONSTANT


@dataclass(frozen=True)
class PriceExpression:
    """A reference to a market price field."""

    field: PriceField

    @property
    def expression_type(self) -> ExpressionType:
        return ExpressionType.PRICE


@dataclass(frozen=True)
class IndicatorExpression:
    """A parameterized technical indicator."""

    name: str
    parameters: tuple[tuple[str, float], ...] = ()
    timeframe: str | None = None

    @property
    def expression_type(self) -> ExpressionType:
        return ExpressionType.INDICATOR


@dataclass(frozen=True)
class TimeExpression:
    """A reference to a timestamp-related value."""

    field: TimeField

    @property
    def expression_type(self) -> ExpressionType:
        return ExpressionType.TIME


@dataclass(frozen=True)
class VariableExpression:
    """A reference to a strategy variable."""

    name: str

    @property
    def expression_type(self) -> ExpressionType:
        return ExpressionType.VARIABLE


Expression = (
    ConstantExpression
    | PriceExpression
    | IndicatorExpression
    | TimeExpression
    | VariableExpression
)


def constant(value: float) -> ConstantExpression:
    return ConstantExpression(value=float(value))


def price(field: PriceField | str) -> PriceExpression:
    return PriceExpression(
        field=field if isinstance(field, PriceField) else PriceField(field),
    )


def indicator(
    name: str,
    *,
    parameters: dict[str, float] | None = None,
    timeframe: str | None = None,
) -> IndicatorExpression:
    normalized_parameters = tuple(
        sorted(
            (
                str(key),
                float(value),
            )
            for key, value in (parameters or {}).items()
        )
    )

    return IndicatorExpression(
        name=name.strip().upper(),
        parameters=normalized_parameters,
        timeframe=timeframe,
    )


def time_value(field: TimeField | str) -> TimeExpression:
    return TimeExpression(
        field=field if isinstance(field, TimeField) else TimeField(field),
    )


def variable(name: str) -> VariableExpression:
    normalized = name.strip()

    if not normalized:
        raise ValueError("Variable name must not be empty.")

    return VariableExpression(name=normalized)
