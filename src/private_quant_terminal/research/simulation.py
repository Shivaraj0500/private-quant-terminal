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


class ResearchSimulationAdapter:
    """Translate supported canonical actions into deterministic research fills.

    Phase 8.6 deliberately supports only single-leg non-option entries and
    exits. Strategy-condition semantics remain owned by the canonical
    strategy runtime.
    """

    def __init__(self, accounting: ResearchAccountingEngine | None = None) -> None:
        self._accounting = accounting or ResearchAccountingEngine()

    def enter(
        self,
        *,
        timestamp: datetime,
        action,
        instrument: Instrument,
        price: float,
        quantity: float,
        transaction_cost: float = 0.0,
    ) -> tuple[ResearchActionEvent, ResearchFill, ResearchAccountingResult]:
        from private_quant_terminal.strategy.actions import EnterAction
        from private_quant_terminal.strategy.positions import (
            LegAction,
            LegInstrumentType,
        )

        if not isinstance(action, EnterAction):
            raise TypeError("enter() requires an EnterAction.")

        position = action.position

        if len(position.legs) != 1:
            raise ValueError(
                "Phase 8.6 research entry requires exactly one strategy leg."
            )

        leg = position.legs[0]

        if leg.instrument_type is LegInstrumentType.OPTION:
            raise ValueError(
                "Phase 8.6 research entry does not support option legs."
            )

        if leg.action is LegAction.BUY:
            side = ResearchFillSide.BUY
        elif leg.action is LegAction.SELL:
            side = ResearchFillSide.SELL
        else:
            raise ValueError(
                f"Unsupported strategy leg action: {leg.action!r}."
            )

        fill = ResearchFill(
            timestamp=timestamp,
            group_id=position.group_id,
            instrument=instrument,
            side=side,
            quantity=quantity,
            price=price,
            transaction_cost=transaction_cost,
            action_type=action.action_type,
        )

        result = self._accounting.apply_fill(None, fill)

        return (
            ResearchActionEvent(
                timestamp=timestamp,
                action_type=action.action_type,
                group_id=position.group_id,
            ),
            fill,
            result,
        )

    def exit(
        self,
        *,
        timestamp: datetime,
        action,
        position: ResearchLegPosition,
        price: float,
        quantity: float | None = None,
        transaction_cost: float = 0.0,
    ) -> tuple[ResearchActionEvent, ResearchFill, ResearchAccountingResult]:
        from private_quant_terminal.strategy.actions import ExitAction

        if not isinstance(action, ExitAction):
            raise TypeError("exit() requires an ExitAction.")

        if position.group_id != action.group_id:
            raise ValueError("Exit action group does not match the position.")

        close_quantity = (
            abs(position.quantity) if quantity is None else quantity
        )

        if close_quantity <= 0:
            raise ValueError("Exit quantity must be positive.")

        if close_quantity > abs(position.quantity):
            raise ValueError(
                "Exit quantity cannot exceed the existing position quantity."
            )

        side = (
            ResearchFillSide.SELL
            if position.quantity > 0
            else ResearchFillSide.BUY
        )

        fill = ResearchFill(
            timestamp=timestamp,
            group_id=action.group_id,
            instrument=position.instrument,
            side=side,
            quantity=close_quantity,
            price=price,
            transaction_cost=transaction_cost,
            action_type=action.action_type,
        )

        result = self._accounting.apply_fill(position, fill)

        return (
            ResearchActionEvent(
                timestamp=timestamp,
                action_type=action.action_type,
                group_id=action.group_id,
            ),
            fill,
            result,
        )
