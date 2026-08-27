import pytest

from private_quant_terminal.brokers.execution_report import (
    ExecutionReport,
)
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.portfolio.drawdown import DrawdownCalculator
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)
from private_quant_terminal.portfolio.position_manager import (
    PositionManager,
)
from private_quant_terminal.portfolio.risk_calculator import (
    PortfolioRiskCalculator,
)
from private_quant_terminal.portfolio.valuation import (
    PortfolioValuationService,
)
from private_quant_terminal.services.portfolio import (
    PortfolioService,
)


class TestPortfolioSummary:
    @pytest.fixture
    def position_manager(self) -> PositionManager:
        return PositionManager()

    @pytest.fixture
    def service(
        self,
        position_manager: PositionManager,
    ) -> PortfolioService:
        return PortfolioService(
            position_manager=position_manager,
            valuation_service=PortfolioValuationService(
                position_manager
            ),
            risk_calculator=PortfolioRiskCalculator(),
            performance_calculator=PortfolioPerformanceCalculator(),
            drawdown_calculator=DrawdownCalculator(),
        )

    def test_returns_empty_portfolio_summary(
        self,
        service: PortfolioService,
    ) -> None:
        summary = service.summary(prices={})

        assert summary.snapshot.positions == ()
        assert summary.snapshot.realized_pnl == 0.0
        assert summary.snapshot.unrealized_pnl == 0.0
        assert summary.snapshot.total_pnl == 0.0
        assert summary.snapshot.open_position_count == 0

        assert summary.risk.gross_exposure == 0.0
        assert summary.risk.net_exposure == 0.0
        assert summary.risk.position_count == 0

        assert summary.closed_trade_count == 0
        assert summary.trading_performance.winning_trades == 0
        assert summary.trading_performance.losing_trades == 0

    def test_returns_summary_for_open_position(
        self,
        service: PortfolioService,
        position_manager: PositionManager,
    ) -> None:
        position_manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=2,
            price=22000.0,
            report=ExecutionReport(
                order_id="order-1",
                status=OrderStatus.FILLED,
                filled_quantity=2,
                remaining_quantity=0,
                average_price=22000.0,
            ),
        )

        summary = service.summary(
            prices={
                "NIFTY": 22500.0,
            },
        )

        assert summary.snapshot.open_position_count == 1
        assert summary.snapshot.unrealized_pnl == 1000.0
        assert summary.snapshot.total_pnl == 1000.0

        assert summary.risk.gross_exposure == 45000.0
        assert summary.risk.net_exposure == 45000.0
        assert summary.risk.long_exposure == 45000.0
        assert summary.risk.short_exposure == 0.0

        assert summary.closed_trade_count == 0

    def test_raises_for_missing_market_price(
        self,
        service: PortfolioService,
        position_manager: PositionManager,
    ) -> None:
        position_manager.apply_execution(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=1,
            price=22000.0,
            report=ExecutionReport(
                order_id="order-1",
                status=OrderStatus.FILLED,
                filled_quantity=1,
                remaining_quantity=0,
                average_price=22000.0,
            ),
        )

        with pytest.raises(
            ValueError,
            match="Missing market price for symbol: NIFTY",
        ):
            service.summary(prices={})
