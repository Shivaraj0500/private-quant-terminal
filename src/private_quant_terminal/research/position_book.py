from __future__ import annotations

from private_quant_terminal.models.instrument import Instrument
from private_quant_terminal.research.simulation import (
    ResearchAccountingEngine,
    ResearchAccountingResult,
    ResearchFill,
    ResearchLegPosition,
)


class ResearchPositionBook:
    """Maintain deterministic multi-leg research positions."""

    def __init__(
        self,
        accounting: ResearchAccountingEngine | None = None,
    ) -> None:
        self._accounting = accounting or ResearchAccountingEngine()
        self._positions: dict[tuple[str, str], ResearchLegPosition] = {}
        self._realized_pnl = 0.0
        self._transaction_cost = 0.0

    def apply_fill(
        self,
        fill: ResearchFill,
    ) -> ResearchAccountingResult:
        """Apply one fill to its concrete strategy leg."""

        key = (fill.group_id, fill.instrument.identifier)
        position = self._positions.get(key)

        result = self._accounting.apply_fill(position, fill)

        if result.position is None:
            self._positions.pop(key, None)
        else:
            self._positions[key] = result.position

        self._realized_pnl += result.realized_pnl
        self._transaction_cost += result.transaction_cost

        return result

    def get_position(
        self,
        group_id: str,
        instrument: Instrument,
    ) -> ResearchLegPosition | None:
        """Return the open position for one strategy leg."""

        key = (group_id.strip(), instrument.identifier)
        return self._positions.get(key)

    def positions(self) -> tuple[ResearchLegPosition, ...]:
        """Return all currently open leg positions."""

        return tuple(self._positions.values())

    def positions_for_group(
        self,
        group_id: str,
    ) -> tuple[ResearchLegPosition, ...]:
        """Return all currently open legs in one strategy position group."""

        normalized_group_id = group_id.strip()

        return tuple(
            position
            for position in self._positions.values()
            if position.group_id == normalized_group_id
        )

    def open_position_count(self) -> int:
        """Return the number of currently open concrete leg positions."""

        return len(self._positions)

    def realized_pnl(self) -> float:
        """Return cumulative realized P&L across all open and closed legs."""

        return self._realized_pnl

    def transaction_cost(self) -> float:
        """Return cumulative transaction costs."""

        return self._transaction_cost

    def clear(self) -> None:
        """Clear all positions and accumulated accounting totals."""

        self._positions.clear()
        self._realized_pnl = 0.0
        self._transaction_cost = 0.0
