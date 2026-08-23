from private_quant_terminal.brokers.execution_report import ExecutionReport
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.portfolio.position_manager import PositionManager
from private_quant_terminal.portfolio.valuation import PortfolioValuationService


class TestPortfolioValuationService:
    def _create_position_manager(self) -> PositionManager:
        return PositionManager()

    def _filled_report(self) -> ExecutionReport:
        return ExecutionReport(
            order_id="ORDER-1",
            status=OrderStatus.FILLED,
            filled_quantity=10,
            remaining_quantity=0,
            average_price=100.0,
        )

    def test_returns_empty_portfolio_snapshot(self) -> None:
        manager = self._create_position_manager()
        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(prices={})

        assert snapshot.positions == ()
        assert snapshot.realized_pnl == 0.0
        assert snapshot.unrealized_pnl == 0.0
        assert snapshot.total_pnl == 0.0

    def test_calculates_long_position_profit(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={"NIFTY": 110.0},
        )

        assert snapshot.unrealized_pnl == 100.0

    def test_calculates_long_position_loss(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={"NIFTY": 90.0},
        )

        assert snapshot.unrealized_pnl == -100.0

    def test_calculates_short_position_profit(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={"NIFTY": 90.0},
        )

        assert snapshot.unrealized_pnl == 100.0

    def test_calculates_short_position_loss(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={"NIFTY": 110.0},
        )

        assert snapshot.unrealized_pnl == -100.0

    def test_combines_multiple_position_pnl(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        manager.apply_execution(
            symbol="BANKNIFTY",
            side=OrderSide.SELL,
            quantity=5,
            price=200.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={
                "NIFTY": 110.0,
                "BANKNIFTY": 180.0,
            },
        )

        assert snapshot.unrealized_pnl == 200.0

    def test_uses_average_price_when_market_price_is_missing(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(prices={})

        assert snapshot.unrealized_pnl == 0.0

    def test_includes_realized_and_unrealized_pnl(self) -> None:
        manager = self._create_position_manager()

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=10,
            price=100.0,
            report=self._filled_report(),
        )

        manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=5,
            price=120.0,
            report=self._filled_report(),
        )

        service = PortfolioValuationService(manager)

        snapshot = service.snapshot(
            prices={"NIFTY": 110.0},
        )

        assert snapshot.realized_pnl == 100.0
        assert snapshot.unrealized_pnl == 50.0
        assert snapshot.total_pnl == 150.0
