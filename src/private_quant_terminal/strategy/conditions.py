from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.strategy.expressions import Expression


class ComparisonOperator(str, Enum):
    """Binary comparison operators."""

    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class LogicalOperator(str, Enum):
    """Boolean operators for condition groups."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class CrossingOperator(str, Enum):
    """Directional crossing operators."""

    CROSS_ABOVE = "CROSS_ABOVE"
    CROSS_BELOW = "CROSS_BELOW"


@dataclass(frozen=True)
class ComparisonCondition:
    """Compare two expressions."""

    left: Expression
    operator: ComparisonOperator
    right: Expression


@dataclass(frozen=True)
class CrossingCondition:
    """Detect one expression crossing another."""

    left: Expression
    operator: CrossingOperator
    right: Expression


@dataclass(frozen=True)
class LogicalCondition:
    """Combine one or more conditions recursively."""

    operator: LogicalOperator
    conditions: tuple[Condition, ...]


Condition = ComparisonCondition | CrossingCondition | LogicalCondition


def compare(
    left: Expression,
    operator: ComparisonOperator | str,
    right: Expression,
) -> ComparisonCondition:
    """Construct a comparison condition."""

    normalized_operator = (
        operator
        if isinstance(operator, ComparisonOperator)
        else ComparisonOperator(operator)
    )

    return ComparisonCondition(
        left=left,
        operator=normalized_operator,
        right=right,
    )


def cross_above(
    left: Expression,
    right: Expression,
) -> CrossingCondition:
    """Construct a cross-above condition."""

    return CrossingCondition(
        left=left,
        operator=CrossingOperator.CROSS_ABOVE,
        right=right,
    )


def cross_below(
    left: Expression,
    right: Expression,
) -> CrossingCondition:
    """Construct a cross-below condition."""

    return CrossingCondition(
        left=left,
        operator=CrossingOperator.CROSS_BELOW,
        right=right,
    )


def all_of(*conditions: Condition) -> LogicalCondition:
    """Require every supplied condition to be true."""

    if not conditions:
        raise ValueError("AND requires at least one condition.")

    return LogicalCondition(
        operator=LogicalOperator.AND,
        conditions=tuple(conditions),
    )


def any_of(*conditions: Condition) -> LogicalCondition:
    """Require at least one supplied condition to be true."""

    if not conditions:
        raise ValueError("OR requires at least one condition.")

    return LogicalCondition(
        operator=LogicalOperator.OR,
        conditions=tuple(conditions),
    )


def not_(condition: Condition) -> LogicalCondition:
    """Negate a condition."""

    return LogicalCondition(
        operator=LogicalOperator.NOT,
        conditions=(condition,),
    )
