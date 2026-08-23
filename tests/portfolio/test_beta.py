import pytest

from private_quant_terminal.portfolio.beta import (
    beta,
    covariance,
    variance,
)


class TestCovariance:
    def test_returns_zero_for_empty_series(
        self,
    ) -> None:
        assert covariance((), ()) == 0.0

    def test_raises_for_mismatched_lengths(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Return series must have the same length.",
        ):
            covariance(
                (0.01, 0.02),
                (0.01,),
            )

    def test_calculates_positive_covariance(
        self,
    ) -> None:
        result = covariance(
            (1.0, 2.0, 3.0),
            (2.0, 4.0, 6.0),
        )

        assert result == pytest.approx(
            4.0 / 3.0,
        )

    def test_calculates_negative_covariance(
        self,
    ) -> None:
        result = covariance(
            (1.0, 2.0, 3.0),
            (3.0, 2.0, 1.0),
        )

        assert result == pytest.approx(
            -2.0 / 3.0,
        )


class TestVariance:
    def test_returns_zero_for_empty_series(
        self,
    ) -> None:
        assert variance(()) == 0.0

    def test_returns_zero_for_constant_series(
        self,
    ) -> None:
        assert variance(
            (2.0, 2.0, 2.0),
        ) == 0.0

    def test_calculates_population_variance(
        self,
    ) -> None:
        result = variance(
            (1.0, 2.0, 3.0),
        )

        assert result == pytest.approx(
            2.0 / 3.0,
        )


class TestBeta:
    def test_calculates_beta_of_one(
        self,
    ) -> None:
        result = beta(
            (0.01, 0.02, 0.03),
            (0.01, 0.02, 0.03),
        )

        assert result == pytest.approx(1.0)

    def test_calculates_beta_greater_than_one(
        self,
    ) -> None:
        result = beta(
            (0.02, 0.04, 0.06),
            (0.01, 0.02, 0.03),
        )

        assert result == pytest.approx(2.0)

    def test_calculates_negative_beta(
        self,
    ) -> None:
        result = beta(
            (-0.01, -0.02, -0.03),
            (0.01, 0.02, 0.03),
        )

        assert result == pytest.approx(-1.0)

    def test_raises_for_zero_benchmark_variance(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match=(
                "Benchmark returns must have non-zero variance."
            ),
        ):
            beta(
                (0.01, 0.02, 0.03),
                (0.01, 0.01, 0.01),
            )