from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.portfolio.snapshot import PortfolioSnapshot


class PortfolioValuationService:
    """Calculate portfolio valuation and profit and loss."""

    def __init__(self, position_manager: PositionManager) -> None:
        """Initialize the valuation service."""
        self._position_manager = position_manager

    def snapshot(
        self,
        prices: dict[str, float],
    ) -> PortfolioSnapshot:
        """Create a portfolio snapshot using current market prices."""
        positions = self._position_manager.positions()

        unrealized_pnl = sum(
            self._calculate_unrealized_pnl(
                quantity=position.quantity,
                average_price=position.average_price,
                current_price=prices.get(
                    position.symbol,
                    position.average_price,
                ),
            )
            for position in positions
        )

        return PortfolioSnapshot(
            positions=positions,
            realized_pnl=self._position_manager.realized_pnl(),
            unrealized_pnl=unrealized_pnl,
        )

    @staticmethod
    def _calculate_unrealized_pnl(
        quantity: int,
        average_price: float,
        current_price: float,
    ) -> float:
        """Calculate unrealized profit or loss for a position."""
        return (
            current_price - average_price
        ) * quantity
