from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from private_quant_terminal.models.instrument import Instrument
from private_quant_terminal.strategy.actions import ActionType


class ResearchFillSide(str, Enum):
    """Economic side of a simulated historical fill."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class ResearchFill:
    """A deterministic historical fill produced by simulation."""

    timestamp: datetime
    group_id: str
    instrument: Instrument
    side: ResearchFillSide
    quantity: float
    price: float
    transaction_cost: float = 0.0
    action_type: ActionType = ActionType.ENTER

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Fill group ID must not be empty.")

        if self.quantity <= 0:
            raise ValueError("Fill quantity must be positive.")

        if self.price < 0:
            raise ValueError("Fill price cannot be negative.")

        if self.transaction_cost < 0:
            raise ValueError("Transaction cost cannot be negative.")

        object.__setattr__(self, "group_id", self.group_id.strip())


@dataclass(frozen=True)
class ResearchLegPosition:
    """Economic position for one concrete instrument leg."""

    group_id: str
    instrument: Instrument
    quantity: float
    average_price: float

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Position group ID must not be empty.")

        if self.quantity == 0:
            raise ValueError("Position quantity cannot be zero.")

        if self.average_price < 0:
            raise ValueError("Average price cannot be negative.")

        object.__setattr__(self, "group_id", self.group_id.strip())


@dataclass(frozen=True)
class ResearchActionEvent:
    """A canonical strategy action observed during research simulation."""

    timestamp: datetime
    action_type: ActionType
    group_id: str


@dataclass(frozen=True)
class ResearchSimulationStep:
    """Economic consequences produced at one historical timestamp."""

    timestamp: datetime
    action_events: tuple[ResearchActionEvent, ...] = ()
    fills: tuple[ResearchFill, ...] = ()
    positions: tuple[ResearchLegPosition, ...] = ()
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    transaction_cost: float = 0.0
    equity: float = 0.0


@dataclass(frozen=True)
class ResearchAccountingResult:
    """Result of applying one historical fill to an economic position."""

    position: ResearchLegPosition | None
    realized_pnl: float
    transaction_cost: float


class ResearchAccountingEngine:
    """Apply deterministic long and short fills to research positions."""

    def apply_fill(
        self,
        position: ResearchLegPosition | None,
        fill: ResearchFill,
    ) -> ResearchAccountingResult:
        """Apply one fill and return the resulting position and P&L."""

        if position is not None:
            if position.group_id != fill.group_id:
                raise ValueError(
                    "Fill group ID does not match the existing position."
                )

            if position.instrument.identifier != fill.instrument.identifier:
                raise ValueError(
                    "Fill instrument does not match the existing position."
                )

        if fill.side is ResearchFillSide.BUY:
            return self._apply_delta(position, fill, fill.quantity)

        if fill.side is ResearchFillSide.SELL:
            return self._apply_delta(position, fill, -fill.quantity)

        raise TypeError(
            f"Unsupported research fill side: {fill.side!r}"
        )

    def mark_to_market(
        self,
        position: ResearchLegPosition,
        market_price: float,
    ) -> float:
        """Calculate unrealized P&L for an open long or short position."""

        if market_price < 0:
            raise ValueError("Market price cannot be negative.")

        return (
            market_price - position.average_price
        ) * position.quantity

    def _apply_delta(
        self,
        position: ResearchLegPosition | None,
        fill: ResearchFill,
        delta: float,
    ) -> ResearchAccountingResult:
        if position is None:
            new_position = ResearchLegPosition(
                group_id=fill.group_id,
                instrument=fill.instrument,
                quantity=delta,
                average_price=fill.price,
            )
            return ResearchAccountingResult(
                position=new_position,
                realized_pnl=0.0,
                transaction_cost=fill.transaction_cost,
            )

        current_quantity = position.quantity

        # Same direction: increase the position using a weighted average.
        if current_quantity * delta > 0:
            total_quantity = current_quantity + delta
            average_price = (
                abs(current_quantity) * position.average_price
                + abs(delta) * fill.price
            ) / abs(total_quantity)

            new_position = ResearchLegPosition(
                group_id=position.group_id,
                instrument=position.instrument,
                quantity=total_quantity,
                average_price=average_price,
            )

            return ResearchAccountingResult(
                position=new_position,
                realized_pnl=0.0,
                transaction_cost=fill.transaction_cost,
            )

        # Opposite direction: close as much of the existing position as
        # possible, then open any remaining quantity at the fill price.
        closing_quantity = min(abs(current_quantity), abs(delta))

        if current_quantity > 0:
            realized_pnl = (
                fill.price - position.average_price
            ) * closing_quantity
        else:
            realized_pnl = (
                position.average_price - fill.price
            ) * closing_quantity

        remaining_quantity = current_quantity + delta

        if remaining_quantity == 0:
            new_position = None
        elif current_quantity * remaining_quantity > 0:
            # Partial close: the original average price remains unchanged.
            new_position = ResearchLegPosition(
                group_id=position.group_id,
                instrument=position.instrument,
                quantity=remaining_quantity,
                average_price=position.average_price,
            )
        else:
            # Full close plus reversal: the remaining position opens at
            # the current fill price.
            new_position = ResearchLegPosition(
                group_id=position.group_id,
                instrument=position.instrument,
                quantity=remaining_quantity,
                average_price=fill.price,
            )

        return ResearchAccountingResult(
            position=new_position,
            realized_pnl=realized_pnl,
            transaction_cost=fill.transaction_cost,
        )
