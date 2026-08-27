import pytest

from private_quant_terminal.portfolio.closed_trade import (
    ClosedTrade,
)


class TestClosedTrade:
    def test_creates_closed_trade(self) -> None:
        trade = ClosedTrade(
            symbol="NIFTY",
            quantity=10,
            entry_price=22000.0,
            exit_price=22500.0,
            realized_pnl=5000.0,
        )

        assert trade.symbol == "NIFTY"
        assert trade.quantity == 10
        assert trade.entry_price == 22000.0
        assert trade.exit_price == 22500.0
        assert trade.realized_pnl == 5000.0

    def test_rejects_empty_symbol(self) -> None:
        with pytest.raises(
            ValueError,
            match="symbol must not be empty",
        ):
            ClosedTrade(
                symbol="",
                quantity=10,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=5000.0,
            )

    def test_rejects_whitespace_symbol(self) -> None:
        with pytest.raises(
            ValueError,
            match="symbol must not be empty",
        ):
            ClosedTrade(
                symbol="   ",
                quantity=10,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=5000.0,
            )

    def test_rejects_zero_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=0,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=0.0,
            )

    def test_rejects_negative_quantity(self) -> None:
        with pytest.raises(
            ValueError,
            match="quantity must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=-1,
                entry_price=22000.0,
                exit_price=22500.0,
                realized_pnl=-500.0,
            )

    def test_rejects_zero_entry_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="entry_price must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=10,
                entry_price=0.0,
                exit_price=22500.0,
                realized_pnl=5000.0,
            )

    def test_rejects_negative_entry_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="entry_price must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=10,
                entry_price=-22000.0,
                exit_price=22500.0,
                realized_pnl=5000.0,
            )

    def test_rejects_zero_exit_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="exit_price must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=10,
                entry_price=22000.0,
                exit_price=0.0,
                realized_pnl=5000.0,
            )

    def test_rejects_negative_exit_price(self) -> None:
        with pytest.raises(
            ValueError,
            match="exit_price must be greater than zero",
        ):
            ClosedTrade(
                symbol="NIFTY",
                quantity=10,
                entry_price=22000.0,
                exit_price=-22500.0,
                realized_pnl=-5000.0,
            )
