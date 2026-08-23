import pytest

from private_quant_terminal.portfolio.alpha import (
    alpha,
    expected_return,
)


class TestExpectedReturn:
    def test_calculates_expected_return_with_zero_risk_free_rate(
        self,
    ) -> None:
        result = expected_return(
            benchmark_return=0.10,
            beta_value=1.0,
        )

        assert result == pytest.approx(0.10)

    def test_calculates_expected_return_with_beta_greater_than_one(
        self,
    ) -> None:
        result = expected_return(
            benchmark_return=0.10,
            beta_value=1.5,
        )

        assert result == pytest.approx(0.15)

    def test_calculates_expected_return_with_risk_free_rate(
        self,
    ) -> None:
        result = expected_return(
            benchmark_return=0.10,
            beta_value=1.2,
            risk_free_rate=0.04,
        )

        assert result == pytest.approx(0.112)

    def test_calculates_expected_return_with_negative_beta(
        self,
    ) -> None:
        result = expected_return(
            benchmark_return=0.10,
            beta_value=-1.0,
            risk_free_rate=0.02,
        )

        assert result == pytest.approx(-0.06)


class TestAlpha:
    def test_returns_zero_when_portfolio_matches_expected_return(
        self,
    ) -> None:
        result = alpha(
            portfolio_return=0.10,
            benchmark_return=0.10,
            beta_value=1.0,
        )

        assert result == pytest.approx(0.0)

    def test_calculates_positive_alpha(
        self,
    ) -> None:
        result = alpha(
            portfolio_return=0.15,
            benchmark_return=0.10,
            beta_value=1.0,
        )

        assert result == pytest.approx(0.05)

    def test_calculates_negative_alpha(
        self,
    ) -> None:
        result = alpha(
            portfolio_return=0.05,
            benchmark_return=0.10,
            beta_value=1.0,
        )

        assert result == pytest.approx(-0.05)

    def test_calculates_alpha_with_risk_free_rate(
        self,
    ) -> None:
        result = alpha(
            portfolio_return=0.14,
            benchmark_return=0.10,
            beta_value=1.2,
            risk_free_rate=0.04,
        )

        # Expected return = 0.04 + 1.2 * (0.10 - 0.04) = 0.112
        # Alpha = 0.14 - 0.112 = 0.028
        assert result == pytest.approx(0.028)

    def test_calculates_alpha_with_negative_beta(
        self,
    ) -> None:
        result = alpha(
            portfolio_return=0.00,
            benchmark_return=0.10,
            beta_value=-1.0,
            risk_free_rate=0.02,
        )

        # Expected return = 0.02 - (0.10 - 0.02) = -0.06
        # Alpha = 0.00 - (-0.06) = 0.06
        assert result == pytest.approx(0.06)