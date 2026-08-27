from math import isclose, isinf

from private_quant_terminal.portfolio.closed_trade import ClosedTrade
from private_quant_terminal.portfolio.performance_calculator import (
    PortfolioPerformanceCalculator,
)


class TestPortfolioPerformanceCalculator:
    def test_returns_zero_performance_for_no_closed_trades(self) -> None:
        calculator = PortfolioPerformanceCalculator()

        result = calculator.calculate(())

        assert result.realized_pnl == 0.0
        assert result.unrealized_pnl == 0.0
        assert result.total_pnl == 0.0
        assert result.winning_trades == 0
        assert result.losing_trades == 0
        assert result.win_rate == 0.0
        assert result.average_win == 0.0
        assert result.average_loss == 0.0
        assert result.profit_factor == 0.0

    def test_calculates_performance_for_winning_and_losing_trades(
        self,
    ) -> None:
        calculator = PortfolioPerformanceCalculator()

        closed_trades = (
            ClosedTrade(
                symbol="NIFTY",
                quantity=1,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=500.0,
            ),
            ClosedTrade(
                symbol="BANKNIFTY",
                quantity=1,
                entry_price=48000.0,
                exit_price=47000.0,
                realized_pnl=1000.0,
            ),
            ClosedTrade(
                symbol="FINNIFTY",
                quantity=1,
                entry_price=21000.0,
                exit_price=20800.0,
                realized_pnl=-200.0,
            ),
            ClosedTrade(
                symbol="MIDCPNIFTY",
                quantity=1,
                entry_price=12000.0,
                exit_price=11500.0,
                realized_pnl=-500.0,
            ),
        )

        result = calculator.calculate(closed_trades)

        assert result.realized_pnl == 800.0
        assert result.unrealized_pnl == 0.0
        assert result.total_pnl == 800.0
        assert result.winning_trades == 2
        assert result.losing_trades == 2
        assert result.win_rate == 50.0
        assert result.average_win == 750.0
        assert result.average_loss == -350.0

        assert isclose(
            result.profit_factor,
            1500.0 / 700.0,
            rel_tol=1e-9,
        )

    def test_calculates_performance_for_only_winning_trades(
        self,
    ) -> None:
        calculator = PortfolioPerformanceCalculator()

        closed_trades = (
            ClosedTrade(
                symbol="NIFTY",
                quantity=1,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=500.0,
            ),
            ClosedTrade(
                symbol="BANKNIFTY",
                quantity=1,
                entry_price=48000.0,
                exit_price=49000.0,
                realized_pnl=1000.0,
            ),
        )

        result = calculator.calculate(closed_trades)

        assert result.realized_pnl == 1500.0
        assert result.winning_trades == 2
        assert result.losing_trades == 0
        assert result.win_rate == 100.0
        assert result.average_win == 750.0
        assert result.average_loss == 0.0
        assert isinf(result.profit_factor)

    def test_calculates_performance_for_only_losing_trades(
        self,
    ) -> None:
        calculator = PortfolioPerformanceCalculator()

        closed_trades = (
            ClosedTrade(
                symbol="NIFTY",
                quantity=1,
                entry_price=22000.0,
                exit_price=21500.0,
                realized_pnl=-500.0,
            ),
            ClosedTrade(
                symbol="BANKNIFTY",
                quantity=1,
                entry_price=48000.0,
                exit_price=47000.0,
                realized_pnl=-1000.0,
            ),
        )

        result = calculator.calculate(closed_trades)

        assert result.realized_pnl == -1500.0
        assert result.winning_trades == 0
        assert result.losing_trades == 2
        assert result.win_rate == 0.0
        assert result.average_win == 0.0
        assert result.average_loss == -750.0
        assert result.profit_factor == 0.0

    def test_ignores_breakeven_trades_for_win_rate(
        self,
    ) -> None:
        calculator = PortfolioPerformanceCalculator()

        closed_trades = (
            ClosedTrade(
                symbol="NIFTY",
                quantity=1,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=500.0,
            ),
            ClosedTrade(
                symbol="BANKNIFTY",
                quantity=1,
                entry_price=48000.0,
                exit_price=48000.0,
                realized_pnl=0.0,
            ),
            ClosedTrade(
                symbol="FINNIFTY",
                quantity=1,
                entry_price=21000.0,
                exit_price=20800.0,
                realized_pnl=-200.0,
            ),
        )

        result = calculator.calculate(closed_trades)

        assert result.realized_pnl == 300.0
        assert result.winning_trades == 1
        assert result.losing_trades == 1
        assert result.win_rate == 50.0
        assert result.average_win == 500.0
        assert result.average_loss == -200.0
        assert result.profit_factor == 2.5
