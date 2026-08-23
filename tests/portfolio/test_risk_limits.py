import pytest

from private_quant_terminal.portfolio.risk_limits import (
    PortfolioRiskLimits,
)


class TestPortfolioRiskLimits:
    def test_creates_portfolio_risk_limits(self) -> None:
        limits = PortfolioRiskLimits(
            max_gross_exposure=1_000_000.0,
            max_net_exposure=500_000.0,
            max_long_exposure=750_000.0,
            max_short_exposure=500_000.0,
            max_largest_position_weight=0.50,
        )

        assert limits.max_gross_exposure == 1_000_000.0
        assert limits.max_net_exposure == 500_000.0
        assert limits.max_long_exposure == 750_000.0
        assert limits.max_short_exposure == 500_000.0
        assert limits.max_largest_position_weight == 0.50

    @pytest.mark.parametrize(
        ("field_name", "value"),
        [
            ("max_gross_exposure", -1.0),
            ("max_net_exposure", -1.0),
            ("max_long_exposure", -1.0),
            ("max_short_exposure", -1.0),
        ],
    )
    def test_rejects_negative_exposure_limit(
        self,
        field_name: str,
        value: float,
    ) -> None:
        values = {
            "max_gross_exposure": 1000.0,
            "max_net_exposure": 1000.0,
            "max_long_exposure": 1000.0,
            "max_short_exposure": 1000.0,
            "max_largest_position_weight": 0.50,
        }

        values[field_name] = value

        with pytest.raises(
            ValueError,
            match=(
                f"{field_name} must be greater than or equal to zero"
            ),
        ):
            PortfolioRiskLimits(**values)

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
            match=(
                "max_largest_position_weight must be "
                "between zero and one"
            ),
        ):
            PortfolioRiskLimits(
                max_gross_exposure=1000.0,
                max_net_exposure=1000.0,
                max_long_exposure=1000.0,
                max_short_exposure=1000.0,
                max_largest_position_weight=weight,
            )

    def test_allows_zero_exposure_limits(self) -> None:
        limits = PortfolioRiskLimits(
            max_gross_exposure=0.0,
            max_net_exposure=0.0,
            max_long_exposure=0.0,
            max_short_exposure=0.0,
            max_largest_position_weight=0.0,
        )

        assert limits.max_gross_exposure == 0.0
        assert limits.max_net_exposure == 0.0
        assert limits.max_long_exposure == 0.0
        assert limits.max_short_exposure == 0.0
        assert limits.max_largest_position_weight == 0.0

    def test_portfolio_risk_limits_is_immutable(self) -> None:
        limits = PortfolioRiskLimits(
            max_gross_exposure=1000.0,
            max_net_exposure=1000.0,
            max_long_exposure=1000.0,
            max_short_exposure=1000.0,
            max_largest_position_weight=0.50,
        )

        with pytest.raises(AttributeError):
            limits.max_gross_exposure = 2000.0
