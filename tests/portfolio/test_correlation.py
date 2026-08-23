from math import isclose

import pytest

from private_quant_terminal.portfolio.correlation import (
    calculate_correlation,
)


class TestCalculateCorrelation:
    def test_calculates_perfect_positive_correlation(
        self,
    ) -> None:
        result = calculate_correlation(
            (1.0, 2.0, 3.0),
            (2.0, 4.0, 6.0),
        )

        assert result == 1.0

    def test_calculates_perfect_negative_correlation(
        self,
    ) -> None:
        result = calculate_correlation(
            (1.0, 2.0, 3.0),
            (6.0, 4.0, 2.0),
        )

        assert result == -1.0

    def test_calculates_zero_correlation(
        self,
    ) -> None:
        result = calculate_correlation(
            (-1.0, 0.0, 1.0),
            (1.0, -2.0, 1.0),
        )

        assert isclose(
            result,
            0.0,
            abs_tol=1e-12,
        )

    def test_returns_zero_for_empty_series(
        self,
    ) -> None:
        assert calculate_correlation((), ()) == 0.0

    def test_returns_zero_for_single_value_series(
        self,
    ) -> None:
        assert calculate_correlation(
            (1.0,),
            (2.0,),
        ) == 0.0

    def test_returns_zero_when_first_series_has_zero_variance(
        self,
    ) -> None:
        assert calculate_correlation(
            (1.0, 1.0, 1.0),
            (1.0, 2.0, 3.0),
        ) == 0.0

    def test_returns_zero_when_second_series_has_zero_variance(
        self,
    ) -> None:
        assert calculate_correlation(
            (1.0, 2.0, 3.0),
            (5.0, 5.0, 5.0),
        ) == 0.0

    def test_raises_error_for_different_series_lengths(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="Return series must have the same length.",
        ):
            calculate_correlation(
                (1.0, 2.0),
                (1.0,),
            )