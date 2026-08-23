from private_quant_terminal.brokers.order_request import OrderRequest
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_type import OrderType
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.risk.limits import RiskLimits
from private_quant_terminal.risk.manager import RiskManager


def create_manager(
    *,
    max_position_quantity: int = 100,
    max_order_quantity: int = 50,
    max_open_positions: int = 2,
) -> tuple[RiskManager, PositionManager]:
    position_manager = PositionManager()

    limits = RiskLimits(
        max_position_quantity=max_position_quantity,
        max_order_quantity=max_order_quantity,
        max_open_positions=max_open_positions,
        max_daily_loss=10000.0,
    )

    return (
        RiskManager(
            limits=limits,
            position_manager=position_manager,
        ),
        position_manager,
    )


def create_order(
    *,
    symbol: str = "NIFTY",
    quantity: int = 10,
    side: OrderSide = OrderSide.BUY,
) -> OrderRequest:
    return OrderRequest(
        symbol=symbol,
        quantity=quantity,
        side=side,
        order_type=OrderType.MARKET,
    )


class TestRiskManager:
    def test_approves_valid_order(self) -> None:
        manager, _ = create_manager()

        result = manager.validate(create_order())

        assert result.approved is True
        assert result.reason is None

    def test_rejects_order_above_maximum_order_quantity(self) -> None:
        manager, _ = create_manager(max_order_quantity=10)

        result = manager.validate(create_order(quantity=11))

        assert result.approved is False
        assert (
            result.reason
            == "Order quantity exceeds configured maximum order quantity"
        )

    def test_approves_order_at_maximum_order_quantity(self) -> None:
        manager, _ = create_manager(max_order_quantity=10)

        result = manager.validate(create_order(quantity=10))

        assert result.approved is True

    def test_approves_position_at_maximum_position_quantity(self) -> None:
        manager, position_manager = create_manager(
            max_position_quantity=100,
            max_order_quantity=100,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 90},
        )()

        result = manager.validate(create_order(quantity=10))

        assert result.approved is True

    def test_rejects_order_that_exceeds_maximum_long_position(self) -> None:
        manager, position_manager = create_manager(
            max_position_quantity=100,
            max_order_quantity=50,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 80},
        )()

        result = manager.validate(create_order(quantity=30))

        assert result.approved is False
        assert (
            result.reason
            == "Order would exceed configured maximum position quantity"
        )

    def test_rejects_order_that_exceeds_maximum_short_position(self) -> None:
        manager, position_manager = create_manager(
            max_position_quantity=100,
            max_order_quantity=50,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": -80},
        )()

        result = manager.validate(
            create_order(
                quantity=30,
                side=OrderSide.SELL,
            )
        )

        assert result.approved is False
        assert (
            result.reason
            == "Order would exceed configured maximum position quantity"
        )

    def test_allows_order_that_reduces_existing_position(self) -> None:
        manager, position_manager = create_manager(
            max_position_quantity=100,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 100},
        )()

        result = manager.validate(
            create_order(
                quantity=50,
                side=OrderSide.SELL,
            )
        )

        assert result.approved is True

    def test_rejects_new_position_when_open_position_limit_reached(self) -> None:
        manager, position_manager = create_manager(
            max_open_positions=2,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 10},
        )()
        position_manager._positions["BANKNIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 10},
        )()

        result = manager.validate(
            create_order(
                symbol="RELIANCE",
                quantity=10,
            )
        )

        assert result.approved is False
        assert (
            result.reason
            == "Order would exceed configured maximum open positions"
        )

    def test_allows_existing_symbol_when_open_position_limit_reached(self) -> None:
        manager, position_manager = create_manager(
            max_open_positions=2,
        )

        position_manager._positions["NIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 10},
        )()
        position_manager._positions["BANKNIFTY"] = type(
            "PositionStub",
            (),
            {"quantity": 10},
        )()

        result = manager.validate(
            create_order(
                symbol="NIFTY",
                quantity=10,
            )
        )

        assert result.approved is True
