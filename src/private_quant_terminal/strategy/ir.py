from dataclasses import dataclass
from datetime import datetime

from private_quant_terminal.strategy.enums import (
    ConditionOperator,
    OrderType,
    PositionSizingMethod,
    StopLossType,
    StrategyStatus,
    StrategyTimeframe,
    TakeProfitType,
)


@dataclass(frozen=True)
class StrategyCondition:
    """Declarative condition used by a strategy."""

    indicator: str
    operator: ConditionOperator
    value: float


@dataclass(frozen=True)
class PositionSizing:
    """Declarative position-sizing rule."""

    method: PositionSizingMethod
    value: float


@dataclass(frozen=True)
class StopLoss:
    """Declarative stop-loss rule."""

    type: StopLossType
    value: float | None = None


@dataclass(frozen=True)
class TakeProfit:
    """Declarative take-profit rule."""

    type: TakeProfitType
    value: float | None = None


@dataclass(frozen=True)
class ExecutionAssumptions:
    """Deterministic assumptions used by research and execution."""

    order_type: OrderType = OrderType.MARKET
    slippage_bps: float = 0.0
    transaction_cost_bps: float = 0.0


@dataclass(frozen=True)
class StrategyDefinition:
    """Canonical declarative representation of a strategy."""

    strategy_id: str
    name: str
    description: str
    instruments: tuple[str, ...]
    timeframe: StrategyTimeframe
    entry_conditions: tuple[StrategyCondition, ...]
    exit_conditions: tuple[StrategyCondition, ...]
    position_sizing: PositionSizing
    stop_loss: StopLoss
    take_profit: TakeProfit
    execution: ExecutionAssumptions
    status: StrategyStatus = StrategyStatus.DRAFT


@dataclass(frozen=True)
class StrategyVersion:
    """Immutable version of a strategy definition."""

    strategy_id: str
    version: int
    specification: StrategyDefinition
    created_at: datetime
