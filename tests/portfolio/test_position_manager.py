import pytest

from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.portfolio.position_manager import PositionManager


def make_report(
    status: OrderStatus = OrderStatus.FILLED,
) -> ExecutionReport:
    return ExecutionReport(
        order_id="ORDER-1",
        status=status,
        filled_quantity=10,
        remaining_quantity=0,
        average_price=25000.0,
    )


class TestPositionManager:
    def test_starts_with_no_positions(self) -> None:
        manager = PositionManager()

        assert manager.positions() == ()
        assert manager.realized_pnl() == 0.0

    def test_opens_long_position(self) -> None:
        manager = PositionManager()

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=25000.0,
            report=make_report(),
        )

        assert position is not None
        assert position.symbol == "NIFTY"
        assert position.quantity == 10
        assert position.average_price == 25000.0

    def test_opens_short_position(self) -> None:
        manager = PositionManager()

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=25000.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == -10
        assert position.average_price == 25000.0

    def test_get_position_returns_none_for_unknown_symbol(self) -> None:
        manager = PositionManager()

        assert manager.get_position("UNKNOWN") is None

    def test_non_filled_execution_does_not_create_position(self) -> None:
        manager = PositionManager()

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=25000.0,
            report=make_report(OrderStatus.REJECTED),
        )

        assert position is None
        assert manager.positions() == ()

    def test_rejects_zero_quantity_for_filled_execution(self) -> None:
        manager = PositionManager()

        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            manager.apply_execution(
                symbol="NIFTY",
                side=OrderSide.BUY,
                quantity=0,
                price=25000.0,
                report=make_report(),
            )

    def test_rejects_negative_quantity_for_filled_execution(self) -> None:
        manager = PositionManager()

        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            manager.apply_execution(
                symbol="NIFTY",
                side=OrderSide.BUY,
                quantity=-10,
                price=25000.0,
                report=make_report(),
            )

    def test_rejects_zero_price_for_filled_execution(self) -> None:
        manager = PositionManager()

        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            manager.apply_execution(
                symbol="NIFTY",
                side=OrderSide.BUY,
                quantity=10,
                price=0.0,
                report=make_report(),
            )

    def test_rejects_negative_price_for_filled_execution(self) -> None:
        manager = PositionManager()

        with pytest.raises(
            ValueError,
            match="price must be greater than zero",
        ):
            manager.apply_execution(
                symbol="NIFTY",
                side=OrderSide.BUY,
                quantity=10,
                price=-25000.0,
                report=make_report(),
            )

    def test_adds_to_existing_long_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == 20
        assert position.average_price == 110.0

    def test_adds_to_existing_short_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == -20
        assert position.average_price == 110.0

    def test_partially_closes_long_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=4,
            price=120.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == 6
        assert position.average_price == 100.0
        assert manager.realized_pnl() == 80.0

    def test_fully_closes_long_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        assert position is None
        assert manager.get_position("NIFTY") is None
        assert manager.realized_pnl() == 200.0

    def test_partially_closes_short_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=4,
            price=100.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == -6
        assert position.average_price == 120.0
        assert manager.realized_pnl() == 80.0

    def test_fully_closes_short_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        assert position is None
        assert manager.get_position("NIFTY") is None
        assert manager.realized_pnl() == 200.0

    def test_reverses_long_position_to_short_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=15,
            price=120.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == -5
        assert position.average_price == 120.0
        assert manager.realized_pnl() == 200.0

    def test_reverses_short_position_to_long_position(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        position = manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=15,
            price=100.0,
            report=make_report(),
        )

        assert position is not None
        assert position.quantity == 5
        assert position.average_price == 100.0
        assert manager.realized_pnl() == 200.0

    def test_positions_returns_multiple_open_positions(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        manager.apply_execution(
            symbol="BANKNIFTY",
            side=OrderSide.SELL,
            quantity=5,
            price=200.0,
            report=make_report(),
        )

        positions = manager.positions()

        assert len(positions) == 2
        assert positions[0].symbol == "NIFTY"
        assert positions[1].symbol == "BANKNIFTY"

    def test_clear_removes_positions_and_realized_pnl(self) -> None:
        manager = PositionManager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=make_report(),
        )

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=120.0,
            report=make_report(),
        )

        manager.clear()

        assert manager.positions() == ()
        assert manager.realized_pnl() == 0.0


class TestPositionManagerOpenPositionCount:
    def test_returns_zero_when_no_positions_exist(self) -> None:
        manager = PositionManager()

        assert manager.open_position_count() == 0

    def test_counts_real_open_positions(self) -> None:
        manager = PositionManager()

        report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=100.0,
        )

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=report,
        )
        manager.apply_execution(
            symbol="BANKNIFTY",
            side=OrderSide.SELL,
            quantity=5,
            price=200.0,
            report=report,
        )

        assert manager.open_position_count() == 2

    def test_closed_position_is_not_counted(self) -> None:
        manager = PositionManager()

        report = ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=100.0,
        )

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=report,
        )
        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=110.0,
            report=report,
        )

        assert manager.open_position_count() == 0
