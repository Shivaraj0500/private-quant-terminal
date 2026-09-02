from dataclasses import dataclass
from datetime import datetime

from private_quant_terminal.strategy.data_requirements import DataRequirement
from private_quant_terminal.strategy.enums import (
    ConditionOperator,
    OrderType,
    PositionSizingMethod,
    StopLossType,
    StrategyStatus,
    StrategyTimeframe,
    TakeProfitType,
)
from private_quant_terminal.strategy.positions import PositionGroup
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.session import StrategySession
from private_quant_terminal.strategy.variables import StrategyVariable


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
class StrategyIR:
    """Canonical strategy representation shared across execution modes."""

    strategy_id: str
    name: str
    description: str
    version: int
    status: StrategyStatus
    instruments: tuple[str, ...]
    timeframe: StrategyTimeframe
    variables: tuple[StrategyVariable, ...] = ()
    rules: tuple[StrategyRule, ...] = ()
    data_requirements: tuple[DataRequirement, ...] = ()
    position_groups: tuple[PositionGroup, ...] = ()
    session: StrategySession | None = None
    position_sizing: PositionSizing | None = None
    stop_loss: StopLoss | None = None
    take_profit: TakeProfit | None = None
    execution: ExecutionAssumptions = ExecutionAssumptions()

    def __post_init__(self) -> None:
        strategy_id = self.strategy_id.strip()
        name = self.name.strip()
        description = self.description.strip()

        if not strategy_id:
            raise ValueError("Strategy ID must not be empty.")

        if not name:
            raise ValueError("Strategy name must not be empty.")

        if not description:
            raise ValueError("Strategy description must not be empty.")

        if self.version <= 0:
            raise ValueError("Strategy version must be greater than zero.")

        if not self.instruments:
            raise ValueError("Strategy must contain at least one instrument.")

        normalized_instruments = tuple(
            instrument.strip().upper()
            for instrument in self.instruments
        )

        if any(not instrument for instrument in normalized_instruments):
            raise ValueError("Strategy instruments must not be empty.")

        if len(set(normalized_instruments)) != len(normalized_instruments):
            raise ValueError("Strategy instruments must be unique.")

        rule_ids = tuple(rule.rule_id for rule in self.rules)
        if len(set(rule_ids)) != len(rule_ids):
            raise ValueError("Strategy rule IDs must be unique.")

        if len(set(self.data_requirements)) != len(self.data_requirements):
            raise ValueError("Strategy data requirements must be unique.")

        group_ids = tuple(group.group_id for group in self.position_groups)
        if len(set(group_ids)) != len(group_ids):
            raise ValueError("Strategy position group IDs must be unique.")

        variable_names = tuple(
            variable.name.lower()
            for variable in self.variables
        )
        if len(set(variable_names)) != len(variable_names):
            raise ValueError("Strategy variable names must be unique.")

        object.__setattr__(self, "strategy_id", strategy_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "instruments", normalized_instruments)


@dataclass(frozen=True)
class StrategyVersion:
    """Immutable version of a strategy definition."""

    strategy_id: str
    version: int
    specification: StrategyDefinition
    created_at: datetime
