import pytest

from private_quant_terminal.portfolio.position import Position
from private_quant_terminal.portfolio.snapshot import PortfolioSnapshot


class TestPortfolioSnapshot:
    def test_creates_snapshot(self) -> None:
        positions = (
            Position(
                symbol="NIFTY",
                quantity=50,
                average_price=22000.0,
            ),
        )

        snapshot = PortfolioSnapshot(
            positions=positions,
            realized_pnl=500.0,
            unrealized_pnl=250.0,
        )

        assert snapshot.positions == positions
        assert snapshot.realized_pnl == 500.0
        assert snapshot.unrealized_pnl == 250.0

    def test_calculates_total_pnl(self) -> None:
        snapshot = PortfolioSnapshot(
            positions=(),
            realized_pnl=1000.0,
            unrealized_pnl=-250.0,
        )

        assert snapshot.total_pnl == 750.0

    def test_returns_open_position_count(self) -> None:
        snapshot = PortfolioSnapshot(
            positions=(
                Position(
                    symbol="NIFTY",
                    quantity=50,
                    average_price=22000.0,
                ),
                Position(
                    symbol="BANKNIFTY",
                    quantity=-25,
                    average_price=48000.0,
                ),
            ),
            realized_pnl=0.0,
            unrealized_pnl=0.0,
        )

        assert snapshot.open_position_count == 2

    def test_snapshot_is_immutable(self) -> None:
        snapshot = PortfolioSnapshot(
            positions=(),
            realized_pnl=0.0,
            unrealized_pnl=0.0,
        )

        with pytest.raises(AttributeError):
            snapshot.realized_pnl = 100.0
