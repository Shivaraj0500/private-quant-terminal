import pytest

from private_quant_terminal.portfolio.rebalancing import Rebalancing


class TestRebalancing:
    def test_calculates_current_weight(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=250000.0,
            portfolio_value=1000000.0,
            target_weight=0.30,
        )

        assert rebalancing.current_weight == 0.25

    def test_calculates_target_value(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=250000.0,
            portfolio_value=1000000.0,
            target_weight=0.30,
        )

        assert rebalancing.target_value == 300000.0

    def test_returns_positive_adjustment_when_buying_is_required(
        self,
    ) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=250000.0,
            portfolio_value=1000000.0,
            target_weight=0.30,
        )

        assert rebalancing.adjustment == 50000.0

    def test_returns_negative_adjustment_when_selling_is_required(
        self,
    ) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=550000.0,
            portfolio_value=1000000.0,
            target_weight=0.40,
        )

        assert rebalancing.adjustment == -150000.0

    def test_returns_zero_adjustment_when_already_at_target(
        self,
    ) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=400000.0,
            portfolio_value=1000000.0,
            target_weight=0.40,
        )

        assert rebalancing.adjustment == 0.0

    def test_rejects_zero_portfolio_value(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=100000.0,
            portfolio_value=0.0,
            target_weight=0.20,
        )

        with pytest.raises(
            ValueError,
            match="portfolio_value must be greater than zero",
        ):
            _ = rebalancing.current_weight

    def test_rejects_negative_portfolio_value(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=100000.0,
            portfolio_value=-1000000.0,
            target_weight=0.20,
        )

        with pytest.raises(
            ValueError,
            match="portfolio_value must be greater than zero",
        ):
            _ = rebalancing.target_value

    def test_rejects_negative_target_weight(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=100000.0,
            portfolio_value=1000000.0,
            target_weight=-0.10,
        )

        with pytest.raises(
            ValueError,
            match="target_weight must be between 0 and 1",
        ):
            _ = rebalancing.target_value

    def test_rejects_target_weight_above_one(self) -> None:
        rebalancing = Rebalancing(
            symbol="NIFTY",
            current_value=100000.0,
            portfolio_value=1000000.0,
            target_weight=1.10,
        )

        with pytest.raises(
            ValueError,
            match="target_weight must be between 0 and 1",
        ):
            _ = rebalancing.target_value