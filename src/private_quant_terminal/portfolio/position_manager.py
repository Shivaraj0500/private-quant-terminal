from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.portfolio.closed_trade import ClosedTrade
from private_quant_terminal.portfolio.position import Position


class PositionManager:
    """Manage portfolio positions and completed trades from broker executions."""

    def __init__(self) -> None:
        """Initialize an empty position manager."""
        self._positions: dict[str, Position] = {}
        self._closed_trades: list[ClosedTrade] = []
        self._realized_pnl: float = 0.0

    def apply_execution(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float,
        report: ExecutionReport,
    ) -> Position | None:
        """Apply a filled execution to the position for a symbol."""
        if report.status is not OrderStatus.FILLED:
            return self.get_position(symbol)

        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if price <= 0:
            raise ValueError("price must be greater than zero")

        position = self._positions.get(symbol)

        if position is None:
            return self._open_position(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
            )

        return self._update_position(
            position=position,
            side=side,
            quantity=quantity,
            price=price,
        )

    def get_position(self, symbol: str) -> Position | None:
        """Return the current position for a symbol."""
        return self._positions.get(symbol)

    def open_position_count(self) -> int:
        """Return the number of currently open positions."""
        return len(self._positions)

    def positions(self) -> tuple[Position, ...]:
        """Return all currently open positions."""
        return tuple(self._positions.values())

    def closed_trades(self) -> tuple[ClosedTrade, ...]:
        """Return all completed closed trades."""
        return tuple(self._closed_trades)

    def closed_trade_count(self) -> int:
        """Return the number of completed closed trades."""
        return len(self._closed_trades)

    def realized_pnl(self) -> float:
        """Return total realized profit and loss."""
        return self._realized_pnl

    def clear(self) -> None:
        """Clear positions, closed trades, and realized profit and loss."""
        self._positions.clear()
        self._closed_trades.clear()
        self._realized_pnl = 0.0

    def _open_position(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float,
    ) -> Position:
        """Open a new long or short position."""
        signed_quantity = quantity

        if side is OrderSide.SELL:
            signed_quantity = -quantity

        position = Position(
            symbol=symbol,
            quantity=signed_quantity,
            average_price=price,
        )

        self._positions[symbol] = position

        return position

    def _update_position(
        self,
        position: Position,
        side: OrderSide,
        quantity: int,
        price: float,
    ) -> Position | None:
        """Update an existing position from a new execution."""
        signed_quantity = quantity

        if side is OrderSide.SELL:
            signed_quantity = -quantity

        current_quantity = position.quantity
        new_quantity = current_quantity + signed_quantity

        if self._same_direction(
            current_quantity=current_quantity,
            signed_quantity=signed_quantity,
        ):
            average_price = self._calculate_average_price(
                current_quantity=current_quantity,
                current_average_price=position.average_price,
                added_quantity=signed_quantity,
                added_price=price,
            )

            return self._store_position(
                symbol=position.symbol,
                quantity=new_quantity,
                average_price=average_price,
            )

        closing_quantity = min(
            abs(current_quantity),
            abs(signed_quantity),
        )

        realized_pnl = self._calculate_realized_pnl(
            current_quantity=current_quantity,
            average_price=position.average_price,
            quantity=closing_quantity,
            exit_price=price,
        )

        self._realized_pnl += realized_pnl

        self._closed_trades.append(
            ClosedTrade(
                symbol=position.symbol,
                quantity=closing_quantity,
                entry_price=position.average_price,
                exit_price=price,
                realized_pnl=realized_pnl,
            )
        )

        if new_quantity == 0:
            self._positions.pop(position.symbol)
            return None

        if abs(signed_quantity) < abs(current_quantity):
            average_price = position.average_price
        else:
            average_price = price

        return self._store_position(
            symbol=position.symbol,
            quantity=new_quantity,
            average_price=average_price,
        )

    def _store_position(
        self,
        symbol: str,
        quantity: int,
        average_price: float,
    ) -> Position:
        """Store and return a position."""
        position = Position(
            symbol=symbol,
            quantity=quantity,
            average_price=average_price,
        )

        self._positions[symbol] = position

        return position

    @staticmethod
    def _same_direction(
        current_quantity: int,
        signed_quantity: int,
    ) -> bool:
        """Return whether two quantities point in the same direction."""
        return (
            current_quantity > 0
            and signed_quantity > 0
        ) or (
            current_quantity < 0
            and signed_quantity < 0
        )

    @staticmethod
    def _calculate_average_price(
        current_quantity: int,
        current_average_price: float,
        added_quantity: int,
        added_price: float,
    ) -> float:
        """Calculate the weighted average entry price."""
        total_quantity = (
            abs(current_quantity)
            + abs(added_quantity)
        )

        return (
            (
                abs(current_quantity)
                * current_average_price
            )
            + (
                abs(added_quantity)
                * added_price
            )
        ) / total_quantity

    @staticmethod
    def _calculate_realized_pnl(
        current_quantity: int,
        average_price: float,
        quantity: int,
        exit_price: float,
    ) -> float:
        """Calculate realized profit or loss for a closed quantity."""
        if current_quantity > 0:
            return (
                exit_price - average_price
            ) * quantity

        return (
            average_price - exit_price
        ) * quantity
