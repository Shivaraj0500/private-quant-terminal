from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.risk.limits import RiskLimits
from private_quant_terminal.risk.result import RiskResult


class RiskManager:
    """Validate order requests against configured portfolio risk limits."""

    def __init__(
        self,
        limits: RiskLimits,
        position_manager: PositionManager,
    ) -> None:
        self._limits = limits
        self._position_manager = position_manager

    def validate(self, order_request: OrderRequest) -> RiskResult:
        """Validate an order request against configured risk limits."""

        if order_request.quantity > self._limits.max_order_quantity:
            return RiskResult(
                approved=False,
                reason=(
                    "Order quantity exceeds configured maximum order quantity"
                ),
            )

        current_position = self._position_manager.get_position(
            order_request.symbol
        )
        current_quantity = (
            current_position.quantity
            if current_position is not None
            else 0
        )

        projected_quantity = self._projected_quantity(
            current_quantity=current_quantity,
            side=order_request.side,
            order_quantity=order_request.quantity,
        )

        if abs(projected_quantity) > self._limits.max_position_quantity:
            return RiskResult(
                approved=False,
                reason=(
                    "Order would exceed configured maximum position quantity"
                ),
            )

        if (
            current_position is None
            and order_request.quantity > 0
            and self._position_manager.open_position_count()
            >= self._limits.max_open_positions
        ):
            return RiskResult(
                approved=False,
                reason=(
                    "Order would exceed configured maximum open positions"
                ),
            )

        return RiskResult(approved=True)

    @staticmethod
    def _projected_quantity(
        current_quantity: int,
        side: OrderSide,
        order_quantity: int,
    ) -> int:
        if side is OrderSide.BUY:
            return current_quantity + order_quantity

        return current_quantity - order_quantity
