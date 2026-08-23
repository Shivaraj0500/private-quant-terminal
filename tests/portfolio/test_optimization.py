import pytest

from private_quant_terminal.portfolio.optimization import (
    equal_weights,
    inverse_volatility_weights,
    normalize_weights,
    portfolio_expected_return,
    portfolio_variance,
    portfolio_volatility,
)


class TestOptimization:
    def test_normalizes_weights(self) -> None:
        result = normalize_weights(
            (2.0, 3.0, 5.0)
        )

        assert result == pytest.approx(
            (0.2, 0.3, 0.5)
        )

    def test_rejects_empty_weights_for_normalization(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one weight is required",
        ):
            normalize_weights(())

    def test_rejects_zero_total_weight(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Weights must not sum to zero",
        ):
            normalize_weights((1.0, -1.0))

    def test_creates_equal_weights(self) -> None:
        result = equal_weights(4)

        assert result == pytest.approx(
            (0.25, 0.25, 0.25, 0.25)
        )

    def test_rejects_invalid_asset_count(self) -> None:
        with pytest.raises(
            ValueError,
            match="Asset count must be greater than zero",
        ):
            equal_weights(0)

    def test_creates_inverse_volatility_weights(
        self,
    ) -> None:
        result = inverse_volatility_weights(
            (0.10, 0.20, 0.40)
        )

        assert result == pytest.approx(
            (0.5714285714, 0.2857142857, 0.1428571429)
        )

    def test_rejects_empty_volatilities(self) -> None:
        with pytest.raises(
            ValueError,
            match="At least one volatility is required",
        ):
            inverse_volatility_weights(())

    def test_rejects_non_positive_volatility(self) -> None:
        with pytest.raises(
            ValueError,
            match="Volatilities must be greater than zero",
        ):
            inverse_volatility_weights(
                (0.10, 0.0, 0.20)
            )

    def test_calculates_portfolio_expected_return(
        self,
    ) -> None:
        result = portfolio_expected_return(
            weights=(0.60, 0.40),
            expected_returns=(0.10, 0.20),
        )

        assert result == pytest.approx(0.14)

    def test_rejects_empty_expected_return_inputs(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one value is required in each sequence",
        ):
            portfolio_expected_return(
                weights=(),
                expected_returns=(),
            )

    def test_rejects_mismatched_expected_return_inputs(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "Weights and expected returns "
                "must have the same length"
            ),
        ):
            portfolio_expected_return(
                weights=(0.50, 0.50),
                expected_returns=(0.10,),
            )

    def test_calculates_portfolio_variance(
        self,
    ) -> None:
        result = portfolio_variance(
            weights=(0.50, 0.50),
            covariance_matrix=(
                (0.04, 0.01),
                (0.01, 0.09),
            ),
        )

        assert result == pytest.approx(0.0375)

    def test_rejects_empty_weights_for_variance(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one weight is required",
        ):
            portfolio_variance(
                weights=(),
                covariance_matrix=(),
            )

    def test_rejects_covariance_matrix_size_mismatch(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Covariance matrix size must match weight count",
        ):
            portfolio_variance(
                weights=(0.50, 0.50),
                covariance_matrix=(
                    (0.04, 0.01),
                ),
            )

    def test_rejects_non_square_covariance_matrix(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Covariance matrix must be square",
        ):
            portfolio_variance(
                weights=(0.50, 0.50),
                covariance_matrix=(
                    (0.04, 0.01, 0.02),
                    (0.01, 0.09, 0.03),
                ),
            )

    def test_calculates_portfolio_volatility(
        self,
    ) -> None:
        result = portfolio_volatility(
            weights=(0.50, 0.50),
            covariance_matrix=(
                (0.04, 0.01),
                (0.01, 0.09),
            ),
        )

        assert result == pytest.approx(
            0.1936491673
        )

    def test_rejects_negative_portfolio_variance(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Portfolio variance must not be negative",
        ):
            portfolio_volatility(
                weights=(1.0,),
                covariance_matrix=((-0.01,),),
            )