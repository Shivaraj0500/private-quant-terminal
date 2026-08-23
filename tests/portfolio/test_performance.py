import pytest

from private_quant_terminal.portfolio.performance import (
    PerformanceSnapshot,
)


class TestPerformanceSnapshot:
    def test_creates_performance_snapshot(self) -> None:
        snapshot = PerformanceSnapshot(
            realized_pnl=1000.0,
            unrealized_pnl=500.0,
            total_pnl=1500.0,
            winning_trades=8,
            losing_trades=2,
            win_rate=80.0,
            average_win=200.0,
            average_loss=-100.0,
            profit_factor=8.0,
        )

        assert snapshot.realized_pnl == 1000.0
        assert snapshot.unrealized_pnl == 500.0
        assert snapshot.total_pnl == 1500.0
        assert snapshot.winning_trades == 8
        assert snapshot.losing_trades == 2
        assert snapshot.win_rate == 80.0
        assert snapshot.average_win == 200.0
        assert snapshot.average_loss == -100.0
        assert snapshot.profit_factor == 8.0

    def test_rejects_negative_winning_trades(self) -> None:
        with pytest.raises(
            ValueError,
            match="winning_trades cannot be negative",
        ):
            PerformanceSnapshot(
                realized_pnl=0.0,
                unrealized_pnl=0.0,
                total_pnl=0.0,
                winning_trades=-1,
                losing_trades=0,
                win_rate=0.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=0.0,
            )

    def test_rejects_negative_losing_trades(self) -> None:
        with pytest.raises(
            ValueError,
            match="losing_trades cannot be negative",
        ):
            PerformanceSnapshot(
                realized_pnl=0.0,
                unrealized_pnl=0.0,
                total_pnl=0.0,
                winning_trades=0,
                losing_trades=-1,
                win_rate=0.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=0.0,
            )

    def test_rejects_invalid_win_rate(self) -> None:
        with pytest.raises(
            ValueError,
            match="win_rate must be between 0 and 100",
        ):
            PerformanceSnapshot(
                realized_pnl=0.0,
                unrealized_pnl=0.0,
                total_pnl=0.0,
                winning_trades=0,
                losing_trades=0,
                win_rate=101.0,
                average_win=0.0,
                average_loss=0.0,
                profit_factor=0.0,
            )