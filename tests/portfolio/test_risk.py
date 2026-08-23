import pytest

from private_quant_terminal.portfolio.risk import PortfolioRisk


class TestPortfolioRisk:
    def test_creates_portfolio_risk(self) -> None:
        risk = PortfolioRisk(
            gross_exposure=150000.0,
            net_exposure=50000.0,
            long_exposure=100000.0,
            short_exposure=50000.0,
            largest_position_weight=0.60,
            position_count=3,
        )

        assert risk.gross_exposure == 150000.0
        assert risk.net_exposure == 50000.0
        assert risk.long_exposure == 100000.0
        assert risk.short_exposure == 50000.0
        assert risk.largest_position_weight == 0.60
        assert risk.position_count == 3

    def test_allows_negative_net_exposure(self) -> None:
        risk = PortfolioRisk(
            gross_exposure=100000.0,
            net_exposure=-40000.0,
            long_exposure=30000.0,
            short_exposure=70000.0,
            largest_position_weight=0.70,
            position_count=2,
        )

        assert risk.net_exposure == -40000.0

    def test_rejects_negative_gross_exposure(self) -> None:
        with pytest.raises(
            ValueError,
            match="gross_exposure must be greater than or equal to zero",
        ):
            PortfolioRisk(
                gross_exposure=-1.0,
                net_exposure=0.0,
                long_exposure=0.0,
                short_exposure=0.0,
                largest_position_weight=0.0,
                position_count=0,
            )

    def test_rejects_negative_long_exposure(self) -> None:
        with pytest.raises(
            ValueError,
            match="long_exposure must be greater than or equal to zero",
        ):
            PortfolioRisk(
                gross_exposure=0.0,
                net_exposure=0.0,
                long_exposure=-1.0,
                short_exposure=0.0,
                largest_position_weight=0.0,
                position_count=0,
            )

    def test_rejects_negative_short_exposure(self) -> None:
        with pytest.raises(
            ValueError,
            match="short_exposure must be greater than or equal to zero",
        ):
            PortfolioRisk(
                gross_exposure=0.0,
                net_exposure=0.0,
                long_exposure=0.0,
                short_exposure=-1.0,
                largest_position_weight=0.0,
                position_count=0,
            )

    @pytest.mark.parametrize(
        "weight",
        [-0.01, 1.01],
    )
    def test_rejects_invalid_largest_position_weight(
        self,
        weight: float,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="largest_position_weight must be between zero and one",
        ):
            PortfolioRisk(
                gross_exposure=100.0,
                net_exposure=100.0,
                long_exposure=100.0,
                short_exposure=0.0,
                largest_position_weight=weight,
                position_count=1,
            )

    def test_rejects_negative_position_count(self) -> None:
        with pytest.raises(
            ValueError,
            match="position_count must be greater than or equal to zero",
        ):
            PortfolioRisk(
                gross_exposure=0.0,
                net_exposure=0.0,
                long_exposure=0.0,
                short_exposure=0.0,
                largest_position_weight=0.0,
                position_count=-1,
            )

    def test_portfolio_risk_is_immutable(self) -> None:
        risk = PortfolioRisk(
            gross_exposure=100000.0,
            net_exposure=50000.0,
            long_exposure=75000.0,
            short_exposure=25000.0,
            largest_position_weight=0.75,
            position_count=2,
        )

        with pytest.raises(AttributeError):
            risk.gross_exposure = 200000.0
