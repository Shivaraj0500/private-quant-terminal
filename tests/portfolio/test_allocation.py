import pytest

from private_quant_terminal.portfolio.allocation import Allocation


class TestAllocation:
    def test_calculates_position_weight(self) -> None:
        allocation = Allocation(
            symbol="NIFTY",
            market_value=250000.0,
            portfolio_value=1000000.0,
        )

        assert allocation.weight == 0.25

    def test_calculates_full_portfolio_weight(self) -> None:
        allocation = Allocation(
            symbol="BANKNIFTY",
            market_value=500000.0,
            portfolio_value=500000.0,
        )

        assert allocation.weight == 1.0

    def test_calculates_zero_market_value_weight(self) -> None:
        allocation = Allocation(
            symbol="NIFTY",
            market_value=0.0,
            portfolio_value=1000000.0,
        )

        assert allocation.weight == 0.0

    def test_rejects_zero_portfolio_value(self) -> None:
        allocation = Allocation(
            symbol="NIFTY",
            market_value=100000.0,
            portfolio_value=0.0,
        )

        with pytest.raises(
            ValueError,
            match="portfolio_value must be greater than zero",
        ):
            _ = allocation.weight

    def test_rejects_negative_portfolio_value(self) -> None:
        allocation = Allocation(
            symbol="NIFTY",
            market_value=100000.0,
            portfolio_value=-500000.0,
        )

        with pytest.raises(
            ValueError,
            match="portfolio_value must be greater than zero",
        ):
            _ = allocation.weight