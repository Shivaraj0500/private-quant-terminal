import pytest

from private_quant_terminal.brokers.execution_report import (
    ExecutionReport,
)
from private_quant_terminal.brokers.order_side import OrderSide
from private_quant_terminal.brokers.order_status import OrderStatus
from private_quant_terminal.portfolio.drawdown import (
    DrawdownCalculator,
)
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


class TestPortfolioService:
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

    def test_returns_positions(
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

        positions = service.positions()

        assert len(positions) == 1
        assert positions[0].symbol == "NIFTY"
        assert positions[0].quantity == 2
        assert positions[0].average_price == 22000.0

    def test_returns_empty_positions(
        self,
        service: PortfolioService,
    ) -> None:
        positions = service.positions()

        assert positions == ()

    def test_returns_portfolio_snapshot(
        self,
        service: PortfolioService,
    ) -> None:
        snapshot = service.snapshot({})

        assert snapshot.positions == ()
        assert snapshot.realized_pnl == 0.0
        assert snapshot.unrealized_pnl == 0.0
        assert snapshot.total_pnl == 0.0
        assert snapshot.open_position_count == 0

    def test_returns_portfolio_risk(
        self,
        service: PortfolioService,
    ) -> None:
        risk = service.risk({})

        assert risk.gross_exposure == 0.0
        assert risk.net_exposure == 0.0
        assert risk.long_exposure == 0.0
        assert risk.short_exposure == 0.0
        assert risk.largest_position_weight == 0.0
        assert risk.position_count == 0

    def test_raises_for_missing_risk_price(
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
            service.risk({})

    def test_returns_portfolio_drawdown(
        self,
        service: PortfolioService,
    ) -> None:
        drawdown = service.drawdown(
            peak_value=100000.0,
            current_value=85000.0,
        )

        assert drawdown.peak_value == 100000.0
        assert drawdown.current_value == 85000.0
        assert drawdown.drawdown == 15000.0
        assert drawdown.drawdown_percent == 15.0

    def test_rejects_invalid_drawdown_peak(
        self,
        service: PortfolioService,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="peak_value must be greater than zero",
        ):
            service.drawdown(
                peak_value=0.0,
                current_value=1000.0,
            )


    def test_returns_risk_adjusted_metrics(
        self,
        service: PortfolioService,
    ) -> None:
        metrics = service.risk_adjusted(
            returns=(
                0.10,
                -0.05,
                0.15,
                0.00,
            ),
            max_drawdown=0.10,
        )

        assert metrics.sharpe_ratio == pytest.approx(
            0.6324555320,
        )
        assert metrics.downside_deviation == pytest.approx(
            0.025,
        )
        assert metrics.sortino_ratio == pytest.approx(
            2.0,
        )
        assert metrics.calmar_ratio == pytest.approx(
            2.0,
        )

    def test_returns_zero_risk_adjusted_metrics_for_empty_returns(
        self,
        service: PortfolioService,
    ) -> None:
        metrics = service.risk_adjusted(
            returns=(),
        )

        assert metrics.sharpe_ratio == 0.0
        assert metrics.sortino_ratio == 0.0
        assert metrics.downside_deviation == 0.0
        assert metrics.calmar_ratio == 0.0
